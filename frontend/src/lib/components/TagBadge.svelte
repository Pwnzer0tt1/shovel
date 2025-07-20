<script lang="ts">
    let { text, color, count }: { text: string, color?: string, count?: number } = $props();
</script>

<span class="badge text-bg-{color ||  "secondary"} mb-1 me-1 p-1-"> 
    {#if count}
        <span class="text-bg-dark bg-opcaity-75 rounded me-1 px-1">{count}</span>
    {/if}
    {text}
</span>