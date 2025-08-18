<script lang="ts">
	import { ctfConfig, selectedPanel } from "$lib/state.svelte";
	import Toast from "./Toast.svelte";
	import StatsOverview from "./StatsOverview.svelte";
	import StatsServices from "./StatsServices.svelte";

    let toast: Toast;

    let activeView: "overview" | "services" = $state("overview");

    let data = $derived.by(async () => {
        const res = await fetch("/api/stats");

        return await res.json();
    });
</script>

<div class="card shadow-lg h-100 overflow-auto">
    <div class="card-header hstack">
        <h5 class="modal-title flex-grow-1">Stats</h5>
        <button onclick={() => {selectedPanel.view = undefined; ctfConfig.hideSideBar = false;}} type="button" class="btn-close" aria-label="Close"></button>
    </div>
    <div class="card-body">
        <ul class="nav nav-underline">
            <li class="nav-item">
                <button onclick={() => activeView = "overview"} class="nav-link {activeView === "overview" ? "active" : ""}" >Overview</button>
            </li>
            <li class="nav-item">
                <button onclick={() => activeView = "services"} class="nav-link {activeView === "services" ? "active" : ""}">Services</button>
            </li>
            
            <button onclick={() => ctfConfig.hideSideBar = !ctfConfig.hideSideBar} class="ms-auto btn btn-outline-primary" aria-label="Fullscreen">
                {#if ctfConfig.hideSideBar}
                    <i class="bi bi-fullscreen-exit"></i>
                {:else}
                    <i class="bi bi-fullscreen"></i>
                {/if}
            </button>
        </ul>

        <hr>

        {#await data}
            <div class="d-flex justify-content-center">
                <div class="spinner-border my-5" role="status">
                    <span class="visually-hidden">Loading…</span>
                </div>
            </div>
        {:then data} 
            {#if activeView === "overview"}
                <StatsOverview flagsOut={data.flagsOut} flowsNum={data.flowsNum} />
            {:else if activeView === "services"}
                <StatsServices flagsOut={data.flagsOut} flowsNum={data.flowsNum} flagsOutFlows={data.flagsOutFlows} />
            {/if}
        {/await}
    </div>
</div>

<!-- Toast -->
<Toast bind:this={toast} />