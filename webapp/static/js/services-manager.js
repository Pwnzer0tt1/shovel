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
        const ipPortsText = document.getElementById('serviceIpPorts').value.trim()
        
        if (!name) {
            alert('Insert a service name')
            return
        }

        const ipports = ipPortsText.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)

        try {
            const response = await fetch('/api/services', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, ipports})
            })

            if (response.ok) {
                document.getElementById('serviceName').value = ''
                document.getElementById('serviceIpPorts').value = ''
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
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="card-title mb-1 text-primary">${name}</h6>
                        <div class="text-muted small">
                            ${ipports.map(ip => `<span class="badge bg-light text-dark border me-1 mb-1">${ip}</span>`).join('')}
                        </div>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-outline-primary btn-sm edit-service-btn" data-service-name="${name}" title="Modify service">
                            <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                                <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708L10.5 8.207l-3-3L12.146.146ZM11.207 9l-3-3-6.903 6.903a.5.5 0 0 0-.115.1l-1.85 4.26a.5.5 0 0 0 .649.649l4.26-1.85a.5.5 0 0 0 .1-.115L11.207 9Z"/>
                            </svg>
                        </button>
                        <button class="btn btn-outline-danger btn-sm delete-service-btn" data-service-name="${name}" title="Delete service">
                            <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                                <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84L14.162 3.5H15.5a.5.5 0 0 0 0-1h-1.004a.58.58 0 0 0-.01 0H11Zm1.228 1-.857 10.66a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.29 3.5h8.42Zm-8.728 3a.5.5 0 0 1 .5.5v5a.5.5 0 0 1-1 0v-5a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v5a.5.5 0 0 1-1 0v-5a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v5a.5.5 0 0 0 1 0v-5Z"/>
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
        document.getElementById('serviceName').value = name
        document.getElementById('serviceIpPorts').value = this.services[name].join('\n')
    }
}

// Inizializza il manager dei servizi
const servicesManager = new ServicesManager()

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('servicesModal')
    if (modal) {
        // Carica servizi quando si apre la modale
        modal.addEventListener('show.bs.modal', () => {
            servicesManager.loadServices()
        })
        
        // Collega il bottone Aggiungi/Modifica
        const addButton = modal.querySelector('.btn-primary')
        if (addButton) {
            addButton.addEventListener('click', () => servicesManager.addService())
        }
        
        // Usa delegazione eventi per i bottoni (creati dinamicamente)
        const servicesList = document.getElementById('servicesList')
        if (servicesList) {
            servicesList.addEventListener('click', (e) => {
                // Bottone elimina
                if (e.target.closest('.delete-service-btn')) {
                    const serviceName = e.target.closest('.delete-service-btn').dataset.serviceName
                    servicesManager.deleteService(serviceName)
                }
                // Bottone modifica
                else if (e.target.closest('.edit-service-btn')) {
                    const serviceName = e.target.closest('.edit-service-btn').dataset.serviceName
                    servicesManager.editService(serviceName)
                }
            })
        }
    }
})