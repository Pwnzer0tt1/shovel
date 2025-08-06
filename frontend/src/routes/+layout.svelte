<script lang="ts">
    let { children } = $props();

    function toggleTheme(e: KeyboardEvent) {
        if (e.target) {
            let el = e.target as HTMLElement;
            if (el.tagName !== 'INPUT' && !e.repeat && !e.ctrlKey && e.key === 't') {
                let currentTheme = document.documentElement.getAttribute("data-bs-theme") || "light";
                currentTheme = currentTheme === 'light' ? 'dark' : 'light';
                document.documentElement.setAttribute('data-bs-theme', currentTheme);
                e.preventDefault();
            }
        }
    }
</script>

<svelte:document onkeydown={toggleTheme} />

{@render children()}