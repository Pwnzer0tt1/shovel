<script lang="ts">
	import { ctfConfig, selectedPanel } from "$lib/state.svelte";
	import Toast from "./Toast.svelte";
	

    let toast: Toast;

    let start_date = $state(ctfConfig.config.start_date);
    let end_date = $state(ctfConfig.config.end_date);
    let tick_length = $state(ctfConfig.config.tick_length);
    let refresh_rate = $state(ctfConfig.config.refresh_rate);
    async function updateSettings(e: any) {
        const res = await fetch("/api/config", {
            method: "POST",
            body: JSON.stringify({
                start_date,
                end_date,
                tick_length,
                refresh_rate
            }),
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (res.ok) {
            toast.show("success", "Settings updated");
            ctfConfig.config =  await res.json();
        }
        else {
            toast.show("danger", "Failed to update settings", JSON.stringify(await res.json()))
        }
    }
</script>

<div class="card shadow-lg h-100">
    <div class="card-header hstack">
        <h5 class="modal-title flex-grow-1">Settings</h5>
        <button onclick={() => selectedPanel.view = undefined} type="button" class="btn-close " aria-label="Close"></button>
    </div>
    <div class="card-body">
        <div class="mb-3">
            <label for="start-datetime" class="form-label">Start datetime (UTC time)</label>
            <input bind:value={start_date} name="start_date" type="datetime-local" class="form-control" id="start-datetime">
        </div>
        <div class="mb-3">
            <label for="end-date" class="form-label">End datetime (UTC time)</label>
            <input bind:value={end_date} name="end_date" type="datetime-local" class="form-control" id="end-d">
        </div>
        <div class="mb-3">
            <label for="tick-length" class="form-label">Tick length (s)</label>
            <input bind:value={tick_length} name="tick_length" type="number" class="form-control" id="tick-length">
        </div>
        <div class="mb-3">
            <label for="refresh-rate" class="form-label">Refresh rate (s)</label>
            <input bind:value={refresh_rate} name="refresh_rate" type="number" class="form-control" id="refresh-rate">
        </div>

        <button onclick={updateSettings} class="btn btn-primary w-100">Update settings</button>
    </div>
</div>

<!-- Toast -->
<Toast bind:this={toast} />