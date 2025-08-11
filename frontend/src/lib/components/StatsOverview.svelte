<script lang="ts">
	import { ctfConfig, tickInfo } from "$lib/state.svelte";
    import { Chart } from "chart.js/auto";
	

    let { flagsOut, flowsNum }: {
        flagsOut: number[],
        flowsNum: number
    } = $props();

    let ctx: HTMLCanvasElement;
    $effect(() => {
        let flagsOutCounter = new Array(tickInfo.tickNumber).fill(0);
        const start_ts = Math.floor(Date.parse(ctfConfig.config.start_date + "Z") / 1000);
        for (const f of flagsOut) {
            const tick = Math.floor((Number(f) / 1000000 - start_ts) / ctfConfig.config.tick_length);

            flagsOutCounter[tick]++;
        }

        const chart = new Chart(
            ctx,
            {
                type: 'line',
                data: {
                    xLabels: [...Array(tickInfo.tickNumber).keys()],
                    datasets: [{
                        label: '# of flags out',
                        data: flagsOutCounter,
                        borderColor: 'red'
                    }]
                }
            }
        );
    });
</script>

<div class="vstack gap-3">
    <div class="hstack gap-3">
        <h3><span class="badge text-bg-primary">FLOWS: {flowsNum}</span></h3>
        <h3><span class="badge text-bg-danger"><i class="bi bi-flag-fill"></i> FLAGS OUT: {flagsOut.length}</span></h3>
    </div>
    <canvas bind:this={ctx}></canvas>
</div>