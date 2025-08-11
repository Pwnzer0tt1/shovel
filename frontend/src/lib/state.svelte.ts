import type { CtfConfig, Flow, Flows, FlowsListFilters } from "./schema";


export const selectedFlow: { 
    flow: Flow | undefined,
    flowIndex: number
} = $state({
    flow: undefined,
    flowIndex: -1
});

export const selectedPanel: {
    view: "ServicesManager" | "Settings" | "Stats" | undefined
} = $state({
    view: undefined
});

export const tickInfo: {
    tickNumber: number
} = $state({
    tickNumber: 0
});

export const flowsFilters: FlowsListFilters = $state({ ts_to: String(1e16), tags_require: [], tags_deny: [] });

export const ctfConfig: {
    config: CtfConfig,
    autoUpdate: boolean,
    ctfEnded: boolean,
    hideSideBar: boolean
} = $state({
    config: {
        start_date: new Date().toISOString(),
        end_date: new Date().toISOString(),
        tick_length: 120,
        refresh_rate: 60,
        services: {}
    },
    autoUpdate: true,
    ctfEnded: false,
    hideSideBar: false
});

export const flows: {
    flows: Flows
} = $state({
    flows: []
});