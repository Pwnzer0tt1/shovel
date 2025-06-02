'use strict'

class ServicesManager {
    constructor() {
        this.services = {}
        this.currentEditButton = null
        this.isLoaded = false
    }

    async loadServices() {
        try {
            const response = await fetch('/api/services')
            this.services = await response.json()
            this.isLoaded = true
            this.updateServicesSelect()
            this.updateServicesList()
            window.dispatchEvent(new CustomEvent('servicesLoaded'))
        } catch (error) {
            console.error('Error loading services:', error)
        }
    }

    async addService() {
        const nameInput = document.getElementById('serviceName')
        const portsInput = document.getElementById('servicePorts')
        const colorInput = document.getElementById('serviceColor')

        const name = nameInput.value.trim()
        const ports = portsInput.value.trim().split('\n').filter(p => p.trim())
        const color = colorInput.value

        if (!name || ports.length === 0) {
            this.showToast('Please fill in all fields', 'error')
            return
        }

        const defaultIp = document.getElementById('app').dataset.defaultIp || '10.60.2.1'
        const ipports = ports.map(port => `${defaultIp}:${port}`)

        const payload = {
            name: name,
            ipports: ipports,
            color: color
        }

        // If editing an existing service, include the old name
        if (this.currentEditButton) {
            const oldName = this.currentEditButton.dataset.serviceName
            if (oldName !== name) {
                payload.old_name = oldName
            }
        }

        try {
            const response = await fetch('/api/services', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })

            if (response.ok) {
                await this.loadServices()
                nameInput.value = ''
                portsInput.value = ''
                colorInput.value = this.generateRandomColor()
                this.resetAddButton()
                this.restoreEditButton()
                this.showToast('Service saved successfully!', 'success')
            } else {
                this.showToast('Error saving service', 'error')
            }
        } catch (error) {
            console.error('Error:', error)
            this.showToast('Error saving service', 'error')
        }
    }

    async deleteService(name) {
        try {
            const response = await fetch(`/api/services/${encodeURIComponent(name)}`, {
                method: 'DELETE'
            })

            if (response.ok) {
                await this.loadServices()
                this.showToast(`Service <strong>${name}</strong> deleted successfully`, 'danger');
            } else {
                alert('Error in deleting service')
            }
        } catch (error) {
            console.error('Connection Error:', error)
            alert('Connection Error')
        }
    }

    showDeleteConfirmModal(serviceName) {
        const modal = document.getElementById('deleteConfirmModal');
        const bsModal = new bootstrap.Modal(modal);

        document.getElementById('serviceNameToDelete').textContent = serviceName;

        const confirmBtn = document.getElementById('confirmDeleteBtn');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        newConfirmBtn.addEventListener('click', async () => {
            await this.deleteService(serviceName);
            bsModal.hide();
        });

        bsModal.show();
    }

    updateServicesSelect() {
        const select = document.getElementById('services-select')
        if (!select) return

        const currentValue = select.value

        const optionsToKeep = Array.from(select.children).slice(0, 2)
        select.innerHTML = ''
        optionsToKeep.forEach(opt => select.appendChild(opt))

        Object.entries(this.services).forEach(([name, serviceData]) => {
            const ipports = Array.isArray(serviceData) ? serviceData : serviceData.ipports
            const color = serviceData.color || '#007bff'

            const optgroup = document.createElement('optgroup')
            optgroup.label = name
            optgroup.dataset.ipports = ipports.join(' ')
            optgroup.dataset.color = color // Add color

            if (ipports.length > 1) {
                const allOption = document.createElement('option')
                allOption.value = ipports.join(',')
                allOption.textContent = `All (${name})`
                optgroup.appendChild(allOption)
            }

            ipports.forEach(ipport => {
                const option = document.createElement('option')
                option.value = ipport
                option.textContent = `${ipport} (${name})`
                optgroup.appendChild(option)
            })

            select.appendChild(optgroup)
        })

        select.value = currentValue
    }

    getServiceBadge(ipport) {
        if (!this.isLoaded) {
            return `<span class="service-badge" style="background-color: #6c757d">Loading...</span>`
        }
        for (const [name, serviceData] of Object.entries(this.services)) {
            const ipports = Array.isArray(serviceData) ? serviceData : serviceData.ipports
            if (ipports.includes(ipport)) {
                const color = serviceData.color || '#007bff'
                return `<span class="service-badge" style="background-color: ${color}">${name}</span>`
            }
        }
        return `<span class="service-badge" style="background-color: #6c757d">Unknown</span>`
    }

    getServiceColor(ipport) {
        if (!this.isLoaded) {
            return '#6c757d'
        }
        for (const [name, serviceData] of Object.entries(this.services)) {
            const ipports = Array.isArray(serviceData) ? serviceData : serviceData.ipports
            if (ipports.includes(ipport)) {
                return serviceData.color || '#007bff'
            }
        }
        return '#6c757d'
    }

    updateServicesList() {
        const container = document.getElementById('servicesList')
        if (!container) return

        container.innerHTML = '<h6>Configured Services:</h6>'

        if (Object.keys(this.services).length === 0) {
            container.innerHTML += '<p class="text-muted">No service configured</p>'
            return
        }

        Object.entries(this.services).forEach(([name, serviceData]) => {
            const ipports = Array.isArray(serviceData) ? serviceData : serviceData.ipports
            const color = serviceData.color || '#007bff'

            const serviceDiv = document.createElement('div')
            serviceDiv.className = 'card mb-2 border-0 shadow-sm'

            serviceDiv.innerHTML = `
            <div class="card-header bg-transparent text-white d-flex justify-content-between align-items-center">   
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="card-title mb-1 text-light d-flex align-items-center">
                            <span class="badge me-2" style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%;"></span>
                            ${name}
                        </h6>
                        <div class="text-muted small">
                            ${ipports.map(ip => `<span class="badge bg-light text-dark border me-1 mb-1">${ip}</span>`).join('')}
                        </div>
                    </div>
                    <div class="btn-group d-flex align-items-center">
                        <button class="btn btn-success btn-sm edit-service-btn" data-service-name="${name}" title="Edit service">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-fill" viewBox="0 0 16 16">
                                <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.5.5 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11z"/>
                            </svg>
                        </button>
                        <button class="btn btn-danger btn-sm delete-service-btn" data-service-name="${name}" title="Delete service">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3-fill" viewBox="0 0 16 16">
                                <path d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1H5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5m-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5M4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06m6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528M8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `
            container.appendChild(serviceDiv)
        })
    }

    generateRandomColor() {
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
            '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA',
            '#F1948A', '#85C1E9', '#F4D03F', '#AED6F1'
        ]
        return colors[Math.floor(Math.random() * colors.length)]
    }


    async editService(name) {
        const addBtn = document.getElementById('addServiceBtn')
        if (addBtn) {
            console.log("Changing add button text and classes for editing")
            addBtn.textContent = 'Confirm changes'
            addBtn.classList.remove('btn-primary')
            addBtn.classList.add('btn-success')
        }

        const serviceData = this.services[name]
        const ipports = Array.isArray(serviceData) ? serviceData : serviceData.ipports
        const color = serviceData.color || '#007bff'

        document.getElementById('serviceName').value = name
        document.getElementById('serviceColor').value = color

        const ports = ipports.map(ipport => {
            const parts = ipport.split(':')
            return parts[parts.length - 1]
        })

        document.getElementById('servicePorts').value = ports.join('\n')
    }

    resetAddButton() {
        const addBtn = document.getElementById('addServiceBtn')
        if (addBtn) {
            addBtn.textContent = 'Add Service'
            addBtn.classList.remove('btn-success')
            addBtn.classList.add('btn-primary')
        }
    }

    // Transform Edit button to X button, to cancel editing
    editBtnToX(button) {
        this.currentEditButton = button;

        button.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
                <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
            </svg>
        `;

        button.classList.remove('btn-success');
        button.classList.add('btn-warning');
        button.title = "Cancel editing";
    }

    // Reset the Edit button to its original state
    restoreEditButton() {
        if (this.currentEditButton) {
            this.currentEditButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-fill" viewBox="0 0 16 16">
                    <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.5.5 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11z"/>
                </svg>
            `;

            this.currentEditButton.classList.remove('btn-warning');
            this.currentEditButton.classList.add('btn-success');
            this.currentEditButton.title = "Edit service";

            this.currentEditButton = null;
        }
    }

    // Cancel editing and reset the form
    cancelEdit() {
        document.getElementById('serviceName').value = '';
        document.getElementById('servicePorts').value = '';
        this.resetAddButton();
        this.restoreEditButton();
    }

    // Show a custom Toast message
    showToast(message, type = 'success') {
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        const toastId = `toast-${Date.now()}`;
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.id = toastId;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toastEl);

        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 3000
        });
        toast.show();

        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
}

// Initialize the ServicesManager instance
const servicesManager = new ServicesManager()
window.servicesManager = servicesManager

document.addEventListener('DOMContentLoaded', () => {
    servicesManager.loadServices().then(() => {
        // Ensure flow list updates after services are loaded
        if (window.flowList) {
            window.flowList.update()
        }
    })
    const modal = document.getElementById('servicesModal')
    if (modal) {
        // Load services when the modal is shown
        modal.addEventListener('show.bs.modal', () => {
            servicesManager.loadServices()
        })

        // Reset status when the modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.getElementById('serviceName').value = ''
            document.getElementById('servicePorts').value = ''
            servicesManager.resetAddButton()
            servicesManager.restoreEditButton()
            
            servicesManager.loadServices().then(() => {
                window.location.reload()
            })
        })

        // Link the "Add Service" button to the addService method
        const addButton = modal.querySelector('#addServiceBtn')
        if (addButton) {
            addButton.addEventListener('click', () => servicesManager.addService())
        }

        // Use the modal's form submit event to prevent default submission
        const servicesList = document.getElementById('servicesList')
        if (servicesList) {
            servicesList.addEventListener('click', (e) => {
                // Delete service
                if (e.target.closest('.delete-service-btn')) {
                    const serviceName = e.target.closest('.delete-service-btn').dataset.serviceName
                    servicesManager.showDeleteConfirmModal(serviceName)
                }

                // Edit service
                else if (e.target.closest('.edit-service-btn')) {
                    const editBtn = e.target.closest('.edit-service-btn');
                    const serviceName = editBtn.dataset.serviceName;

                    // If the button is already in edit mode (has class 'btn-warning'), cancel the edit
                    if (editBtn.classList.contains('btn-warning')) {
                        servicesManager.cancelEdit();
                    } else {
                        servicesManager.editBtnToX(editBtn);
                        servicesManager.editService(serviceName);
                    }
                }
            })
        }
    }
})
