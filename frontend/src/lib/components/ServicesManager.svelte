<script lang="ts">
	import type { CtfConfig, AddService, DeleteService, EditRefreshRate } from "$lib/schema";
	import { selectedFlow, selectedPanel } from "$lib/state.svelte";
	import { superForm, type SuperValidated } from "sveltekit-superforms";
	import Toast from "./Toast.svelte";
	

    let { ctfConfig, addServiceForm, deleteServiceForm, editRefreshRateForm }: {
        ctfConfig: CtfConfig,
        addServiceForm: SuperValidated<AddService, any, AddService>,
        deleteServiceForm: SuperValidated<DeleteService, any, DeleteService>,
        editRefreshRateForm: SuperValidated<EditRefreshRate, any, EditRefreshRate>
    } = $props();

    const { form: form_addService, errors: errors_addService, constraints: constraints_addService, message: message_addService, enhance: enhance_addService } = superForm(addServiceForm);
    const { form: form_deleteService, errors: errors_deleteService, constraints: constraints_deleteService, message: message_deleteService, enhance: enhance_deleteService } = superForm(deleteServiceForm);
    const { form: form_editRefreshRate, errors: errors_editRefreshRate, constraints: constraints_editRefreshRate, message: message_editRefreshRate, enhance: enhance_editRefreshRate } = superForm(editRefreshRateForm);

    $form_addService.color = '#' + (Math.random() * 0xFFFFFF << 0).toString(16).padStart(6, '0');
    $form_editRefreshRate.refreshRate = ctfConfig.refresh_rate;

    let toast: Toast;

    $effect(() => {
        if (selectedFlow.flow) {
            $form_addService.serviceIP = selectedFlow.flow.dest_ipport.split(":")[0];
            $form_addService.ports = selectedFlow.flow.dest_ipport.split(":")[1];
        }
    });

    function editService(event: any) {
        const s = ctfConfig.services[event.currentTarget.value];
        $form_addService.name = event.currentTarget.value;
        $form_addService.color = s.color;
        $form_addService.serviceIP = s.ipports[0].split(":")[0];
        $form_addService.ports = s.ipports.map(v => v.split(":")[1]).join(", ");
    }

    function deleteService(event: any) {
        $form_deleteService.name = event.currentTarget.value;
    }
</script>

<div class="card shadow-lg">
    <div class="card-header hstack">
        <h5 class="modal-title flex-grow-1">Services Manager</h5>
        <button onclick={() => selectedPanel.view = null} type="button" class="btn-close " aria-label="Close"></button>
    </div>
    <div class="card-body ">
        <!-- Create/Edit service -->
        <form action="?/addService" method="POST" use:enhance_addService>
            <div class="row mb-4">
                <div class="col-md-8">
                    <label class="form-label" for="name">Service Name</label>
                    <input type="text" name="name" class="form-control {$errors_addService.name ? "is-invalid" : ""}" bind:value={$form_addService.name} {...$constraints_addService.name} placeholder="Web server" required>
                    <div class="invalid-feedback">{$errors_addService.name}</div>
                </div>
                <div class="col-md-4">
                    <label class="form-label" for="color">Color</label>
                    <input type="color" name="color" class="form-control {$errors_addService.color ? "is-invalid" : ""} form-control-color w-100 p-0 border-0" bind:value={$form_addService.color} {...$constraints_addService.color} required>
                    <div class="invalid-feedback">{$errors_addService.color}</div>
                </div>
            </div>
            <div class="row mb-4">
                <div class="col-md-8">
                    <label class="form-label" for="serviceIP">Service IP</label>
                    <input type="text" name="serviceIP" class="form-control {$errors_addService.serviceIP ? "is-invalid" : ""}" bind:value={$form_addService.serviceIP} {...$constraints_addService.serviceIP} placeholder="7.8.9.0" required>
                    <div class="invalid-feedback">{$errors_addService.serviceIP}</div>
                </div>
                <div class="col-md-4">
                    <label class="form-label" for="ports">Port</label>
                    <input type="text" name="ports" class="form-control {$errors_addService.ports ? "is-invalid" : ""}" bind:value={$form_addService.ports} {...$constraints_addService.ports} placeholder="80, 443, 8080" required>
                    <div class="invalid-feedback">{$errors_addService.ports}</div>
                </div>
            </div>
            <button class="btn btn-primary w-100 mb-0" type="submit">Add Service</button>
        </form>

        <hr>

        <!-- Application settings -->
        <div class="mb-3">
            <h6 class="text-muted mb-3">
                <i class="bi bi-gear-fill me-2"></i>
                Application Settings
            </h6>
            <label for="refreshRateInput" class="form-label">Flow list Auto-Refresh rate
                <span class="form-text">(seconds)</span>
            </label>
            <form action="?/editRefreshRate" method="POST" use:enhance_editRefreshRate>
                <div class="input-group">
                    <input type="number" name="refreshRate" class="form-control {$errors_editRefreshRate.refreshRate ? "is-invalid" : ""}" bind:value={$form_editRefreshRate.refreshRate} {...$constraints_editRefreshRate} required>
                    <button type="submit" class="btn btn-success">Save</button>
                </div>
                <div class="invalid-feedback">{$errors_editRefreshRate.refreshRate}</div>
            </form>
        </div>

        <hr>

        <!-- Services list -->
        <div class="configured-services-section">
            <h6 class="text-muted mb-3">
                <i class="bi bi-list-ul me-2"></i>
                Configured Services
            </h6>
            <div class="vstack gap-2">
                {#each Object.entries(ctfConfig.services) as [n, s]}
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
                                <span class="badge text-bg-secondary">{ipport}</span>
                            {/each}
                        </div>
                    </div>
                {/each}
            </div>
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
                <p>Are you sure you want to delete the service <strong>{$form_deleteService.name}</strong>?</p>
                <p class="fw-bold small">This action cannot be undone.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <form action="?/deleteService" method="POST" use:enhance_deleteService>
                    <input type="text" name="name" bind:value={$form_deleteService.name} {...$constraints_deleteService.name} hidden>
                    <button type="submit" class="btn btn-danger" data-bs-dismiss="modal">Delete</button>
                </form>                
            </div>
        </div>
    </div>
</div>

<!-- Toast -->
<Toast bind:this={toast} />