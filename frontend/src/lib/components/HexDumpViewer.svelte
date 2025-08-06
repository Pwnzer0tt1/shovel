<script lang="ts">
	let { sha256, blob }: { sha256: string, blob: Uint8Array } = $props();

    let offset: string[] = [];
    let hex: string[] = [];
    let text: string[] = [];

    blob.forEach((b, i) => {
        if (i % 16 === 0) {
            offset.push(i.toString(16).padStart(8, "0").toUpperCase());
        }

        hex.push(b.toString(16).padStart(2, "0").toUpperCase());
        text.push((b >= 0x20 && b < 0x7f) ? String.fromCharCode(b) : ".");
    });

    let startIndex: number | undefined = undefined;
    let endIndex: number | undefined = undefined;
    let shiftPressed = false;

    function shiftDown(e: KeyboardEvent) {
        if (e.target) {
            let el = e.target as HTMLElement;
            if (el.tagName !== "INPUT" && !e.repeat && !e.ctrlKey) {
                shiftPressed = e.shiftKey;
            }
        }
    }
    function shiftUp(e: KeyboardEvent) {
        if (e.target) {
            let el = e.target as HTMLElement;
            if (el.tagName !== "INPUT" && !e.repeat && !e.ctrlKey) {
                shiftPressed = e.shiftKey;
            }
        }
    }

    function overCell(e: any) {
        const elIndex = Number(e.currentTarget.getAttribute("data-index"));
        const hexCells = document.getElementsByClassName(`${sha256}-hex`) as HTMLCollectionOf<HTMLDivElement>;
        const textCells = document.getElementsByClassName(`${sha256}-text`) as HTMLCollectionOf<HTMLDivElement>;

        for (let index = 0; index < blob.length; index++) {
            let hexEl = hexCells.item(index);
            let textEl = textCells.item(index);

            if (hexEl === null || textEl === null) {
                continue;
            }

            if (index === startIndex || index === endIndex) {
                continue;
            }

            let isIncluded = false;
            if (startIndex !== undefined && endIndex === undefined) {
                if (elIndex > startIndex && index > startIndex && index <= elIndex) {    
                    hexEl.style.backgroundColor = "#7e9ca6";
                    textEl.style.backgroundColor = "#7e9ca6";
                    isIncluded = true;
                }
                else if (index >= elIndex && index < startIndex) {
                    hexEl.style.backgroundColor = "#7e9ca6";
                    textEl.style.backgroundColor = "#7e9ca6";
                    isIncluded = true;
                }
            }
            else if (startIndex === undefined && endIndex !== undefined) {
                if (elIndex > endIndex && index > endIndex && index <= elIndex) {    
                    hexEl.style.backgroundColor = "#7e9ca6";
                    textEl.style.backgroundColor = "#7e9ca6";
                    isIncluded = true;
                }
                else if (index >= elIndex && index < endIndex) {
                    hexEl.style.backgroundColor = "#7e9ca6";
                    textEl.style.backgroundColor = "#7e9ca6";
                    isIncluded = true;
                }
            }
            else if (startIndex !== undefined && endIndex !== undefined) {
                if (index > startIndex && index < endIndex) {    
                    hexEl.style.backgroundColor = "#7e9ca6";
                    textEl.style.backgroundColor = "#7e9ca6";
                    isIncluded = true;
                }
            }

            if (index === elIndex) {
                hexEl.style.backgroundColor = "#5a84a0";
                textEl.style.backgroundColor = "#5a84a0";
            }
            else if (!isIncluded) {
                hexEl.style.backgroundColor = "#353535";
                textEl.style.backgroundColor = "#353535";
            }
        }
    }

    function selectCell(e: any) {
        let elIndex = Number(e.currentTarget.getAttribute("data-index"));
        let hexCell = (document.getElementsByClassName(`${sha256}-hex`) as HTMLCollectionOf<HTMLDivElement>).item(elIndex);
        let textCell = (document.getElementsByClassName(`${sha256}-text`) as HTMLCollectionOf<HTMLDivElement>).item(elIndex);

        if (hexCell) {
            hexCell.style.backgroundColor = "#066bd6";
        }
        if (textCell) {
            textCell.style.backgroundColor = "#066bd6";
        }

        if (shiftPressed) {
            if (elIndex === startIndex) {
                startIndex = undefined;
            }
            else if (elIndex === endIndex) {
                endIndex = undefined;
            }
            else if (startIndex === undefined && endIndex === undefined) {
                startIndex = elIndex;
            }
            else if (startIndex === undefined && endIndex !== undefined) {
                if (elIndex > endIndex) {
                    startIndex = endIndex;
                    endIndex = elIndex;
                }
                else {
                    startIndex = elIndex;
                }
            }
            else if (startIndex !== undefined && endIndex !== undefined) {
                if (elIndex < startIndex) {
                    startIndex = elIndex;
                }
                else {
                    endIndex = elIndex;
                }
            }
            else if (startIndex !== undefined) {
                if (elIndex < startIndex) {
                    endIndex = startIndex;
                    startIndex = elIndex;
                }
                else {
                    endIndex = elIndex;
                }
            }
        }
        else {
            startIndex = undefined;    
            endIndex = undefined;
        }
    }

    function copyBytes(e: ClipboardEvent) {
        if (startIndex !== undefined && endIndex !== undefined) {
            e.clipboardData?.setData("text/plain", hex.slice(startIndex, endIndex + 1).join(" "));
        }
        
        e.preventDefault();
    }
</script>

<svelte:document onkeydown={shiftDown} onkeyup={shiftUp} />

<div class="d-flex gap-3 text-light" style="background-color: #353535;">
    <div style="background-color: #545454;">
        {#each offset as o}
            <div class="px-2" style="height: 24px;">{o}</div>
        {/each}
    </div>
    <div style="flex: 1 0 40%;" oncopy={copyBytes}>
        <div class="d-flex align-content-start flex-wrap">
            {#each Object.entries(hex) as [i, h]}
                <div data-index={i} onclick={selectCell} onmouseover={overCell} class="{sha256}-hex hex-cell text-center" role="none" onfocus={(e) => {}}>{h}</div>
            {/each}
        </div>
    </div>
    <div style="flex: 1 0 40%;" oncopy={copyBytes}>
        <div class="d-flex align-content-start flex-wrap">
            {#each Object.entries(text) as [i, t]}
                <div data-index={i} onclick={selectCell} onmouseover={overCell} class="{sha256}-text text-cell text-center" role="none" onfocus={(e) => {}}>{t}</div>
            {/each}
        </div>
    </div>
</div>

<style>
    .hex-cell, .text-cell {
        flex: 0 0 6.25%;
        height: 24px;
    }

    .hex-cell::selection, .text-cell::selection {
        color:white;
    }
</style>