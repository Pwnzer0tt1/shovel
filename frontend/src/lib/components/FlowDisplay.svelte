<script lang="ts">
	import type { CtfConfig, Flow } from "$lib/schema";
	import { selectedFlow } from "$lib/state.svelte";
	import { onMount } from "svelte";
	import { includes } from "zod/v4";
    
    let { ctfConfig }: { ctfConfig: CtfConfig } = $props();

    let appDataActiveView: "render" | "utf8" | "hex" = $state("render");

    const MAGIC_EXT = {
        'GIF image': 'gif',
        'HTML document': 'html',
        'JPEG image': 'jpg',
        'PDF document': 'pdf',
        'PNG image': 'png',
        'SVG Scalable Vector Graphics image': 'svg',
        'VGM Video Game Music': 'vgm',
        'Web Open Font': 'woff',
        'Zip archive': 'zip'
    };

    const HTTP_HEADER_BL = [
        ':method',
        ':path',
        ':scheme',
        ':status',
        'accept-ranges',
        'allow',
        'cache-control',
        'connection',
        'content-length',
        'content-range',
        'content-type',
        'cross-origin-opener-policy',
        'date',
        'host',
        'last-modified',
        'location',
        'referrer-policy',
        'transfer-encoding',
        'vary',
        'x-content-type-options',
        'x-frame-options',
        undefined // header name is missing
    ];

    function getExtFromMagic(magic: string) {
        for (const [magicPrefix, ext] of Object.entries(MAGIC_EXT)) {
            if (magic.startsWith(magicPrefix)) {
                return ext;
            }
        }
        return "txt";
    }

    let flowData = $derived.by(async () => {
        let res = await fetch(`/api/flow/${selectedFlow.flow?.id}`);
        let json = await res.json();
        console.log(json);

        const dateStart = new Date(json.flow.ts_start / 1000).toISOString().split("T").join(", ");
        const dateEnd = new Date(json.flow.ts_end / 1000).toISOString().split("T").join(", ");
        const start_ts = Math.floor(Date.parse(ctfConfig.start_date) / 1000);
        const tick = ((json.flow.ts_start / 1000000 - start_ts) / ctfConfig.tick_length).toFixed(3);

        let fileinfos: any = {};
        for (const [txId, data] of Object.entries(json[json.flow.app_proto])) {
            console.log(data)
            let appDataFileinfo: {
                data: Blob,
                ext: string
            }[] = [];
            if (json.fileinfo) {
                let fileinfo = json.fileinfo.map((x: any) => JSON.parse(x.extra_data));
                for (const d of Object.values(fileinfo)) {
                    if (d.tx_id === Number(txId)) {
                        let f = await fetch(`/filestore/${d.sha256.slice(0, 2)}/${d.sha256}`);
                        let ext = getExtFromMagic(d.magic ?? "");
                        let blob = await f.blob();
                        appDataFileinfo.push({
                            data: blob,
                            ext
                        });
                    }
                }
            }
            fileinfos[json.flow.app_proto] = appDataFileinfo;
        }

        console.log(fileinfos);

        return {
            dateStart,
            dateEnd,
            tick,
            proto: json.flow.proto,
            appProto: json.flow.app_proto,
            srcIpPort: json.flow.src_ipport,
            dstPort: json.flow.dest_port,
            dstIpPort: json.flow.dest_ipport,
            pktsToServer: json.flow.extra_data.pkts_toserver,
            pktsToClient: json.flow.extra_data.pkts_toclient,
            bytesToServer: json.flow.extra_data.bytes_toserver,
            bytesToClient: json.flow.extra_data.bytes_toclient,
            metadata: json.flow.metadata,
            alerts: json.alert,
            anomalies: json.anomaly,
            flowAppProto: json[json.flow.app_proto],
            fileinfos
        };
    });

    function changeAppDataView(event: any) {
        appDataActiveView = event.currentTarget.value;
    }
</script>

{#await flowData}
    Loading...
{:then flowData}
    <div class="vstack gap-3">
        <!-- Flow card -->
        <div class="row">
            <div class="col-auto">
                <div class="card p-2 border-secondary shadow-lg h-100">
                    <p class="my-0">Tick {flowData.tick}</p>
                    <p class="my-0">From {flowData.dateStart}</p>
                    <p class="my-0">to {flowData.dateEnd}</p>
                </div>
            </div>
            <div class="col">
                <div class="card p-2 border-secondary shadow-lg">
                    <p class="my-0">{flowData.proto} flow from {flowData.srcIpPort} to {flowData.dstIpPort}</p>
                    <p class="my-0"><i class="bi bi-arrow-right"></i> {flowData.pktsToServer} packets ({flowData.bytesToServer} bytes)</p>
                    <p class="my-0"><i class="bi bi-arrow-left"></i> {flowData.pktsToClient} packets ({flowData.bytesToClient} bytes)</p>
                </div>
            </div>
            <div class="col-auto">
                <button class="btn btn-success shadow-lg h-100" aria-label="Download pcap"><i class="bi bi-file-earmark-arrow-down-fill"></i></button>
            </div>
        </div>

        <!-- Alerts -->
        <div class="vstack gap-3">
            {#each flowData.alerts as a}
                {@const alert = JSON.parse(a.extra_data)}
                {#if alert.signature !== "tag"}
                    <div class="card p-2 border-{a.color} shadow-lg">{alert.signature}</div>
                {/if}
            {/each}
        </div>

        <!-- Anomalies -->
        <div class="vstack gap-3">
            {#each flowData.anomalies as anomaly}
                <div class="card p-2 border-warning shadow-lg">Dissection anomaly: {JSON.stringify(anomaly)}</div>
            {/each}
        </div>

        <!-- App data -->
        {#if flowData.appProto && flowData.appProto !== "failed"}
            <div class="accordion">
                <div class="accordion-item border-success shadow-lg">
                    <h2 class="accordion-header">
                        <button class="accordion-button bg-body-tertiary text-body-emphasis" type="button" data-bs-toggle="collapse" data-bs-target="#display-app" aria-expanded="true" aria-controls="display-app">{flowData.appProto}</button>
                    </h2>
                    <div id="display-app" class="accordion-collapse collapse show" data-bs-parent="#accordionExample">
                        <div class="accordion-body vstack gap-3">
                            <div class="hstack">
                                <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                                    <input value="render" onchange={changeAppDataView} type="radio" class="btn-check" name="btnradio" id="app-data-btn-render" autocomplete="off" checked>
                                    <label class="btn btn-outline-primary" for="app-data-btn-render">Render</label>

                                    <input value="utf8" onchange={changeAppDataView} type="radio" class="btn-check" name="btnradio" id="app-data-btn-utf8" autocomplete="off">
                                    <label class="btn btn-outline-primary" for="app-data-btn-utf8">UTF-8</label>

                                    <input value="hex" onchange={changeAppDataView} type="radio" class="btn-check" name="btnradio" id="app-data-btn-hex" autocomplete="off">
                                    <label class="btn btn-outline-primary" for="app-data-btn-hex">Hex</label>
                                </div>
                                <a class="ms-auto" href="/">Generate script</a>
                            </div>
                            <hr>
                            <div>
                                {#if flowData.appProto === "http" || flowData.appProto === "http2"}
                                    {#each flowData.flowAppProto as data}
                                        {@const requestHeaders = data.request_headers.filter((x: any) => !HTTP_HEADER_BL.includes(x.name.toLowerCase()))}
                                        {@const responseHeaders = data.response_headers.filter((x: any) => !HTTP_HEADER_BL.includes(x.name.toLowerCase()))}
                                        {#each requestHeaders as h}
                                            <p class="my-0">{h.name}: {h.value}</p>
                                        {/each}
                                        {#each responseHeaders as h}
                                            <p class="my-0">{h.name}: {h.value}</p>
                                        {/each}
                                    {/each}
                                {/if}
                            </div>
                            <div>
                                {#each flowData.flowAppProto as data}
                                    {#if flowData.appProto === "http" || flowData.appProto === "http2"}
                                        <span class="fw-bold">{data.http_method ?? "?"} http://{data.hostname}:{data.http_port ?? flowData.dstPort}{data.url ?? ""} {data.protocol ?? ""}  <i class="bi bi-caret-left-fill"></i> {data.status ?? "?"}</span>
                                    {:else}
                                        <span>{JSON.stringify(data, null, 4)}</span>
                                    {/if}
                                {/each}
                            </div>
                            <div class="vstack gap-5 mt-5">
                                {#if appDataActiveView === "render"}
                                    {#each Object.entries(flowData.fileinfos[flowData.appProto]) as [k, v]}
                                        <div class="accordion" id="accordionExample">
                                            <div class="accordion-item">
                                                <h2 class="accordion-header">
                                                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#app-render-{k}" aria-expanded="true" aria-controls="collapseOne">File </button>
                                                </h2>
                                                <div id="app-render-{k}" class="accordion-collapse collapse show" data-bs-parent="#accordionExample">
                                                    <div class="accordion-body">
                                                        {#if ["gif", "jpg", "png", "svg"].includes(v.ext)}
                                                            <img src={URL.createObjectURL(v.data)} alt="">
                                                        {:else if v.ext === "pdf"}
                                                            <iframe src={URL.createObjectURL(v.data)} frameborder="0"></iframe>
                                                        {:else if v.ext === "html"}
                                                            <iframe class="w-100" title="HTML renderer" src={URL.createObjectURL(v.data.slice(0, v.data.size, "text/html"))} frameborder="0"></iframe>
                                                        {:else}
                                                            {#await v.data.text() then t}
                                                                <p class="text-break">{t}</p>
                                                            {/await}
                                                        {/if}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    {/each}
                                {:else if appDataActiveView === "utf8"}
                                {:else if appDataActiveView === "hex"}
                                {/if}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
        
        <!-- Raw data -->
        
    </div>
{/await}