<script lang="ts">
	import { onMount } from "svelte";

    let {
        text,
        ext,
        magic,
        sha256
    }: {
        text: string,
        ext: string,
        magic: string,
        sha256: string
    } = $props();

    onMount(() => {
        const editor = ace.edit(`editor-${sha256}`);
        editor.setOptions({
            readOnly: true,
            minLines: 10,
            maxLines: 60,
            fontSize: 14,
        });
        editor.setTheme("ace/theme/dracula");


        switch (ext) {
            case "html":
                editor.session.setMode("ace/mode/html");
                break;
            default:
                editor.session.setMode("ace/mode/text");
                break;
        }
    });
</script>


<div id="editor-{sha256}" class="w-100 rounded-bottom">{text}</div>