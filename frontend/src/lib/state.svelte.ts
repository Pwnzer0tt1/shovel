import type { Flow } from "./schema";


export const selectedFlow: { 
    flow: Flow | undefined,
    flowIndex: number
} = $state({
    flow: undefined,
    flowIndex: -1
});