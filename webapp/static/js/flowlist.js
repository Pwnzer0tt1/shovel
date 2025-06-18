'use strict'

/*
 * Copyright (C) 2023-2024  ANSSI
 * SPDX-License-Identifier: GPL-2.0-or-later
 */

import Api from './api.js'

/**
 * Flow list sidebar
 *
 * Triggers 'locationchange' event on the window to update flow display.
 */
class FlowList {
    constructor() {
        this.apiClient = new Api()
        const url = new URL(document.location)
        this.selectedFlowId = url.searchParams.get('flow')

        this.autoUpdateBtn = document.getElementById('autoUpdateBtn')
        this.autoUpdateEnabled = localStorage.getItem('autoUpdateEnabled') !== null
            ? localStorage.getItem('autoUpdateEnabled') === 'true'
            : this.autoUpdateBtn.textContent.includes('ON')

        this.autoUpdateBtn.textContent = `Auto-Update: ${this.autoUpdateEnabled ? 'ON' : 'OFF'}`
        this.autoUpdateBtn.classList.add(this.autoUpdateEnabled ? 'btn-success' : 'btn-danger')
        this.initTickProgressBar()
    }


    async init() {
        // On left/right arrow keys, go to previous/next flow
        document.addEventListener('keydown', e => {
            if (e.target.tagName !== 'INPUT' && !e.ctrlKey && !e.altKey && !e.shiftKey) {
                switch (e.code) {
                    case 'ArrowLeft':
                        if (this.selectedFlowId) {
                            let prevElem = document.querySelector('#flow-list a.active')?.previousElementSibling
                            if (prevElem && prevElem.tagName.toLowerCase() === 'span') {
                                prevElem = prevElem.previousElementSibling
                            }
                            prevElem?.click()
                        } else {
                            document.querySelector('#flow-list a')?.click()
                        }
                        e.preventDefault()
                        break
                    case 'ArrowRight':
                        if (this.selectedFlowId) {
                            let nextElem = document.querySelector('#flow-list a.active')?.nextElementSibling
                            if (nextElem && nextElem.tagName.toLowerCase() === 'span') {
                                nextElem = nextElem.nextElementSibling
                            }
                            nextElem?.click()
                        } else {
                            document.querySelector('#flow-list a')?.click()
                        }
                        e.preventDefault()
                        break
                    case 'Escape':
                        // On Escape key, remove flow selection
                        if (this.selectedFlowId) {
                            this.selectedFlowId = null
                            window.history.pushState(null, '', window.location.pathname)
                            window.dispatchEvent(new Event('locationchange'))
                        }
                        e.preventDefault()
                        break
                }
            }
        })

        // On flow click, update URL and dispatch 'locationchange' event
        document.getElementById('flow-list').addEventListener('click', e => {
            if (!e.ctrlKey) {
                const newFlowId = e.target.closest('a')?.dataset?.flow
                if (newFlowId && this.selectedFlowId !== newFlowId) {
                    this.selectedFlowId = newFlowId
                    window.history.pushState(null, '', e.target.closest('a').href)
                    window.dispatchEvent(new Event('locationchange'))
                }
                e.preventDefault()
            }
        })

        // Infinite scroll: load more flows when loading indicator is seen
        this.observer = new window.IntersectionObserver((entries) => {
            entries.forEach(async e => {
                if (e.isIntersecting) {
                    const lastFlowTs = document.getElementById('flow-list').lastElementChild?.dataset.ts_start
                    if (lastFlowTs) {
                        // User sees loading indicator and flows list is not empty
                        await this.update(lastFlowTs)
                    }
                }
            })
        })
        this.observer.observe(document.getElementById('flow-list-loading-indicator'))

        // On browser history pop, dispatch 'locationchange' event, then update flows list
        window.addEventListener('popstate', e => {
            const url = new URL(document.location)
            const newFlowId = url.searchParams.get('flow')
            if (this.selectedFlowId !== newFlowId) {
                this.selectedFlowId = newFlowId
                window.dispatchEvent(new Event('locationchange'))
            }
            this.update()
        })

        // On 'locationchange' event, update active flow
        window.addEventListener('locationchange', _ => {
            this.updateActiveFlow(true)
        })

        // On services filter change, update URL then update flows list
        document.getElementById('services-select').addEventListener('change', e => {
            const url = new URL(document.location)
            url.searchParams.delete('service')
            e.target.value.split(',').forEach(s => {
                if (s) {
                    url.searchParams.append('service', s)
                }
            })
            window.history.pushState(null, '', url.href)
            this.update()
        })

        // Don't close filter dropdown on click inside
        document.getElementById('dropdown-filter').addEventListener('click', e => {
            e.stopPropagation()
        })

        // On time filter change, update URL then update flows list
        document.getElementById('filter-time-until').addEventListener('change', e => {
            const untilTick = Number(e.target.value)
            const url = new URL(document.location)
            if (untilTick) {
                url.searchParams.set('to', Math.floor(((untilTick + 1) * (this.tickLength || 1) + this.startTs)) * 1000000)
            } else {
                url.searchParams.delete('to')
                e.target.value = null
            }
            window.history.pushState(null, '', url.href)
            this.update()
        })

        // On protocol filter change, update URL then update flows list
        document.getElementById('filter-protocol').addEventListener('change', e => {
            const appProto = e.target.value
            const url = new URL(document.location)
            if (appProto) {
                url.searchParams.set('app_proto', appProto)
            } else {
                url.searchParams.delete('app_proto')
            }
            window.history.pushState(null, '', url.href)
            this.update()
        })

        // On glob search filter submit, update URL then update flows list
        document.getElementById('filter-search').addEventListener('keyup', e => {
            if (e.key !== 'Enter') {
                return
            }
            const search = e.target.value
            const url = new URL(document.location)
            if (search) {
                url.searchParams.set('search', search)
            } else {
                url.searchParams.delete('search')
            }
            window.history.pushState(null, '', url.href)
            this.update()
        })

        // On CTRL-MAJ-F key, search selection
        document.addEventListener('keyup', e => {
            if (e.target.tagName !== 'INPUT' && e.ctrlKey && e.shiftKey && !e.altKey && e.code === 'KeyF') {
                const sel = window.getSelection().toString()
                if (sel) {
                    const url = new URL(document.location)
                    url.searchParams.set('search', sel)
                    window.history.pushState(null, '', url.href)
                    this.update()
                }
                e.preventDefault()
            }
        })

        // On tags filter change, update URL then update flows list
        document.getElementById('filter-tag').addEventListener('click', e => {
            const tag = e.target.closest('a')?.dataset.tag
            if (tag) {
                const url = new URL(document.location)
                const requiredTags = url.searchParams.getAll('tag_require')
                const deniedTags = url.searchParams.getAll('tag_deny')
                if (requiredTags.includes(tag)) {
                    // Remove tag from required tags
                    url.searchParams.delete('tag_require')
                    requiredTags.forEach(t => {
                        if (t !== tag) {
                            url.searchParams.append('tag_require', t)
                        }
                    })
                    // If shift is pressed, then add to denied tags
                    if (e.shiftKey) {
                        url.searchParams.append('tag_deny', tag)
                    }
                } else if (deniedTags.includes(tag)) {
                    // Remove tag from denied tags
                    url.searchParams.delete('tag_deny')
                    deniedTags.forEach(t => {
                        if (t !== tag) {
                            url.searchParams.append('tag_deny', t)
                        }
                    })
                    // If shift is pressed, then add to required tags
                    if (e.shiftKey) {
                        url.searchParams.append('tag_require', tag)
                    }
                } else if (e.shiftKey) {
                    // Add tag to denied tags
                    url.searchParams.append('tag_deny', tag)
                } else {
                    // Add tag to required tags
                    url.searchParams.append('tag_require', tag)
                }
                window.history.pushState(null, '', url.href)
                this.update()
                e.preventDefault()
            }
        })

        // Apply current flow tick as time filter on click
        document.querySelector('#display-flow-tick > a').addEventListener('click', e => {
            const url = new URL(document.location)
            url.searchParams.set('to', e.currentTarget.dataset.ts)
            window.history.pushState(null, '', url.href)
            this.update()
        })

        // Handle auto update button click
        document.getElementById('autoUpdateBtn').addEventListener('click', e => {
            this.autoUpdateEnabled = !this.autoUpdateEnabled

            localStorage.setItem('autoUpdateEnabled', this.autoUpdateEnabled.toString())
            e.currentTarget.textContent = `Auto-Update: ${this.autoUpdateEnabled ? 'ON' : 'OFF'}`

            // Change colour of button
            if (this.autoUpdateEnabled && this.tickLength > 0) {
                e.currentTarget.classList.remove('btn-danger')
                e.currentTarget.classList.add('btn-success')

                // Start auto update
                this.updatePreservingScroll(false)
                this.autoUpdateInterval = setInterval(() => {
                    this.updatePreservingScroll(false)
                }, this.refreshRate * 1000)
            } else {
                e.currentTarget.classList.remove('btn-success')
                e.currentTarget.classList.add('btn-danger')

                if (this.autoUpdateInterval) {
                    clearInterval(this.autoUpdateInterval)
                    this.autoUpdateInterval = null
                }
            }
        })

        // Trigger initial flows list update
        const appData = document.getElementById('app').dataset
        this.startTs = Math.floor(Date.parse(appData.startDate) / 1000)
        this.tickLength = Number(appData.tickLength)
        this.refreshRate = Number(appData.refreshRate)
        this.tags = []
        this.update()

        if (this.tickLength > 0) {
            this.startTickProgress()
        }
    }

    /**
     * Pretty print delay
     * @param {Number} delay Delay in milliseconds
     * @returns Pretty string representation
     */
    pprintDelay(delay) {
        delay = delay / 1000
        if (delay > 1000) {
            delay = delay / 1000
            return `${delay.toPrecision(3)} s`
        } else {
            return `${delay.toPrecision(3)} ms`
        }
    }

    /**
     * Pretty print service IP address and port
     * @param {String} ipport
     * @returns Pretty string representation
     */
    pprintService(ipport) {
        const optgroup = document.querySelector(`select#services-select optgroup[data-ipports~='${ipport}']`)
        const name = optgroup?.label
        const color = optgroup?.dataset.color || '#6c757d'
        const port = ipport.split(':').slice(-1)

        if (window.servicesManager && window.servicesManager.services) {
            const serviceColor = window.servicesManager.getServiceColor(ipport)
            if (serviceColor !== '#6c757d') {
                if (name) {
                    return `<span class="service-badge" style="background-color: ${serviceColor}">${name}</span> (:${port})`
                } else {
                    return servicesManager.getServiceBadge(ipport)
                }
            }
        }

        if (name) {
            return `<span class="service-badge" style="background-color: ${color}">${name}</span> (:${port})`
        } else {
            return servicesManager.getServiceBadge(ipport)
        }
    }

    /**
     * Build tag element
     * @param {String} text Tag name
     * @param {String} color Tag color
     * @param {Number} count Tag count
     * @returns HTML element representing the tag
     */
    tagBadge(text, color, count) {
        const badge = document.createElement('span')
        badge.classList.add('badge', `text-bg-${color ?? 'none'}`, 'mb-1', 'me-1', 'p-1')
        badge.textContent = text
        if (count !== undefined) {
            const badgeCount = document.createElement('span')
            badgeCount.classList.add('text-bg-dark', 'bg-opacity-75', 'rounded', 'me-1', 'px-1')
            badgeCount.textContent = count
            badge.prepend(badgeCount)
        }
        return badge
    }

    /**
     * Set up the tick progress bar
     */
    initTickProgressBar() {
        this.tickProgressBar = null
        this.tickInfo = null
        this.tickTimer = null
        this.tickProgressInterval = null

        this.initTickElements()
    }

    initTickElements() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.assignTickElements())
        } else {
            this.assignTickElements()
        }
    }

    assignTickElements() {
        this.tickProgressBar = document.getElementById('tick-progress-bar')
        this.tickInfo = document.getElementById('tick-info')
        this.tickTimer = document.getElementById('tick-timer')
    }

    /**
     * Start the tick progress bar
     */
    startTickProgress() {
        if (!this.tickProgressBar) {
            this.assignTickElements()
        }

        if (!this.tickProgressBar || !this.tickInfo || !this.tickTimer) {
            setTimeout(() => this.startTickProgress(), 100)
            return
        }

        if (this.tickProgressInterval) {
            clearInterval(this.tickProgressInterval)
        }

        const updateProgress = () => {
            if (!this.tickLength || this.tickLength <= 0) return
            if (!this.tickProgressBar || !this.tickInfo || !this.tickTimer) return

            const now = Date.now() / 1000
            const currentTick = Math.floor((now - this.startTs) / this.tickLength)
            const tickStartTime = this.startTs + (currentTick * this.tickLength)
            const tickEndTime = tickStartTime + this.tickLength
            const progress = ((now - tickStartTime) / this.tickLength) * 100
            const remainingSeconds = Math.max(0, tickEndTime - now)

            // Update the progress bar width and aria attributes
            const clampedProgress = Math.min(100, Math.max(0, progress))
            this.tickProgressBar.style.width = `${clampedProgress}%`
            this.tickProgressBar.setAttribute('aria-valuenow', clampedProgress)

            // Update the tick info text
            this.tickInfo.textContent = `Tick ${currentTick}`

            // update the timer text
            const minutes = Math.floor(remainingSeconds / 60)
            const seconds = Math.floor(remainingSeconds % 60)
            this.tickTimer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`

            this.tickProgressBar.className = 'progress-bar progress-bar-striped progress-bar-animated'
            if (progress < 50) {
                this.tickProgressBar.classList.add('bg-success')
            } else if (progress < 80) {
                this.tickProgressBar.classList.add('bg-warning')
            } else {
                this.tickProgressBar.classList.add('bg-danger')
            }
        }

        updateProgress()
        this.tickProgressInterval = setInterval(updateProgress, 1000)
    }

    /**
     * Stop the tick progress bar
     */
    stopTickProgress() {
        if (this.tickProgressInterval) {
            clearInterval(this.tickProgressInterval)
            this.tickProgressInterval = null
        }

        if (this.tickProgressBar && this.tickInfo && this.tickTimer) {
            this.tickProgressBar.style.width = '0%'
            this.tickProgressBar.setAttribute('aria-valuenow', '0')
            this.tickProgressBar.className = 'progress-bar bg-success'
            this.tickInfo.textContent = 'Tick 0'
            this.tickTimer.textContent = '00:00'
        }
    }

    /**
     * Update protocols in filters dropdown
     */
    async updateProtocolFilter(appProto) {
        const protocolSelect = document.getElementById('filter-protocol')

        // Empty select options
        while (protocolSelect.lastChild) {
            protocolSelect.removeChild(protocolSelect.lastChild)
        }

        // Add protocols
        let option = document.createElement('option')
        option.value = ''
        option.textContent = 'All'
        protocolSelect.appendChild(option)
        option = document.createElement('option')
        option.value = 'raw'
        option.textContent = 'Raw'
        protocolSelect.appendChild(option)
        appProto.forEach((proto) => {
            const option = document.createElement('option')
            option.value = proto
            option.textContent = proto.toUpperCase()
            protocolSelect.appendChild(option)
        })

        // Update protocol filter select state
        const url = new URL(document.location)
        const current = url.searchParams.get('app_proto')
        protocolSelect.value = current ?? ''
        protocolSelect.classList.toggle('is-active', current !== null)
    }

    /**
     * Update tags in filters dropdown
     * @param {Array} tags All available tags
     * @param {Array} requiredTags Required tags in filter
     * @param {Array} deniedTags Denied tags in filter
     */
    updateTagFilter(tags, requiredTags, deniedTags) {
        // Empty dropdown content
        ['filter-tag-available', 'filter-tag-require', 'filter-tag-deny'].forEach(id => {
            const el = document.getElementById(id)
            el.parentElement.classList.add('d-none')
            while (el.lastChild) {
                el.removeChild(el.lastChild)
            }
        })

        // Create tags and append to corresponding section of dropdown
        tags.forEach(t => {
            const {tag, color} = t
            const badge = this.tagBadge(tag, color)
            const link = document.createElement('a')
            link.href = '#'
            link.dataset.tag = tag
            link.appendChild(badge)
            let destElement = document.getElementById('filter-tag-available')
            if (requiredTags.includes(tag)) {
                destElement = document.getElementById('filter-tag-require')
            } else if (deniedTags.includes(tag)) {
                destElement = document.getElementById('filter-tag-deny')
            }
            destElement.appendChild(link)
            destElement.parentElement.classList.remove('d-none')
        })
    }

    /**
     * Fill flows list
     */
    async fillFlowsList(flows, tags) {
        const flowList = document.getElementById('flow-list')
        flows.forEach((flow) => {
            const date = new Date(flow.ts_start / 1000)
            const startDate = new Intl.DateTimeFormat(
                undefined,
                {hour: 'numeric', minute: 'numeric', second: 'numeric', fractionalSecondDigits: 1}
            ).format(date)

            // Don't insert flow already in list
            // This happens when adding flows during infinite scroll
            if (flowList.querySelector(`a[data-flow="${flow.id}"]`)) {
                return
            }

            // Create tick element on new tick
            if (this.tickLength > 0) {
                const tick = Math.floor((flow.ts_start / 1000000 - this.startTs) / this.tickLength)
                if (tick !== this.lastTick) {
                    const tickEl = document.createElement('span')
                    tickEl.classList.add('list-group-item', 'sticky-top', 'pt-3', 'pb-1', 'px-2', 'border-0', 'border-bottom', 'bg-light-subtle', 'text-center', 'fw-semibold')
                    tickEl.textContent = `Tick ${tick}`
                    flowList.appendChild(tickEl)
                    this.lastTick = tick
                }
            }

            // Build URL
            const url = new URL(document.location)
            url.searchParams.set('flow', flow.id)

            // Build DOM elements
            const flowEl = document.createElement('a')
            flowEl.classList.add('list-group-item', 'list-group-item-action', 'py-1', 'px-2', 'lh-sm', 'border-0', 'border-bottom')
            flowEl.href = url.href
            flowEl.dataset.flow = flow.id
            flowEl.dataset.ts_start = flow.ts_start

            const flowInfoDiv = document.createElement('div')
            flowInfoDiv.classList.add('d-flex', 'justify-content-between', 'mb-1')
            const flowInfoDiv1 = document.createElement('small')
            flowInfoDiv1.innerHTML = this.pprintService(flow.dest_ipport)
            const flowInfoDiv2 = document.createElement('small')
            flowInfoDiv2.textContent = `${this.pprintDelay(flow.ts_end - flow.ts_start)}, ${startDate}`
            flowInfoDiv.appendChild(flowInfoDiv1)
            flowInfoDiv.appendChild(flowInfoDiv2)
            flowEl.appendChild(flowInfoDiv)

            // Use application protocol as first badge if defined
            const appProto = flow.app_proto?.replace('failed', 'raw') ?? 'raw'
            const badge = this.tagBadge(appProto.toUpperCase())
            flowEl.appendChild(badge)

            const flowTags = flow.tags?.split(',')
            tags.forEach(t => {
                const {tag, color} = t
                if (flowTags?.includes(tag)) {
                    const tagId = 'tag_' + tag.replace(/[^A-Za-z0-9]/g, '_')
                    const badge = this.tagBadge(tag, color, flow.flowints?.[tagId])
                    flowEl.appendChild(badge)
                }
            })

            flowList.appendChild(flowEl)
        })

        // Hide loading indicator if we are displaying less than 100 new flows
        document.getElementById('flow-list-loading-indicator').classList.toggle('d-none', flows.length < 99)

        // Refresh observer
        // This trigger the observer again if the loading indicator is still intersecting with the viewport
        this.observer.disconnect()
        this.observer.observe(document.getElementById('flow-list-loading-indicator'))
    }

    /**
     * Update highlighted flow in flows list
     */
    updateActiveFlow(scrollInto) {
        document.querySelector('#flow-list a.active')?.classList.remove('active')
        const linkElement = document.querySelector(`#flow-list a[data-flow="${this.selectedFlowId}"]`)
        linkElement?.classList.add('active')
        if (scrollInto) {
            linkElement?.scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'})
        }
    }

    /**
     * Update flowlist
     * If `fillTo` is given, then only append newly fetch flows
     */
    async update(fillTo) {
        const url = new URL(document.location)
        const fromTs = url.searchParams.get('from')
        const toTs = fillTo ?? url.searchParams.get('to')
        const services = url.searchParams.getAll('service')
        const filterAppProto = url.searchParams.get('app_proto')
        const filterSearch = url.searchParams.get('search')
        const filterTagsRequire = url.searchParams.getAll('tag_require')
        const filterTagsDeny = url.searchParams.getAll('tag_deny')

        if (!fillTo) {
            // Update search input
            const searchInput = document.getElementById('filter-search')
            searchInput.value = filterSearch ?? ''
            searchInput.classList.toggle('is-active', filterSearch !== null)

            // Update filter dropdown visual indicator
            document.querySelector('#dropdown-filter > button').classList.toggle('text-bg-purple', toTs || filterTagsRequire.length || filterTagsDeny.length || filterAppProto || filterSearch)

            // Update service filter select state
            document.getElementById('services-select').value = services.join(',')

            // Update time filter state
            if (toTs) {
                const toTick = (Number(toTs) / 1000000 - this.startTs) / (this.tickLength || 1) - 1
                document.getElementById('filter-time-until').value = toTick
            }
            document.getElementById('filter-time-until').classList.toggle('is-active', toTs)

            // Update tags filter before API response
            this.updateTagFilter(this.tags, filterTagsRequire, filterTagsDeny)

            // Empty flow list
            const flowList = document.getElementById('flow-list')
            while (flowList.lastChild) {
                flowList.removeChild(flowList.lastChild)
            }
            this.lastTick = null

            // Show loading indicator
            // As the list is empty, the infinite scroll callback won't be triggered
            document.getElementById('flow-list-loading-indicator').classList.remove('d-none')
        }

        // Fetch API and update
        const {flows, appProto, tags} = await this.apiClient.listFlows(
            fromTs ? Number(fromTs) : null,
            toTs ? Number(toTs) : null,
            services,
            filterAppProto,
            filterSearch,
            filterTagsRequire,
            filterTagsDeny
        )
        this.tags = tags
        await this.updateProtocolFilter(appProto)
        this.updateTagFilter(tags, filterTagsRequire, filterTagsDeny)
        await this.fillFlowsList(flows, tags)
        this.updateActiveFlow(!fillTo)
    }

    /**
     * Aggiorna la flowlist mantenendo la posizione di scroll
     */
    async updatePreservingScroll(fillTo) {
        const flowListEl = document.getElementById('flow-list')
        const prevScrollTop = flowListEl.scrollTop
        await this.update(fillTo)
        flowListEl.scrollTop = prevScrollTop
    }

}

const flowList = new FlowList()
window.flowList = flowList

const initFlowList = async () => {
    // Wait for services manager to be available
    if (window.servicesManager && !window.servicesManager.isLoaded) {
        await new Promise(resolve => {
            window.addEventListener('servicesLoaded', resolve, {once: true})
        })
    }

    await flowList.init()

    if (flowList.autoUpdateEnabled && flowList.tickLength > 0) {
        flowList.autoUpdateInterval = setInterval(() => {
            flowList.updatePreservingScroll(false)
        }, flowList.refreshRate * 1000)
    }
}

initFlowList()