import type { CtfConfig, Flow, FlowsListFilters } from "./schema";


export const selectedFlow: { 
    flow: Flow | undefined,
    flowIndex: number
} = $state({
    flow: undefined,
    flowIndex: -1
});

export const selectedPanel: {
    view: "ServicesManager" | undefined
} = $state({
    view: undefined
});

export const tickInfo: {
    tickNumber: number
} = $state({
    tickNumber: 0
});

export const flowsFilters: FlowsListFilters = $state({ ts_to: String(1e16) });

export const ctfConfig: {
    config: CtfConfig
} = $state({
    config: {
        start_date: "",
        tick_length: 120,
        refresh_rate: 60,
        services: {}
    }
});