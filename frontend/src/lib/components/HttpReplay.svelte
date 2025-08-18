<script lang="ts">
	import { ctfConfig } from "$lib/state.svelte";


    let { flowId, ipport, data } = $props();

    let serviceName = $derived.by(() => {
        for (const [sn, s] of Object.entries(ctfConfig.config.services)) {
            if (s.ipports.map((v) => `${v.ip}:${v.port}`).includes(ipport)) {
                return sn;
            }
        }

        return "unknown";
    });

    let userAgent = $derived.by(() => {
        for (const header of data[0].request_headers) {
            if (header.name.toLowerCase() == "user-agent") {
                return header.value;
            }
        }

        return "CHANGE ME";
    });

    $effect(() => {
        const editor = ace.edit("http-replay-editor");
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

<div id="http-replay-editor" class="rounded-bottom">
#!/usr/bin/env python3
# Filename: replay-{ serviceName }-{ flowId }.py
import json
import logging
import random
import requests
import sys

"""
This file was generated from network capture towards { data[0].hostname }.
Corresponding flow id: { flowId }
Service: { serviceName }
"""

# Setup logger to log requests
logging.basicConfig(format='[%(levelname)s] %(message)s')
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)

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

# SNIPPET: Generate uniformly random strings of length `k`
# rand_choice = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# value = "".join(random.choices(rand_choice, k=16))

# FIXME: You should identify if a flagid was used in the following
# payload. If it is the case, then you should loop using EXTRA.
#for flag_id in EXTRA:

s = requests.Session()
s.headers["User-Agent"] = "{userAgent}"

{#each data as req}
# 

r = s.{req.http_method.toLowerCase()}(
    f"http://&#123;HOST&#125;:{req.http_port || "80"}{req.url}",
    {#if req.http_method === "POST"}
    data={req.rq_content},
    {/if}
    headers=&#123;
        {#each req.request_headers as header}
            {#if !["connection", "content-length", "host", "user-agent"].includes(header.name.toLowerCase())}
        "{header.name}": "{header.value}",
            {/if}
        {/each}
    &#125;,
    timeout=2, # prevent stall
)

if r.status_code != {req.status}:
    logging.error(f"Request returned wrong status code &#123;r.status_code&#125;, expected {req.status}")
print(r.text, flush=True)
{/each}
</div>