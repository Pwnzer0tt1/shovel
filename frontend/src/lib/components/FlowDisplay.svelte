<script lang="ts">
	import type { Flow } from "$lib/schema";
	import { ctfConfig, selectedFlow } from "$lib/state.svelte";
	import TextViewer from "./TextViewer.svelte";
	import HexDumpViewer from "./HexDumpViewer.svelte";
    

    let appDataActiveView: "render" | "utf8" | "hex" = $state("render");
    let rawDataActiveView: "utf8" | "hex" = $state("utf8");

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

    function getExtFromMagic(magic: string) {
        for (const [magicPrefix, ext] of Object.entries(MAGIC_EXT)) {
            if (magic.startsWith(magicPrefix)) {
                return ext;
            }
        }
        return "txt";
    }

    let rawFlowData = $derived.by(async () => {
        let res = await fetch(`/api/flow/${selectedFlow.flow?.id}/raw`);
        let json = await res.json();

        return {
            raw: json
        }
    });

    let flowData = $derived.by(async () => {
        let res = await fetch(`/api/flow/${selectedFlow.flow?.id}`);
        let json: {
            flow: Flow,
            fileinfo?: {
                extra_data: {
                    gaps: boolean,
                    size: number,
                    state: string,
                    tx_id: number,
                    sha256: string,
                    stored: boolean,
                    file_id: number,
                    filename: string
                }
            }[],
            alert?: {
                extra_data: {
                    gid: number,
                    rev: number,
                    action: string,
                    category: string,
                    metadata: {
                        tag: string[],
                        color: string[]
                    },
                    severity: number,
                    signature: string,
                    signature_id: number
                },
                color: string
            }[],
            anomaly: {
                extra_data: any
            }[],
            http?: any,
            http2?: any,
            quic?: any,
            ftp?: any,
            tls?: any,
            tftp?: any,
            nfs?: any,
            smb?: any,
            ssh?: any,
            rdp?: any,
            rfb?: any
        } = await res.json();

        const dateStart = json.flow.extra_data?.start.split("T").join(", ");
        const dateEnd = json.flow.extra_data?.end.split("T").join(", ");
        const start_ts = Math.floor(Date.parse(ctfConfig.start_date) / 1000);
        const tick = ((Number(json.flow.ts_start) / 1000000 - start_ts) / ctfConfig.tick_length).toFixed(3);

        let fileinfos: {
            [key: string]: {
                data: Blob,
                ext: string,
                filename: string,
                filestore: string,
                magic: string,
                bytes: Uint8Array
            }[]
        } = {};
        if (json.flow.app_proto && json.flow.app_proto !== "failed") {
            for (const [txId, data] of Object.entries(json[json.flow.app_proto])) {
                let appDataFileinfo: {
                    data: Blob,
                    ext: string,
                    filename: string,
                    filestore: string,
                    magic: string,
                    bytes: Uint8Array,
                    sha256: string
                }[] = [];
                if (json.fileinfo) {
                    let fileinfo = json.fileinfo.map((x: any) => x.extra_data);
                    for (const d of Object.values(fileinfo)) {
                        if (d.tx_id === Number(txId)) {
                            let f = await fetch(`/filestore/${d.sha256.slice(0, 2)}/${d.sha256}`);
                            let ext = getExtFromMagic(d.magic ?? "");
                            let blob = await f.clone().blob();
                            let bytes = await f.bytes();
                            appDataFileinfo.push({
                                data: blob,
                                ext,
                                filename: d.filename,
                                filestore: `/filestore/${d.sha256.slice(0, 2)}/${d.sha256}`,
                                magic: d.magic ?? "",
                                bytes,
                                sha256: d.sha256
                            });
                        }
                    }
                }
                fileinfos[json.flow.app_proto] = appDataFileinfo;
            }
        }

        return {
            dateStart,
            dateEnd,
            tick,
            proto: json.flow.proto,
            appProto: json.flow.app_proto,
            flowEstablished: json.flow.extra_data ? json.flow.extra_data.state !== "new" : undefined,
            srcIpPort: json.flow.src_ipport,
            dstPort: json.flow.dest_port,
            dstIpPort: json.flow.dest_ipport,
            pktsToServer: json.flow.extra_data ? json.flow.extra_data.pkts_toserver : undefined,
            pktsToClient: json.flow.extra_data ? json.flow.extra_data.pkts_toclient : undefined,
            bytesToServer: json.flow.extra_data ? json.flow.extra_data.bytes_toserver : undefined,
            bytesToClient: json.flow.extra_data ? json.flow.extra_data.bytes_toclient : undefined,
            metadata: json.flow.metadata,
            alerts: json.alert,
            anomalies: json.anomaly,
            flowAppProto: json[json.flow.app_proto],
            fileinfos,
            pcapFilename: json.flow.pcap_filename
        };
    });

    function changeAppDataView(event: any) {
        appDataActiveView = event.currentTarget.value;
    }

    function changeRawDataView(event: any) {
        rawDataActiveView = event.currentTarget.value;
    }

    let editorEl: HTMLDivElement | null = $state(null);
    let editor: any;
    $effect(() => {
        if (editorEl) {
            editor = ace.edit("editor");
            editor.setTheme("ace/theme/dracula");
            editor.setOptions({
                readOnly: true
            });
        }
    });

    function switchView(e: KeyboardEvent) {
        if (e.target) {
            let el = e.target as HTMLElement;
            if (el.tagName !== 'INPUT' && !e.repeat && !e.ctrlKey && e.key === 'v') {
                if (appDataActiveView === "render") {
                    appDataActiveView = "utf8";
                }
                else if (appDataActiveView === "utf8") {
                    appDataActiveView = "hex";
                }
                else if (appDataActiveView === "hex") {
                    appDataActiveView = "render";
                }
                
                if (rawDataActiveView === "utf8") {
                    rawDataActiveView = "hex";    
                }
                else if (rawDataActiveView === "hex") {
                    rawDataActiveView = "utf8";
                }
            }
        }
    }
</script>

<svelte:document onkeydown={switchView} />

{#await flowData}
    Loading...
{:then flowData}
    {@debug flowData}
    <div class="vstack gap-3">
        <!-- Flow card -->
        <div class="hstack gap-2 align-items-stretch">
            <div class="card p-2 border-secondary shadow-lg">
                <p class="my-0">Tick {flowData.tick}</p>
                <p class="my-0">From {flowData.dateStart}</p>
                <p class="my-0">to {flowData.dateEnd}</p>
            </div>
            <div class="flex-grow-1 card p-2 border-secondary shadow-lg">
                <p class="my-0">{flowData.proto} flow from {flowData.srcIpPort} to {flowData.dstIpPort}</p>
                <p class="my-0"><i class="bi bi-arrow-right"></i> {flowData.pktsToServer} packets ({flowData.bytesToServer} bytes)</p>
                <p class="my-0"><i class="bi bi-arrow-left"></i> {flowData.pktsToClient} packets ({flowData.bytesToClient} bytes)</p>
            </div>
            <a href={flowData.pcapFilename.slice(1, -1)} download={flowData.pcapFilename.slice(1, -1).split("/")[2]} class="btn btn-success shadow-lg d-flex align-items-center" aria-label="Download pcap"><i class="bi bi-file-earmark-arrow-down-fill"></i></a>
        </div>

        <!-- Alerts -->
        {#if flowData.alerts}
            {#if flowData.alerts.length > 0}
                <div class="vstack gap-3">
                    {#each flowData.alerts as a}
                        {#if a.extra_data.signature !== "tag"}
                            <div class="card p-2 border-{a.color} shadow-lg">{a.extra_data.signature}</div>
                        {/if}
                    {/each}
                </div>
            {/if}
        {/if}

        <!-- Anomalies -->
        {#if flowData.anomalies.length > 0}
            <div class="vstack gap-3">
                {#each flowData.anomalies as anomaly}
                    <div class="card p-2 border-warning shadow-lg">Dissection anomaly: {JSON.stringify(anomaly)}</div>
                {/each}
            </div>
        {/if}

        <!-- App data -->
        {#if flowData.appProto && flowData.appProto !== "failed"}
            <div class="accordion" id="accordion-app">
                <div class="accordion-item border-success shadow-lg">
                    <h2 class="accordion-header">
                        <button class="accordion-button bg-body-tertiary text-body-emphasis" type="button" data-bs-toggle="collapse" data-bs-target="#display-app" aria-expanded="true" aria-controls="display-app">{flowData.appProto}</button>
                    </h2>
                    <div id="display-app" class="accordion-collapse collapse show" data-bs-parent="#accordion-app">
                        <div class="accordion-body vstack gap-3">
                            <div class="hstack">
                                <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                                    <input value="render" onchange={changeAppDataView} type="radio" class="btn-check" name="appviewbtnradio" id="app-data-btn-render" autocomplete="off" checked={appDataActiveView === "render"}>
                                    <label class="btn btn-outline-primary" for="app-data-btn-render">Render</label>

                                    <input value="utf8" onchange={changeAppDataView} type="radio" class="btn-check" name="appviewbtnradio" id="app-data-btn-utf8" autocomplete="off"  checked={appDataActiveView === "utf8"}>
                                    <label class="btn btn-outline-primary" for="app-data-btn-utf8">UTF-8</label>

                                    <input value="hex" onchange={changeAppDataView} type="radio" class="btn-check" name="appviewbtnradio" id="app-data-btn-hex" autocomplete="off"  checked={appDataActiveView === "hex"}>
                                    <label class="btn btn-outline-primary" for="app-data-btn-hex">Hex</label>
                                </div>
                                <a class="ms-auto" href="/">Generate script</a>
                            </div>
                            <hr>
                            <div class="vstack gap-4">
                                {#each flowData.flowAppProto as data}
                                    <div>
                                        {#if flowData.appProto === "http" || flowData.appProto === "http2"}
                                            <span class="fw-bold">{data.http_method ?? "?"} http://{data.hostname}:{data.http_port ?? flowData.dstPort}{data.url ?? ""} {data.protocol ?? ""} <i class="bi bi-caret-left-fill"></i> {data.status ?? "?"}</span>
                                            {#each data.request_headers as  h}
                                                <p class="my-0">{h.name}: {h.value}</p>
                                            {/each}
                                            {#each data.response_headers as  h}
                                                <p class="my-0">{h.name}: {h.value}</p>
                                            {/each}
                                        {:else}
                                            <span>{JSON.stringify(data, null, 4)}</span>
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                            <div class="vstack gap-3">
                                {#each Object.entries(flowData.fileinfos[flowData.appProto]) as [k, v]}
                                    <div class="accordion" id="accordion-app-{k}">
                                        <div class="accordion-item">
                                            <h2 class="accordion-header btn-group w-100">
                                                <a href={v.filestore} download="{v.filename.replace("/", "_")}.{v.ext}" class="btn btn-success rounded-bottom-0">Download File</a>
                                                <button class="accordion-button rounded-start-0" type="button" data-bs-toggle="collapse" data-bs-target="#app-render-{k}" aria-expanded="true" aria-controls="collapseOne">File: {v.filename}  {v.magic}</button>
                                            </h2>
                                            <div id="app-render-{k}" class="accordion-collapse collapse show" data-bs-parent="#accordion-app-render-{k}">
                                                {#if appDataActiveView === "render"}
                                                    <div class="accordion-body">
                                                        {#if ["gif", "jpg", "png", "svg"].includes(v.ext)}
                                                            <img src={URL.createObjectURL(v.data)} alt="">
                                                        {:else if v.ext === "pdf"}
                                                            <iframe title="App data viewer" src={URL.createObjectURL(v.data)} frameborder="0"></iframe>
                                                        {:else if v.ext === "html"}
                                                            <iframe class="bg-light w-100" style="height: 40vh;" title="HTML renderer" src={URL.createObjectURL(v.data.slice(0, v.data.size, "text/html"))} frameborder="0"></iframe>
                                                        {:else}
                                                            {#await v.data.text() then t}
                                                                <pre class="text-break">{t}</pre>
                                                            {/await}
                                                        {/if}
                                                    </div>
                                                {:else if appDataActiveView === "utf8"}
                                                    <div class="accordion-body p-0">
                                                        {#await v.data.text() then t}
                                                            <TextViewer text={t} ext={v.ext} magic={v.magic} sha256={v.sha256} />
                                                        {/await}
                                                    </div>
                                                {:else if appDataActiveView === "hex"}
                                                    <div class="accordion-body">
                                                        <HexDumpViewer sha256={v.sha256} blob={v.bytes} />
                                                    </div>
                                                {/if}
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
        
        <!-- Raw data -->
        {#await rawFlowData}
            Loading...
        {:then rawFlowData}
            {@debug rawFlowData}
            {#if (flowData.proto === "TCP" || flowData.proto === "UDP") && flowData.flowEstablished}
                <div class="accordion" id="accordion-raw">
                    <div class="accordion-item border-primary shadow-lg">
                        <h2 class="accordion-header">
                            <button class="accordion-button bg-body-tertiary text-body-emphasis" type="button" data-bs-toggle="collapse" data-bs-target="#display-raw" aria-expanded="true" aria-controls="display-raw">Raw data</button>
                        </h2>
                        <div id="display-raw" class="accordion-collapse collapse show" data-bs-parent="#accordion-raw">
                            <div class="accordion-body vstack gap-3">
                                <div class="hstack">
                                    <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                                        <input value="utf8" onchange={changeRawDataView} type="radio" class="btn-check" name="rawviewbtnradio" id="raw-data-btn-utf8" autocomplete="off" checked={rawDataActiveView === "utf8"}>
                                        <label class="btn btn-outline-primary" for="raw-data-btn-utf8">UTF-8</label>

                                        <input value="hex" onchange={changeRawDataView} type="radio" class="btn-check" name="rawviewbtnradio" id="raw-data-btn-hex" autocomplete="off" checked={rawDataActiveView === "hex"}>
                                        <label class="btn btn-outline-primary" for="raw-data-btn-hex">Hex</label>
                                    </div>
                                    <a class="ms-auto" href="/">Generate script</a>
                                </div>
                                <hr>
                                <div class="vstack gap-3 mt-3">
                                    {#each Object.entries(rawFlowData.raw) as [i, chunk]}
                                        {@const byteArray = Uint8Array.from(atob(chunk.data), c => c.charCodeAt(0))}
                                        {#if rawDataActiveView === "utf8"}
                                            <pre class="p-2 {chunk.server_to_client === "0" ? "bg-danger" : ""}{chunk.server_to_client === "1" ? "bg-success" : ""}">{new TextDecoder().decode(byteArray)}</pre>
                                        {:else if rawDataActiveView === "hex"}
                                            <pre class="p-2 {chunk.server_to_client === "0" ? "bg-danger" : ""}{chunk.server_to_client === "1" ? "bg-success" : ""}"><HexDumpViewer sha256={i} blob={byteArray} /></pre>
                                        {/if}
                                    {/each}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {/if}
        {/await}
    </div>
{/await}