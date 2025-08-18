<script lang="ts">
	import { ctfConfig, tickInfo } from "$lib/state.svelte";
    import { Chart } from "chart.js/auto";
	

    let { flagsOut, flowsNum, flagsOutFlows }: {
        flagsOut: number[],
        flowsNum: number,
        flagsOutFlows: {
            ts_start: string,
            dest_ipport: string | null
        }[]
    } = $props();

    let ctx: HTMLCanvasElement;
    $effect(() => {
        const start_ts = Math.floor(Date.parse(ctfConfig.config.start_date + "Z") / 1000);
        let flagsOutServices = [];

        for (const [n, s] of Object.entries(ctfConfig.config.services)) {
            let flagsCounter = new Array(tickInfo.tickNumber).fill(0);
            const ipports = s.ipports.map((v) => `${v.ip}:${v.port}`);
            for (const f of flagsOutFlows) {
                if (ipports.includes(f.dest_ipport || "")) {
                    const tick = Math.floor((Number(f.ts_start) / 1000000 - start_ts) / ctfConfig.config.tick_length);
                    flagsCounter[tick]++;
                }
            }

            flagsOutServices.push({
                label: n,
                data: flagsCounter,
                borderColor: s.color
            });
        }

        const chart = new Chart(
            ctx,
            {
                type: 'line',
                data: {
                    xLabels: [...Array(tickInfo.tickNumber).keys()],
                    datasets: flagsOutServices
                },
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: "Flags out by service"
                        }
                    }
                }
            }
        );
    });
</script>

<div class="vstack gap-3">
    <div class="hstack gap-3">
        
    </div>
    <canvas bind:this={ctx}></canvas>
</div>