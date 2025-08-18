<script lang="ts">
    // Bootrstrap CSS
    import "bootstrap/dist/css/bootstrap.min.css";
    // Bottstrap Icons
    import "bootstrap-icons/font/bootstrap-icons.min.css";
    // Bootrstrap JS
    import scriptSrc from "bootstrap/dist/js/bootstrap.bundle.min.js?url";

    // Ace
    import "ace-builds/src-min-noconflict/ace.js";
    import "ace-builds/src-min-noconflict/theme-dracula.js";
	import "ace-builds/src-min-noconflict/mode-html.js";
	import "ace-builds/src-min-noconflict/mode-text.js";
	import "ace-builds/src-min-noconflict/mode-python.js";

    // Prettier
    import "prettier/standalone.js";


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

<svelte:head>
    <script src={scriptSrc}></script>
</svelte:head>

{@render children()}