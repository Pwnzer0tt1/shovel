'use strict'

class ServicesManager {
    constructor() {
        this.services = {}
    }

    async loadServices() {
        try {
            const response = await fetch('/api/services')
            this.services = await response.json()
            this.updateServicesSelect()
            this.updateServicesList()
        } catch (error) {
            console.error('Error loading services:', error)
        }
    }

    async addService() {
        const name = document.getElementById('serviceName').value.trim()
        const ip = document.getElementById('serviceIP').value.trim()  // Fixed IP
        const portsText = document.getElementById('servicePorts').value.trim()

        if (!name) {
            alert('Insert a service name')
            return
        }

        // Process the ports input
        const ports = portsText.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .filter(port => /^\d+$/.test(port))

        if (ports.length === 0) {
            alert('Insert at least one valid port')
            return
        }

        const ipports = ports.map(port => `${ip}:${port}`)

        try {
            const response = await fetch('/api/services', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, ipports})
            })

            if (response.ok) {
                document.getElementById('serviceName').value = ''
                document.getElementById('servicePorts').value = ''
                await this.loadServices()
            } else {
                alert('Error in saving service')
            }
        } catch (error) {
            console.error('Connection Error:', error)
            alert('Connection Error')
        }
    }

    async deleteService(name) {
        if (!confirm(`Are you sure to delete this service: "${name}"?`)) return

        try {
            const response = await fetch(`/api/services/${encodeURIComponent(name)}`, {
                method: 'DELETE'
            })

            if (response.ok) {
                await this.loadServices()
            } else {
                alert('Error in deleting service')
            }
        } catch (error) {
            console.error('Connection Error:', error)
            alert('Connection Error')
        }
    }

    updateServicesSelect() {
        const select = document.getElementById('services-select')
        if (!select) return

        const currentValue = select.value

        const optionsToKeep = Array.from(select.children).slice(0, 2)
        select.innerHTML = ''
        optionsToKeep.forEach(opt => select.appendChild(opt))

        Object.entries(this.services).forEach(([name, ipports]) => {
            const optgroup = document.createElement('optgroup')
            optgroup.label = name
            optgroup.dataset.ipports = ipports.join(' ')

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

    updateServicesList() {
        const container = document.getElementById('servicesList')
        if (!container) return

        container.innerHTML = '<h6>Configured Services:</h6>'

        if (Object.keys(this.services).length === 0) {
            container.innerHTML += '<p class="text-muted">No service configured</p>'
            return
        }

        Object.entries(this.services).forEach(([name, ipports]) => {
            const serviceDiv = document.createElement('div')
            serviceDiv.className = 'card mb-2 border-0 shadow-sm'

            serviceDiv.innerHTML = `
            <div class="card-header bg-transparent text-white d-flex justify-content-between align-items-center">   
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="card-title mb-1 text-light">${name}</h6>
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

    editService(name) {
        const ipports = this.services[name]
        
        document.getElementById('serviceName').value = name
        
        const ports = ipports.map(ipport => {
            const parts = ipport.split(':')
            return parts[parts.length - 1]
        })
        
        document.getElementById('servicePorts').value = ports.join('\n')
    }
}

// Inizialize the ServicesManager instance
const servicesManager = new ServicesManager()

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('servicesModal')
    if (modal) {
        // Load services when the modal is shown
        modal.addEventListener('show.bs.modal', () => {
            servicesManager.loadServices()
        })

        // Link the "Add Service" button to the addService method
        const addButton = modal.querySelector('.btn-primary')
        if (addButton) {
            addButton.addEventListener('click', () => servicesManager.addService())
        }

        // Use the modal's form submit event to prevent default submission
        const servicesList = document.getElementById('servicesList')
        if (servicesList) {
            servicesList.addEventListener('click', (e) => {
                // deletion button
                if (e.target.closest('.delete-service-btn')) {
                    const serviceName = e.target.closest('.delete-service-btn').dataset.serviceName
                    servicesManager.deleteService(serviceName)
                }
                // modification button
                else if (e.target.closest('.edit-service-btn')) {
                    const serviceName = e.target.closest('.edit-service-btn').dataset.serviceName
                    servicesManager.editService(serviceName)
                }
            })
        }
    }
})