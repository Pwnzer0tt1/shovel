import type { Flow, FlowsListFilters } from "./schema";


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