<script lang="ts">
	import { ctfConfig, tickInfo } from "$lib/state.svelte";
	import { onMount } from "svelte";


    let startTs = $derived(Math.floor(Date.parse(ctfConfig.config.start_date + "Z") / 1000));
    let tickLength = $derived(ctfConfig.config.tick_length);

    let progressBarValue = $state(0);
    let tickTimer = $state("00:00");
    let progressBarColor = $state("success");

    function updateProgressBar() {
        ctfConfig.ctfEnded = Date.now() > Date.parse(ctfConfig.config.end_date);

        const now = ctfConfig.ctfEnded ? Date.parse(ctfConfig.config.end_date) / 1000 : Date.now() / 1000;
        const currentTick = Math.floor((now - startTs) / tickLength);
        const tickStartTime = startTs + (currentTick * tickLength);
        const tickEndTime = tickStartTime + tickLength;
        const progress = ((now - tickStartTime) / tickLength) * 100;
        const remainingSeconds = Math.max(0, tickEndTime - now);

        progressBarValue = Math.min(100, Math.max(0, progress));

        tickInfo.tickNumber = currentTick;

        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = Math.floor(remainingSeconds % 60);

        tickTimer = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

        if (progress < 50) {
            progressBarColor = "success";
        }
        else if (progress < 80) {
            progressBarColor = "warning";
        }
        else {
            progressBarColor = "danger";
        }
    }

    onMount(() => {
        updateProgressBar();

        setInterval(updateProgressBar, 1000);
    });
</script>

<div class="card bg-body-tertiary p-2 shadow-lg w-100">
    <div class="hstack w-100 gap-2">
        <small class="fw-bold">Tick {tickInfo.tickNumber}</small>
        <div class="flex-grow-1">
            <div class="progress" role="progressbar" aria-label="Tick progress bar" aria-valuenow={progressBarValue} aria-valuemin="0" aria-valuemax="100" style="height: 8px;">
                <div class="progress-bar bg-{progressBarColor} progress-bar-striped progress-bar-animated" style="width: {progressBarValue}%"></div>
            </div>
        </div>
        <small>{tickTimer}</small>
    </div>
</div>