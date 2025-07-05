<script lang="ts">
	import { onMount } from 'svelte';

    let { children } = $props();

    onMount(() => {
        // Toggle on T key, ignore input fields or key repeat
        document.addEventListener('keydown', e => {
            if (e.target) {
                if (e.target.tagName !== 'INPUT' && !e.repeat && !e.ctrlKey && e.key === 't') {
                    let currentTheme = document.documentElement.getAttribute("data-bs-theme") || "light";
                    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-bs-theme', currentTheme);
                    e.preventDefault();
                }
            }
        });
    });
</script>

{@render children()}