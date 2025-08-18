<script lang="ts">
	import { ctfConfig } from "$lib/state.svelte";


    let { ipport, data, raw } = $props();

    let serviceName = $derived.by(() => {
        for (const [sn, s] of Object.entries(ctfConfig.config.services)) {
            if (s.ipports.map((v) => `${v.ip}:${v.port}`).includes(ipport)) {
                return sn;
            }
        }

        return "unknown";
    });

    $effect(() => {
        const editor = ace.edit("raw-replay-editor");
        editor.setOptions({
            readOnly: true,
            minLines: 10,
            maxLines: 30,
            fontSize: 14,
            customScrollbar: true
        });
        editor.setTheme("ace/theme/dracula");
        editor.session.setMode("ace/mode/python");
    });
</script>

<div id="raw-replay-editor" class="rounded-bottom">
#!/usr/bin/env python3
# Filename: replay-{serviceName}-{data.id}.py
import json
import os
import random

from pwn import *

"""
This file was generated from network capture towards {data.ip} ({data.proto}).
Corresponding flow id: {data.id}
Service: {serviceName}
"""

# Set logging level
context.log_level = "DEBUG"  # or INFO, WARNING, ERROR

# Load arguments
# EXTRA is an array of the flagids for current service and team
if len(sys.argv) &lt; 2:
    print(f'Usage: &#123;sys.argv[0]&#125; &lt;target&gt; [flag_id]')
    sys.exit(1)
HOST = sys.argv[1]
if len(sys.argv) &gt; 2:
    EXTRA = json.loads(bytes.fromhex(sys.argv[2]).decode())
else:
    EXTRA = []

# Connect to remote and run the actual exploit
# Timeout is important to prevent stall
r = remote(HOST, {data.port}, typ="{data.proto.toLowerCase()}", timeout=2)

# SNIPPET: Generate uniformly random strings of length `k`
# rand_choice = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# value = "".join(random.choices(rand_choice, k=16))

# FIXME: You should identify if a flag_id was used in the following
# payload. If it is the case, then you should loop using EXTRA.
# for flag_id in EXTRA:

{#each raw as raw_data}
    {#if raw_data.server_to_client === "0"}
        {#if raw_data.data && raw_data.data[raw_data.data.length - 1] == 10}
r.sendline({raw_data.data.slice(0, -1)})
        {:else}
r.send({raw_data.data})
        {/if}
    {:else}
data = r.recvuntil({raw_data.data.slice(-16)})
    {/if}
{/each}

# Use the following to capture all remaining bytes:
# data = r.recvall(timeout=5)
# print(data, flush=True)

r.close()
</div>