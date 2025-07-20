<script lang="ts">
	import type { CtfConfig, Flows, Tags } from "$lib/schema";
	import { flowsFilters, selectedPanel, tickInfo } from "$lib/state.svelte";
	import FlowCard from "./FlowCard.svelte";

    let { ctfConfig, flows, tags, appProto }: {
        ctfConfig: CtfConfig,
        flows: Flows,
        tags: Tags,
        appProto: string[]
    } = $props();

    let innerHeight = $state(0);
    let sideBarHeight = $state(0);
    let autoUpdateBtnHeight = $state(0);
    let settingsHeight = $state(0);
    let flowsListHeight = $derived(sideBarHeight - autoUpdateBtnHeight - settingsHeight);

    let selectedSeervice: string = $state("");
    let beforeTick: number | undefined = $state(undefined);
    let protocol: string = $state("");
    let search: string = $state("");

    function changeSelectedService() {

    }

    function changeBeforeTick() {
        if (beforeTick) {
            flowsFilters.ts_to = String(Math.floor((beforeTick * ctfConfig.tick_length + Math.floor(Date.parse(ctfConfig.start_date) / 1000)) * 1000000));
        }
    }

    function changeProtocol() {
        if (protocol !== "") {
            flowsFilters.app_proto = protocol;
        }
        else {
            flowsFilters.app_proto = undefined;
        }
    }

    function changeSearch() {
        if (search !== "") {
            flowsFilters.search = search;
        }
        else {
            flowsFilters.search = undefined;
        }
    }
</script>

<svelte:window bind:innerHeight />

<div bind:clientHeight={sideBarHeight} class="vstack gap-2 h-100">
    <button bind:clientHeight={autoUpdateBtnHeight} title="Refresh flow list" class="btn btn-success shadow-lg">Auto-Update: ON</button>
    <div bind:clientHeight={settingsHeight} class="hstack gap-2">
        <select class="form-select shadow-lg">
            <option value="" selected>All flows</option>
            <option value="!">Flows from unknown services</option>
            {#each Object.entries(ctfConfig.services) as [name, service]}
                <optgroup label={name}>
                    {#if service.ipports.length > 1}
                        <option value={ service.ipports.join(", ") }>All ({ name })</option>
                    {/if}
                    {#each service.ipports as ipport}
                        <option value={ipport}>{ipport} ({ name })</option>
                    {/each}
                </optgroup>
            {/each}
        </select>
        <button onclick={() => selectedPanel.view = "ServicesManager"} class="btn btn-secondary shadow-lg" title="Customize services" aria-label="Service settings">
            <i class="bi bi-gear-fill"></i>
        </button>
        <div class="dropend">
            <button class="btn btn-secondary shadow-lg text-nowrap" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-label="Dropdown filter">
                <i class="bi bi-funnel-fill"></i>
                <i class="bi bi-chevron-right"></i>
            </button>
            <div class="dropdown-menu p-2" style="width: 25vw;">
                <div class="input-group flex-nowrap mb-3">
                    <span class="input-group-text gap-2"><i class="bi bi-clock-fill"></i> Before tick</span>
                    <input onchange={changeBeforeTick} bind:value={beforeTick} type="number" min="0" class="form-control" placeholder={tickInfo.tickNumber.toString()}>
                </div>
                <div class="input-group flex-nowrap mb-3">
                    <span class="input-group-text">Protocol</span>
                    <select onchange={changeProtocol} bind:value={protocol} class="form-select">
                        <option value="">All</option>
                        <option value="raw">Raw</option>
                        {#each appProto as proto}
                            <option value={proto}>{proto.toUpperCase()}</option>
                        {/each}
                    </select>
                </div>
                <div class="input-group flex-nowrap mb-3">
                    <span class="input-group-text">Search</span>
                    <input onchange={changeSearch} bind:value={search} type="text" class="form-control" placeholder="glob, e.g. 'ex?mple'">
                </div>
                <div id="filter-tag">
                    <div class="card mb-2 bg-secondary-subtle">
                        <header class="card-header d-flex justify-content-between py-1 px-2 small">Available tags</header>
                        <div class="card-body mb-0 p-2" id="filter-tag-available"></div>
                    </div>
                    <div class="card mb-2 bg-secondary-subtle border-success">
                        <header class="card-header d-flex justify-content-between py-1 px-2 small">Required tags</header>
                        <div class="card-body mb-0 p-2" id="filter-tag-require"></div>
                    </div>
                    <div class="card mb-2 bg-secondary-subtle border-danger">
                        <header class="card-header d-flex justify-content-between py-1 px-2 small">Denied tags</header>
                        <div class="card-body mb-0 p-2" id="filter-tag-deny"></div>
                    </div>
                    <p class="my-1">
                        <small class="fw-light fst-italic">Hold <kbd>Shift</kbd> to deny tag.</small>
                    </p>
                </div>
            </div>
        </div>
    </div>
    <div class="card p-1 shadow-lg" style="height: {flowsListHeight}px;">
        {#if flows.length == 0}
            <div class="d-flex justify-content-center">
                <div class="spinner-border my-5" role="status">
                    <span class="visually-hidden">Loading…</span>
                </div>
            </div>
        {:else}
            <div class="overflow-y-scroll">
                <div class="list-group list-group-flush m-1 rounded">
                    {#each Object.entries(flows) as [index, f]}
                        <FlowCard index={Number(index)} flow={f} tags={tags} ctfConfig={ctfConfig} />
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</div>