<script lang="ts">
	import { onMount } from "svelte";

    let {
        text,
        ext,
        magic
    }: {
        text: string,
        ext: string,
        magic: string
    } = $props();

    let id = Math.floor(Math.random() * 10 ** 9)

    onMount(() => {
        const editor = ace.edit(`editor-${id}`);
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


<div id="editor-{id}" class="w-100 rounded-bottom">{text}</div>