<script lang="ts">
	import FlowDisplay from '$lib/components/FlowDisplay.svelte';
	import ServicesManager from '$lib/components/ServicesManager.svelte';
	import SideBar from '$lib/components/SideBar.svelte';
	import TickProgressBar from '$lib/components/TickProgressBar.svelte';
	import WelcomePanel from '$lib/components/WelcomePanel.svelte';
	import type { Tags } from '$lib/schema';
	import { ctfConfig, flows, flowsFilters, selectedFlow, selectedPanel } from '$lib/state.svelte.js';
	import { onMount } from 'svelte';

    let { data } = $props();
    ctfConfig.config = data.ctfConfig;


    let innerHeight = $state(0);
    let tickProgressBarHeight = $state(0);
    let panelsHeight = $derived(innerHeight - tickProgressBarHeight);

    let tags: Tags = $state([]);
    let appProto: string[] = $state([]);

    let flowsListInterval;


    async function getFlowsList() {
        let res = await fetch(`/api/flow?filters=${JSON.stringify(flowsFilters)}`);
        let json = await res.json();

        flows.flows = json.flows;
        tags = json.tags;
        appProto = json.appProto;
    }

    function flowsSelection(e: KeyboardEvent) {
        if (e.target) {
            let el = e.target as HTMLElement;
            if (el.tagName !== "INPUT" && !e.ctrlKey && !e.altKey && !e.shiftKey) {
                switch (e.code) {
                    case "ArrowLeft":
                        if (selectedFlow.flow) {
                            if (selectedFlow.flowIndex > 0) {
                                selectedFlow.flow = flows.flows.at(selectedFlow.flowIndex - 1);
                                selectedFlow.flowIndex -= 1;
                            }
                        }
                        else {
                            selectedFlow.flow = flows.flows.at(0);
                            selectedFlow.flowIndex = 0;
                        }
                        break;
                    case "ArrowRight":
                        if (selectedFlow.flow) {
                            if (selectedFlow.flowIndex < flows.flows.length - 1) {
                                selectedFlow.flow = flows.flows.at(selectedFlow.flowIndex + 1);
                                selectedFlow.flowIndex += 1;
                            }
                        }
                        else {
                            selectedFlow.flow = flows.flows.at(0);
                            selectedFlow.flowIndex = 0;
                        }
                        break;
                    case "Escape":
                        if (selectedPanel.view) {
                            selectedPanel.view = undefined;
                        }
                        else {
                            selectedFlow.flow = undefined;
                        }
                        break;
                }
            }
        }
    }

    $effect(() => {
        if (flowsFilters) {
            selectedFlow.flow = undefined;
            selectedFlow.flowIndex = -1;
            getFlowsList();
        }
    });

    onMount(() => {
        getFlowsList();

        flowsListInterval = setInterval(async () => {
            getFlowsList();
        }, data.ctfConfig.refresh_rate * 1000);
    });
</script>

<svelte:window bind:innerHeight />

<svelte:document onkeydown={flowsSelection} />

<div class="vstack vh-100 p-2">
    <div class="hstack gap-2 pb-2" style="height: {panelsHeight}px;">
        <div class="pb-3 h-100">
            <!-- Side bar -->
            <SideBar tags={tags} appProto={appProto} />
        </div>
        <div class="col-9 h-100 overflow-y-auto pe-2">
            {#if selectedPanel.view === "ServicesManager"}
                <!-- Manage services -->
                <ServicesManager />
            {:else}
                {#if selectedFlow.flow}
                    <!-- Flow display -->
                    <FlowDisplay />
                {:else}
                    <!-- Welcome section, shown only when no flows are selected -->
                    <WelcomePanel />
                {/if}
            {/if}
        </div>
    </div>
    <div class="fixed-bottom p-2" bind:clientHeight={tickProgressBarHeight}>
        <!-- Progress bar per tick -->
        <TickProgressBar startTs={Math.floor(Date.parse(data.ctfConfig.start_date) / 1000)} tickLength={data.ctfConfig.tick_length} />
    </div>
</div>