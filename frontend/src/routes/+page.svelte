<script lang="ts">
	import FlowCard from '$lib/components/FlowCard.svelte';
	import SideBar from '$lib/components/SideBar.svelte';
	import TickProgressBar from '$lib/components/TickProgressBar.svelte';
	import type { Flows, Tags } from '$lib/schema';
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

    onMount(() => {
        getFlowsList();

        flowsListInterval = setInterval(async () => {
            getFlowsList();
        }, data.ctfConfig.refresh_rate * 1000);
    });
</script>

<svelte:window bind:innerHeight />

<div class="vstack m-2">
    <div class="hstack gap-2" style="height: {panelsHeight}px;">
        <div class="h-100">
            <!-- Side bar -->
            <SideBar ctfConfig={data.ctfConfig} flows={flows} tags={tags} tickProgressBarHeight={tickProgressBarHeight} />
        </div>
        <div class="container-fluid card bg-body-secondary" style="height: {panelsHeight}px;">
            <!-- Welcome section, shown only when no flows are selected -->
            <div class="my-auto text-center p-2">
                <img src="/favicon.svg" alt="" width="80">
                <p class="fs-1 fw-light">Shovel</p>
                <ul class="list-unstyled">
                    <li class="mb-1">Use <kbd>Left</kbd>, <kbd>Right</kbd> keys to quickly navigate flows.</li>
                    <li class="mb-1">Use <kbd>Ctrl+Maj+F</kbd> key to search current selection.</li>
                    <li class="mb-1">Use <kbd>V</kbd> key to quickly switch raw data view.</li>
                    <li class="mb-1">Use <kbd>T</kbd> key to switch color theme.</li>
                    <li class="mb-1">Use <kbd>Esc</kbd> key to de-select the current flow.</li>
                </ul>
                <p class="text-body-secondary small">
                    <a href="https://github.com/ANSSI-FR/shovel">Get the source code</a>, licensed under GPL-2.0.
                </p>
                <p>This version is a fork made by <a href="https://github.com/pwnzer0tt1/shovel" class="fw-bold">Pwnzer0tt1</a>.</p>
            </div>

            <!-- Flow display -->
            <!--<div>
                <div class="row m-0 d-none" id="display-flow">
                    <div class="col-12 col-lg-auto p-0">
                        <section class="card m-3 mb-0 bg-body shadow font-monospace border-secondary">
                            <div class="card-body">
                                <pre class="mb-0 d-none" id="display-flow-tick">
                                    <a href="#" class="text-decoration-none" title="Apply as filter">Tick <span></span></a>
                                </pre>
                                <pre class="mb-0" id="display-flow-time"></pre>
                            </div>
                        </section>
                    </div>
                    <div class="col p-0">
                        <section class="card m-3 mb-0 bg-body shadow font-monospace border-secondary">
                            <pre class="card-body mb-0" id="display-flow-pkt"></pre>
                        </section>
                    </div>
                    <div class="col-auto p-0">
                        <a class="btn btn-success shadow m-3 ms-0" href="#" download id="display-flow-pcap" title="Download pcap" aria-label="Download pcap">
                            <i class="bi bi-download"></i>
                        </a>
                    </div>
                </div>
                <div id="display-alerts"></div>
                <div class="text-center m-3 d-none" id="display-down">
                    <svg width="30mm" height="30mm" viewBox="0 0 65.652 70.495" fill="currentColor">
                        <g transform="translate(-83.965 -103.17)">
                            <path d="m92.172 103.17c-4.5323 0-8.2062 3.6739-8.2062 8.2062v4.1031c6e-5 4.5323 3.6739 8.2067 8.2062 8.2067h22.568v6.0575h4.1031v-6.0575h22.568c4.5323 0 8.2062-3.6745 8.2062-8.2067v-4.1031c-6e-5 -4.5323-3.6739-8.2062-8.2062-8.2062zm0 4.1031h49.239c2.2661 0 4.1031 1.837 4.1031 4.1031v4.1031c-3e-5 2.2661-1.837 4.1036-4.1031 4.1036h-49.239c-2.2661 0-4.1031-1.8375-4.1031-4.1036v-4.1031c2.7e-5 -2.2661 1.837-4.1031 4.1031-4.1031zm10.258 4.1031c-2.7324 3e-3 -2.7324 4.1004 0 4.1036 2.7388 3e-3 2.7388-4.1068 0-4.1036zm-8.2057 1e-3c-1.0258 0-2.0518 0.68351-2.0526 2.0505 0.0015 2.737 4.1046 2.737 4.1031 0 7.39e-4 -1.367-1.0247-2.0505-2.0505-2.0505zm31.649 17.188c-0.45372 0.0199-0.92202 0.20945-1.3451 0.62839l-7.737 7.737-7.737-7.737c-0.42312-0.41893-0.89144-0.60792-1.3451-0.62787-1.6204-0.0713-3.0527 2.0184-1.5565 3.5295l7.737 7.737-7.737 7.737c-1.9151 1.9342 0.9674 4.8168 2.9016 2.9016l7.737-7.737 7.737 7.737c1.9342 1.9152 4.8168-0.96739 2.9016-2.9016l-7.737-7.737 7.737-7.737c1.4962-1.5111 0.0639-3.6012-1.5565-3.53zm-11.134 21.253v7.4336c-3.3993 0-6.1552 2.7554-6.1552 6.1547h-22.568c-2.7219 0.0135-2.7219 4.0896 0 4.1031h22.568c-4e-5 3.3993 2.7559 6.1552 6.1552 6.1552h4.1031c3.3993 0 6.1552-2.7559 6.1552-6.1552h22.568c2.7219-0.0135 2.7219-4.0896 0-4.1031h-22.568c4e-5 -3.3993-2.7559-6.1547-6.1552-6.1547v-7.4336zm0 11.537h4.1031c1.1331 0 2.0515 0.91849 2.0516 2.0516v4.1031c-1e-5 1.1331-0.91849 2.0516-2.0516 2.0516h-4.1031c-1.1331 0-2.0516-0.91849-2.0516-2.0516v-4.1031c2e-5 -1.1331 0.91849-2.0516 2.0516-2.0516z"></path>
                        </g>
                    </svg>
                    <p class="mt-2 mb-0">Flow failed to establish</p>
                    <p class="fst-italic">Is the service down?</p>
                </div>
                <section class="card m-3 bg-body shadow font-monospace d-none border-success" id="display-app">
                    <header class="card-header d-flex justify-content-between">
                        <h1 class="h6 lh-base mb-0">
                            <a class="text-reset text-decoration-none" data-bs-toggle="collapse" href="#display-app-collapse" role="button" aria-expanded="true" aria-controls="display-app-collapse" aria-label="Display app">
                                <i class="bi bi-chevron-down"></i>
                                <span></span>
                            </a>
                            <span class="nav nav-pills d-inline-flex" role="tablist" id="display-app-tabs">
                                <button class="nav-link py-0 active" id="display-app-render-tab" data-bs-toggle="pill" type="button" role="tab" aria-selected="true">Render</button>
                                <button class="nav-link py-0" id="display-app-utf8-tab" data-bs-toggle="pill" type="button" role="tab" aria-selected="false">UTF-8</button>
                                <button class="nav-link py-0" id="display-app-hex-tab" data-bs-toggle="pill" type="button" role="tab" aria-selected="false">Hex</button>
                            </span>
                        </h1>
                        <a class="text-nowrap" href="#" target="_blank">Generate script</a>
                    </header>
                    <div class="collapse show" id="display-app-collapse">
                        <pre class="card-body mb-0"></pre>
                        <template id="display-app-fileinfo">
                            <div class="card mt-1 mb-2 ms-3 bg-secondary-subtle font-monospace rounded-0">
                                <header class="card-header d-flex justify-content-between py-1 px-2 small">
                                    <a class="text-reset text-decoration-none" data-bs-toggle="collapse" href="#" aria-expanded="true" aria-label="Display app file info">
                                        <i class="bi bi-chevron-down"></i>
                                        <span></span>
                                    </a>
                                </header>
                                <div class="tab-content collapse show">
                                    <pre class="card-body mb-0 p-2 tab-pane active display-app-render"></pre>
                                    <pre class="card-body mb-0 p-2 tab-pane display-app-utf8"></pre>
                                    <pre class="card-body mb-0 p-2 tab-pane display-app-hex"></pre>
                                </div>
                            </div>
                        </template>
                    </div>
                </section>
                <section class="card m-3 bg-body shadow font-monospace d-none border-primary" id="display-raw">
                    <header class="card-header d-flex justify-content-between">
                        <h1 class="h6 lh-base mb-0">
                            <a class="text-reset text-decoration-none" data-bs-toggle="collapse"
                                href="#display-raw-collapse" role="button" aria-expanded="true"
                                aria-controls="display-raw-collapse">
                                    <i class="bi bi-chevron-down"></i>
                                    Raw data
                                </a>
                                <span class="nav nav-pills d-inline-flex" role="tablist">
                            <button class="nav-link py-0 active" id="display-raw-utf8-tab" data-bs-toggle="pill"
                                    data-bs-target="#display-raw-utf8" type="button" role="tab" aria-controls="display-raw-utf8"
                                    aria-selected="true">UTF-8</button>
                            <button class="nav-link py-0" id="display-raw-hex-tab" data-bs-toggle="pill"
                                    data-bs-target="#display-raw-hex" type="button" role="tab" aria-controls="display-raw-hex"
                                    aria-selected="false">Hex</button>
                            </span>
                        </h1>
                        <a class="text-nowrap" id="display-raw-replay" href="#" target="_blank">Generate script</a>
                    </header>
                    <div class="tab-content collapse show" id="display-raw-collapse">
                        <pre class="card-body mb-0 tab-pane active" id="display-raw-utf8" role="tabpanel" aria-labelledby="display-raw-utf8-tab" tabindex="0"></pre>
                        <pre class="card-body mb-0 tab-pane" id="display-raw-hex" role="tabpanel" aria-labelledby="display-raw-hex-tab" tabindex="0"></pre>
                    </div>
                </section>
            </div> -->
        </div>
    </div>
    <div class="fixed-bottom m-2" bind:clientHeight={tickProgressBarHeight}>
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