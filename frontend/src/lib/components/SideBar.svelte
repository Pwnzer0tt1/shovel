<script lang="ts">
	import type { CtfConfig, Flows, Tags } from "$lib/schema";
	import FlowCard from "./FlowCard.svelte";

    let { ctfConfig, flows, tags, tickProgressBarHeight }: {
        ctfConfig: CtfConfig,
        flows: Flows,
        tags: Tags,
        tickProgressBarHeight: number
    } = $props();

    let innerHeight = $state(0);
    let sideBarHeight = $state(0);
    let autoUpdateBtnHeight = $state(0);
    let settingsHeight = $state(0);
    let flowsListHeight = $derived(sideBarHeight - autoUpdateBtnHeight - settingsHeight - tickProgressBarHeight)
</script>

<svelte:window bind:innerHeight />

<div bind:clientHeight={sideBarHeight} class="vstack gap-2 h-100">
    <button bind:clientHeight={autoUpdateBtnHeight} title="Refresh flow list" class="btn btn-success shadow-lg">Auto-Update: ON</button>
    <div bind:clientHeight={settingsHeight} class="hstack gap-2">
        <select class="form-select shadow-lg">
            <option value="" selected>All flows</option>
            <option value="!">Flows from unknown services</option>
            {#each Object.entries(ctfConfig.services) as [name, service]}
                <optgroup label={name} data-ipports={ service.ipports.join(" ") }>
                    {#if service.ipports.length > 1}
                        <option value={ service.ipports.join(", ") }>All ({ name })</option>
                    {/if}
                    {#each service.ipports as ipport}
                        <option value={ipport}>{ipport} ({ name })</option>
                    {/each}
                </optgroup>
            {/each}
        </select>
        <button class="btn btn-secondary shadow-lg" data-bs-toggle="modal" data-bs-target="#servicesModal" title="Customize services" aria-label="Service settings">
            <i class="bi bi-gear-fill"></i>
        </button>
        <div class="dropend">
            <button class="btn btn-secondary shadow-lg text-nowrap" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-label="Dropdown filter">
                <i class="bi bi-funnel-fill"></i>
                <i class="bi bi-chevron-right"></i>
            </button>
            <div class="dropdown-menu p-3 filter-dropdown rounded-0">
                <div class="input-group flex-nowrap mb-3">
                    <span class="input-group-text gap-2">
                        <i class="bi bi-clock-fill"></i> Before tick
                    </span>
                    <input type="number" min="0" class="form-control" placeholder="now" id="filter-time-until">
                </div>
                <div class="input-group flex-nowrap mb-3">
                    <span class="input-group-text">Protocol</span>
                    <select class="form-select" id="filter-protocol"></select>
                </div>
                <div class="input-group flex-nowrap mb-3">
                    <span class="input-group-text">Search</span>
                    <input type="text" class="form-control" placeholder="glob, e.g. 'ex?mple'" id="filter-search">
                </div>
                <div id="filter-tag">
                    <div class="card mb-2 bg-secondary-subtle rounded-0">
                        <header class="card-header d-flex justify-content-between py-1 px-2 small">Available tags</header>
                        <div class="card-body mb-0 p-2" id="filter-tag-available"></div>
                    </div>
                    <div class="card mb-2 bg-secondary-subtle rounded-0 border-success">
                        <header class="card-header d-flex justify-content-between py-1 px-2 small">Required tags</header>
                        <div class="card-body mb-0 p-2" id="filter-tag-require"></div>
                    </div>
                    <div class="card mb-2 bg-secondary-subtle rounded-0 border-danger">
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
    <div class="card border-2 p-1 shadow-lg" style="height: {flowsListHeight}px;">
        {#if flows.length == 0}
            <div class="d-flex justify-content-center">
                <div class="spinner-border my-5" role="status">
                    <span class="visually-hidden">Loading…</span>
                </div>
            </div>
        {:else}
            <div class="overflow-y-scroll">
                <div class="list-group list-group-flush m-1 rounded" style="scrollbar-">
                    {#each Object.entries(flows) as [index, f]}
                        <FlowCard index={Number(index)} flow={f} tags={tags} ctfConfig={ctfConfig} />
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</div>