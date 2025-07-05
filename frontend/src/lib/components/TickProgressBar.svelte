<script lang="ts">
	import { onMount } from "svelte";

    let { startTs, tickLength }: {
        startTs: number,
        tickLength: number
    } = $props();

    let progressBarValue = $state(0);
    let tickInfo = $state("Tick 0");
    let tickTimer = $state("00:00");
    let progressBarColor = $state("success");

    function updateProgressBar() {
        const now = Date.now() / 1000;
        const currentTick = Math.floor((now - startTs) / tickLength);
        const tickStartTime = startTs + (currentTick * tickLength);
        const tickEndTime = tickStartTime + tickLength;
        const progress = ((now - tickStartTime) / tickLength) * 100;
        const remainingSeconds = Math.max(0, tickEndTime - now);

        progressBarValue = Math.min(100, Math.max(0, progress));
        tickInfo = `Tick ${currentTick}`;

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

<nav class="card bg-body-tertiary border-2 p-2">
    <div class="row align-items-center">
        <div class="col-auto">
            <small class="fw-bold">{tickInfo}</small>
        </div>
        <div class="col">
            <div class="progress" role="progressbar" aria-label="Tick progress bar" aria-valuenow={progressBarValue} aria-valuemin="0" aria-valuemax="100" style="height: 8px;">
                <div class="progress-bar bg-{progressBarColor} progress-bar-striped progress-bar-animated" style="width: {progressBarValue}%"></div>
            </div>
        </div>
        <div class="col-auto">
            <small>{tickTimer}</small>
        </div>
    </div>
</nav>