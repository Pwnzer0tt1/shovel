<script lang="ts">
	import FlowDisplay from '$lib/components/FlowDisplay.svelte';
	import SideBar from '$lib/components/SideBar.svelte';
	import TickProgressBar from '$lib/components/TickProgressBar.svelte';
	import WelcomePanel from '$lib/components/WelcomePanel.svelte';
	import type { Flows, Tags } from '$lib/schema';
	import { selectedFlow } from '$lib/state.svelte.js';
	import { onMount } from 'svelte';

    let { data } = $props();


    let innerHeight = $state(0);
    let tickProgressBarHeight = $state(0);
    let panelsHeight = $derived(innerHeight - tickProgressBarHeight);


    let flows: Flows = $state([]);
    let tags: Tags = $state([]);
    let appProto: string[] = $state([]);

    let flowsListInterval;

    async function getFlowsList() {
        let res = await fetch("/api/flow");
        let json = await res.json();
        console.log(json);

        flows = json.flows;
        tags = json.tags;
    }

    function flowsSelection(e: KeyboardEvent) {
        if (e.target) {
            if (e.target.tagName !== "INPUT" && !e.ctrlKey && !e.altKey && !e.shiftKey) {
                switch (e.code) {
                    case "ArrowLeft":
                        if (selectedFlow.flow) {
                            if (selectedFlow.flowIndex > 0) {
                                selectedFlow.flow = flows.at(selectedFlow.flowIndex - 1);
                                selectedFlow.flowIndex -= 1;
                            }
                        }
                        else {
                            selectedFlow.flow = flows.at(0);
                            selectedFlow.flowIndex = 0;
                        }
                        break;
                    case "ArrowRight":
                        if (selectedFlow.flow) {
                            if (selectedFlow.flowIndex < flows.length - 1) {
                                selectedFlow.flow = flows.at(selectedFlow.flowIndex + 1);
                                selectedFlow.flowIndex += 1;
                            }
                        }
                        else {
                            selectedFlow.flow = flows.at(0);
                            selectedFlow.flowIndex = 0;
                        }
                        break;
                    case "Escape":
                        selectedFlow.flow = undefined;
                        break;
                }
            }
        }
    }

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
            <SideBar ctfConfig={data.ctfConfig} flows={flows} tags={tags} tickProgressBarHeight={tickProgressBarHeight} />
        </div>
        <div class="col-9 h-100 overflow-y-scroll pe-2">
            {#if selectedFlow.flow}
                <!-- Flow display -->
                <FlowDisplay ctfConfig={data.ctfConfig} />
            {:else}
                <!-- Welcome section, shown only when no flows are selected -->
                <WelcomePanel />
            {/if}
        </div>
    </div>
    <div class="fixed-bottom p-2" bind:clientHeight={tickProgressBarHeight}>
        <!-- Progress bar per tick -->
        <TickProgressBar startTs={Math.floor(Date.parse(data.ctfConfig.start_date) / 1000)} tickLength={data.ctfConfig.tick_length} />
    </div>
</div>


<!-- Modal to manage services -->
<div class="modal fade" id="servicesModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content" style="max-height: 90vh;">
            <div class="modal-header">
                <h5 class="modal-title">Service Manager</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" style="max-height: calc(90vh - 120px); overflow-y: auto;">
                <div class="row mb-4">
                    <div class="col-md-8">
                        <label class="form-label" for="serviceName">Service Name</label>
                        <input type="text" class="form-control" id="serviceName" placeholder="es. web">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label" for="serviceColor">Color</label>
                        <input type="color" class="form-control form-control-color w-100" id="serviceColor" title="Choose service color">
                    </div>
                </div>
                <div class="row mb-4">
                    <div class="col-md-8">
                        <label class="form-label">
                            Target IP <span class="form-text">(auto-extracted from PCAP: { data.ctfConfig.default_ip })</span>
                        </label>
                        <div class="input-group">
                            <input type="text" class="form-control" id="serviceIP" value={ data.ctfConfig.default_ip } readonly>
                            <button class="btn btn-success" type="button" id="editServiceIPBtn" title="Edit IP" aria-label="Edit service IP">
                                <i class="bi bi-pencil-fill"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Port</label>
                        <input class="form-control" type="text" id="servicePorts" placeholder="(e.g., 80, 443, 8080)">
                    </div>
                </div>
                <button class="btn btn-primary w-100 mb-0" id="addServiceBtn">Add Service</button>

                <!-- Divisore e sezione settings -->
                <hr class="my-4">
                <div class="mb-3">
                    <h6 class="text-muted mb-3">
                        <i class="bi bi-gear-fill me-2"></i>
                        Application Settings
                    </h6>
                    <label for="refreshRateInput" class="form-label">Flow list Auto-Refresh rate
                        <span class="form-text">(seconds)</span>
                    </label>
                    <div class="input-group">
                        <input type="number" class="form-control" id="refreshRateInput" min="1" value={ data.ctfConfig.refresh_rate }>
                        <button type="button" class="btn btn-success" id="saveRefreshRateBtn">Save</button>
                    </div>
                </div>

                <!-- Sezione servizi configurati con scroll separato -->
                <hr class="my-4">
                <div class="configured-services-section">
                    <h6 class="text-muted mb-3">
                        <i class="bi bi-list-ul me-2"></i>
                        Configured Services
                    </h6>
                    <div id="servicesList" class="services-list-container" style="max-height: 300px; overflow-y: auto; padding-right: 5px;">
                        <!-- I servizi verranno inseriti qui -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal to confirm deletion of a service -->
<div class="modal fade" id="deleteConfirmModal" tabindex="-1" aria-labelledby="deleteConfirmModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title" id="deleteConfirmModalLabel">Delete confirmation</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                Are you sure you want to delete the service <strong id="serviceNameToDelete"></strong>?
                <p class="text-muted mt-2 mb-0 small">This action cannot be undone.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-danger" id="confirmDeleteBtn">Delete</button>
            </div>
        </div>
    </div>
</div>