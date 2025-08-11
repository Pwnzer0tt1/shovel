<script lang="ts">
	import FlowDisplay from '$lib/components/FlowDisplay.svelte';
	import ServicesManager from '$lib/components/ServicesManager.svelte';
	import Settings from '$lib/components/Settings.svelte';
	import SideBar from '$lib/components/SideBar.svelte';
	import Stats from '$lib/components/Stats.svelte';
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

    let flowsListInterval: string | number | NodeJS.Timeout | undefined;


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
                        ctfConfig.hideSideBar = false;
                        break;
                }
            }
        }
    }

    // Fetch new flows when filters are changed
    $effect(() => {
        if (flowsFilters) {
            selectedFlow.flow = undefined;
            selectedFlow.flowIndex = -1;
            getFlowsList();
        }
    });

    // Reset interval for flows fetching on refresh rate updates
    $effect(() => {
        clearInterval(flowsListInterval);
        flowsListInterval = setInterval(async () => {
            if (ctfConfig.autoUpdate) {
                getFlowsList();
            }
        }, ctfConfig.config.refresh_rate * 1000);
    });

    onMount(() => {
        getFlowsList();
    });
</script>

<svelte:window bind:innerHeight />

<svelte:document onkeydown={flowsSelection} />

<div class="vstack vh-100 p-2">
    <div class="hstack gap-2 pb-2" style="height: {panelsHeight}px;">
        {#if !ctfConfig.hideSideBar}
            <div class="pb-3 h-100">
                <!-- Side bar -->
                <SideBar tags={tags} appProto={appProto} />
            </div>
        {/if}
        <div class="col-{ctfConfig.hideSideBar ? "12" : "9"} h-100 overflow-y-auto">
            {#if selectedPanel.view === "ServicesManager"}
                <!-- Manage services -->
                <ServicesManager />
            {:else if selectedPanel.view === "Settings"}
                <Settings />
            {:else if selectedPanel.view === "Stats"}
                <Stats />
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
    <div class="fixed-bottom p-2 hstack gap-2" bind:clientHeight={tickProgressBarHeight}>
        <!-- Progress bar per tick -->
        <TickProgressBar />
        {#if ctfConfig.ctfEnded}
            <button class="col-2 btn btn-outline-danger">CTF ENDED</button>
        {/if}
        <div class="btn-group" role="group" aria-label="Basic example">
            <button onclick={() => selectedPanel.view = "Settings"} type="button" class="btn btn-primary" title="Settings" aria-label="Settings"><i class="bi bi-gear-fill"></i></button>
            <button onclick={() => selectedPanel.view = "Stats"} type="button" class="btn btn-primary" title="Statistics" aria-label="Statistics"><i class="bi bi-activity"></i></button>
        </div>
    </div>
</div>