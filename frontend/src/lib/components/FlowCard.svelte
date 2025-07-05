<script lang="ts">
	import type { Flow, Tags } from "$lib/schema";
	import TagBadge from "./TagBadge.svelte";

    let { flow, tags }: { flow: Flow, tags: Tags } = $props();
    let time = new Date(Number(flow.ts_start)).toISOString().split("T")[1].slice(0, -1);
    let delay = (flow.ts_end - flow.ts_start) / 1000;
    let flowTags = flow.tags.split(",");
    let appProto = flow.app_proto ? flow.app_proto.replace("failed", "raw") : "raw";
</script>

<button class="list-group-item list-group-item-action py-1 px-2" type="button">
    <div class="d-flex justify-content-between mb-1">
        <small><span class="badge" style="background-color: #1a5fb4">CCMarket</span> (:{flow.dest_ipport.split(":")[1]})</small>
        <small>{delay.toPrecision(3)} { delay > 1000 ? "s" : "ms" }, { time }</small>
    </div>
    <TagBadge text={appProto.toUpperCase()} />
    {#each tags as t}
        {#if flowTags.includes(t.tag)}
            {@const tagId = "tag_" + t.tag.replace(/[^A-Za-z0-9]/g, "_")}
            <TagBadge text={t.tag} color={t.color} count={flow.metadata ? flow.metadata.flowints[tagId] : undefined} />
        {/if}
    {/each}
</button>