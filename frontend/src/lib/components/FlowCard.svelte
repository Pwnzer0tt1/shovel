<script lang="ts">
	import type { Flow, Tags } from "$lib/schema";
	import { ctfConfig, selectedFlow } from "$lib/state.svelte";
	import TagBadge from "./TagBadge.svelte";

    let { index, flow, tags }: { index: number, flow: Flow, tags: Tags } = $props();
    
    const delay = (Number(flow.ts_end) - Number(flow.ts_start)) / 1000;
    const time = new Date(Number(flow.ts_start) / 1000).toISOString().split("T")[1];
    
    const flowTags = (flow.alerts ?? []).map((v) => v.tag);
    const appProto = flow.app_proto ? flow.app_proto.replace("failed", "raw") : "raw";

    let btn: HTMLButtonElement;

    let {serviceColor, serviceName} = $derived.by(() => {
        for (const [name, service] of Object.entries(ctfConfig.config.services)) {
            if (service.ipports.map(v => `${v.ip}:${v.port}`).includes(flow.dest_ipport)) {
                return {serviceColor: service.color, serviceName: name};
            }
        }

        return {serviceColor: "#6c757d", serviceName: "Unknown"};
    });

    function selectFlow() {
        selectedFlow.flow = flow;
        selectedFlow.flowIndex = index;

        btn.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" });
    }

    $effect(() => {
        if (selectedFlow.flow) {
            if (selectedFlow.flow.id === flow.id) {
                btn.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" });
            }
        }
    });
</script>

<button bind:this={btn} onclick={selectFlow} class="list-group-item list-group-item-action py-1 px-2 {selectedFlow.flow ? (selectedFlow.flow.id === flow.id ? "active" : "") : ""}" type="button">
    <div class="d-flex justify-content-between mb-1">
        <small><span class="badge" style="background-color: {serviceColor}">{serviceName}</span> (:{flow.dest_port})</small>
        <small>{delay.toPrecision(3)} { delay > 1000 ? "s" : "ms" }, { time }</small>
    </div>
    <TagBadge text={appProto.toUpperCase()} />
    {#each tags as t}
        {#if flowTags.includes(t.tag)}
            {@const tagId = "tag_" + t.tag.replace(/[^A-Za-z0-9]/g, "_")}
            <TagBadge text={t.tag} color={t.color} count={flow.metadata ? (flow.metadata.flowints ? flow.metadata.flowints[tagId] : undefined) : undefined} />
        {/if}
    {/each}
</button>