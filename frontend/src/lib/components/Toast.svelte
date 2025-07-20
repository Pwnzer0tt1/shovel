<script lang="ts">
    let type = $state();
    let text = $state();

    let toast: HTMLDivElement;

    export function show(_type: 'success' | 'info' | 'warning' | 'danger' | 'none', _text: string) {
        type = _type;
        text = _text;

        const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);
        toastBootstrap.show();
    }
</script>

<div class="toast-container position-fixed bottom-0 end-0 p-3 rounded">
    <div bind:this={toast} class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="hstack gap-1 p-3 text-bg-{type}">
            {#if type === 'success'}
                <i class="bi bi-check-circle-fill"></i>
            {:else if type === 'info'}
                <i class="bi bi-info-circle-fill"></i>
            {:else if type === 'warning' || type === 'danger'}
                <i class="bi bi-exclamation-triangle-fill"></i>
            {/if}
            <strong>{text}</strong>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    </div>
</div>