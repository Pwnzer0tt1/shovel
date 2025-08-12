<script lang="ts">
	import { ctfConfig, selectedPanel } from "$lib/state.svelte";
	import Toast from "./Toast.svelte";
	

    let toast: Toast;
    let serviceToDelete: string | undefined = $state(undefined);

    let name = $state("");
    let color = $state('#' + (Math.random() * 0xFFFFFF << 0).toString(16).padStart(6, '0'));
    let ipports: {
        ip: string,
        port: number
    }[] = $state([{ ip: "", port: 0 }]);

    async function addService(event: any) {
        const res = await fetch("/api/config/services", {
            method: "POST",
            body: JSON.stringify({
                name,
                color,
                ipports
            })
        });

        if (res.ok) {
            toast.show("success", `Service ${name} added`);
            ctfConfig.config = await res.json();
        }
        else {
            toast.show("danger", `Failed to add service ${name}`, await res.text());
        }
    }

    function editService(event: any) {
        const s = ctfConfig.config.services[event.currentTarget.value];    

        name = event.currentTarget.value;
        color = s.color;
        ipports = s.ipports;
    }

    function deleteService(event: any) {
        serviceToDelete = event.currentTarget.value;
    }

    async function confirmDeleteService(event: any) {
        const res = await fetch(`/api/config/services?name=${serviceToDelete}`, {
            method: "DELETE"
        });

        if (res.ok) {
            toast.show("warning", `Service ${serviceToDelete} deleted`);
            ctfConfig.config = await res.json();
        }
        else {
            toast.show("danger", `Failed to delete service ${serviceToDelete}`, await res.text())
        }
    }

    function addIpPort(e: any) {
        ipports.push({ ip: "", port: 0 });
    }

    function deleteIpPort(e: any) {
        if (ipports.length > 1) {
            ipports.splice(Number(e.currentTarget.getAttribute("data-index")), 1);
        }
    }
</script>

<div class="card shadow-lg h-100 overflow-auto">
    <div class="card-header hstack">
        <h5 class="modal-title flex-grow-1">Services Manager</h5>
        <button onclick={() => selectedPanel.view = undefined} type="button" class="btn-close " aria-label="Close"></button>
    </div>
    <div class="card-body">
        <!-- Create/Edit service -->
        <div class="row mb-4">
            <div class="col-md-8">
                <label class="form-label" for="name">Service Name</label>
                <input type="text" name="name" class="form-control" bind:value={name} placeholder="Web server" required>
            </div>
            <div class="col-md-4">
                <label class="form-label" for="color">Color</label>
                <input type="color" name="color" class="form-control form-control-color w-100 p-0 border-0" bind:value={color} required>
            </div>
        </div>
        <div class="d-flex align-content-start flex-wrap gap-2 mb-4">
            {#each Object.entries(ipports) as [index, ipp]}
                <div class="input-group" style="width: 25%;">
                    <input bind:value={ipp.ip} type="text" class="form-control" placeholder="IP" aria-label="IP" required>
                    <span class="input-group-text">:</span>
                    <input bind:value={ipp.port} type="number" min="0" max="65535" class="form-control" placeholder="Port" aria-label="Port" required>
                    <button onclick={deleteIpPort} data-index={index} class="btn btn-danger" title="Delete IP:port" aria-label="Delete IP:port"><i class="bi bi-dash-lg"></i></button>
                </div>
            {/each}
            <button onclick={addIpPort} class="btn btn-success" title="Add IP:port" aria-label="Add IP:port"><i class="bi bi-plus-lg"></i></button>
        </div>
        <button onclick={addService} class="btn btn-primary w-100">Add Service</button>

        <hr>

        <!-- Services list -->
        <h6 class="text-muted mb-3"><i class="bi bi-list-ul me-2"></i> Configured Services</h6>
        <div class="vstack gap-2">
            {#each Object.entries(ctfConfig.config.services) as [n, s]}
                <div class="card p-2">
                    <div class="hstack gap-2">
                        <h5><span class="badge" style="background-color: {s.color};">{n}</span></h5>
                        <div class="btn-group ms-auto" role="group" aria-label="Service actions">
                            <button onclick={editService} value={n} type="button" class="btn btn-success" aria-label="Edit service"><i class="bi bi-pencil-fill"></i></button>
                            <button onclick={deleteService} value={n} type="button" class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#deleteServiceModal" aria-label="Delete service"><i class="bi bi-trash3-fill"></i></button>
                        </div>
                    </div>
                    <div class="hstack gap-2">
                        {#each s.ipports as ipport}
                            <span class="badge text-bg-secondary">{ipport.ip}:{ipport.port}</span>
                        {/each}
                    </div>
                </div>
            {/each}
        </div>
    </div>
</div>

<!-- Delete service modal -->
<div class="modal fade" id="deleteServiceModal" tabindex="-1" aria-labelledby="Delete service modal" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-danger">
                <h1 class="modal-title fs-5 text-white">Delete confirmation</h1>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p>Are you sure you want to delete the service <strong>{serviceToDelete}</strong>?</p>
                <p class="fw-bold small">This action cannot be undone.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button onclick={confirmDeleteService} type="submit" class="btn btn-danger" data-bs-dismiss="modal">Delete</button>
            </div>
        </div>
    </div>
</div>

<!-- Toast -->
<Toast bind:this={toast} />