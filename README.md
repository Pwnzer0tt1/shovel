# Shovel

<!--
Copyright (C) 2023-2024  ANSSI
SPDX-License-Identifier: CC0-1.0
-->

Shovel is a web application that offers a graphical user interface to explore
[Suricata Extensible Event Format (EVE) outputs](https://docs.suricata.io/en/suricata-7.0.1/output/eve/eve-json-output.html).
Its primary focus is to help [Capture-the-Flag players](https://en.wikipedia.org/wiki/Capture_the_flag_(cybersecurity))
analyse network flows during stressful and time-limited attack-defense games such as
[FAUSTCTF](https://faustctf.net/), [ENOWARS](https://enowars.com/) or [ECSC](https://ecsc.eu/).
Shovel is developed in the context of
[ECSC Team France](https://ctftime.org/team/159269/) training.

![Shovel](./.github/demo.webp)

You might also want to have a look at these other awesome traffic analyser tools:

- https://github.com/secgroup/flower (first commit in 2018)
- https://github.com/eciavatta/caronte (first commit in 2020)
- https://github.com/OpenAttackDefenseTools/tulip (fork from flower in May 2022)

Compared to these traffic analyser tools, Shovel only relies on Suricata while
making opinionated choices for the frontend. This has a few nice implications:

- dissection of all application protocols supported by Suricata (HTTP2, modbus, SMB, DNS, etc),
- flows payloads and dissections are stored inside SQLite databases for fast queries,
- ingest can be a folder of pcaps for non-root CTF, or a live capture (less delay),
- tags are defined using Suricata rules (regex, libmagic match, HTTP header, etc),
- no heavy build tools needed, Shovel is easy to tweak.

Moreover, Shovel is batteries-included with some Suricata alert rules.

```
        ┌────────────────────────┐
device  │ Suricata with:         │   eve.db    ┌───────────────┐
or pcap │  - Eve SQLite plugin   ├────────────►│               │
───────►│  - TCP payloads plugin │ payload.db  │ Python webapp │
        │  - UDP payloads plugin ├────────────►│               │
        └────────────────────────┘             └────▲──────────┘
                                              .env  │
                                              ──────┘
```

## Getting started

### Services mapping, ticks and flag format configuration

Shovel is configured using environment variables.
Copy `example.env` to `.env` and update the optional configuration parameters.
You may update this file later and restart only the webapp.

Add the flag format in `suricata/rules/suricata.rules` if needed.
If you modify this file after starting Suricata, you may reload rules using
`pkill -USR2 suricata`.

### Network capture

Shovel currently implements 3 capture modes:

- **Mode A**: pcap replay (slower, for archives replay or rootless CTF).
- **Mode B**: capture interface (fast, requires root on vulnbox and in Docker).
- **Mode C**: PCAP-over-IP (fast, requires root on vulnbox).

Please prefer mode B or C to get the best latency between the game network and
Suricata.
Use mode A only if you are not root on the vulnbox and have access to pcap files
indirectly.

---

### Mode A - pcap capture mode (slower)

Place pcap files in a folder such as `input_pcaps/`.
If you are continuously adding new pcap, add `--pcap-file-continuous` to
Suricata command line.

A sample configuration can be found in `docker-compose-a.yml`.

If you don't want to use Docker, you may manually launch Suricata and the web
application using the two following commands:

```bash
./suricata/entrypoint.sh -r input_pcaps
(cd webapp && uvicorn --host 127.0.0.1 main:app)
```

> [!WARNING]
> Please note that restarting Suricata will cause all network capture files to
> be loaded again. It might add some delay before observing new flows.

> [!TIP]
> For a Microsoft Windows system, you may capture network traffic using the
> following command (3389 is RDP) inside a PowerShell console:
> ```powershell
> &'C:\Program Files\Wireshark\tshark.exe' -i game -w Z:\ -f "tcp port not 3389" -b duration:60
> ```

---

### Mode B - Live capture interface mode (fast)

This mode requires to have direct access to the game network interface.
This can be achieved by mirroring vulnbox traffic through a tunnel,
[see FAQ for more details](#how-to-setup-traffic-mirroring-using-openssh).
Here this device is named `tun5`.

A sample configuration can be found in `docker-compose-b.yml`.

If you don't want to use Docker, you may manually launch Suricata and the web
application using the two following commands:

```bash
sudo ./suricata/entrypoint.sh -i tun5
(cd webapp && uvicorn --host 127.0.0.1 main:app)
```

> [!WARNING]
> Please note that stopping Suricata will stop network capture.

You may also run `sudo tcpdump -n -i tun5 -G 30 -w trace-%Y-%m-%d_%H-%M-%S.pcap`
for archiving purposes.

---

### Mode C - Live capture using PCAP-over-IP (fast)

This mode requires to have access to a TCP listener exposing PCAP-over-IP.
Such server can be easily spawned using:

```bash
tcpdump -U --immediate-mode -ni game -s 65535 -w - not tcp port 22 | nc -l 57012
```

If you need to route PCAP-over-IP to multiple clients, you should consider using
[pcap-broker](https://github.com/fox-it/pcap-broker).
A sample configuration is given in `docker-compose-c.yml`.

If you don't want to use Docker, you may manually launch Suricata and the web
application using the two following commands:

```bash
PCAP_OVER_IP=pcap-broker:4242 ./suricata/entrypoint.sh -r /dev/stdin
(cd webapp && uvicorn --host 127.0.0.1 main:app)
```

> [!WARNING]
> Please note that stopping Suricata will stop network capture.

## Usage

### Starting Shovel

To start Shovel more easily, you can use the `./start.py` script to start the containers. Let's see in detail.

Use the flag `--build` (or `-b`) to start the containers. In addition, add one of the following to specify the capture
mode:

- `--mode-a` - **Mode A**, for pcap replay mode.
- `--mode-b` - **Mode B**, for live capture interface mode.
- `--mode-c` - **Mode C**, for live capture using PCAP-over-IP (default, if not specified).

---

If **Mode C** is used, you can customize the `.env` file with:

- `--target-ip TARGET_IP` (or `-ip`): specify the IP address of the vulnbox from which to capture traffic (MANDATORY).
- `--date START_DATE`: add the start date of the competition, using the ISO format (i.e.,
  `YYYY-MM-DDThh:mm+ZZ:zz`). If the timezone is not specified, it will default to UTC+02:00 (CEST).

---

To stop Shovel containers, just run:

```bash
./start.py --down
```

### Customizing services

To setup the services mapping, you can edit the `.env` file by hand. In alternative, once Shovel is started you can
customize the configuration directly from the web interface.

Click on the settings icon in the top left corner to open the **Service Manager** modal. Here you can add:

- service name,
- port numbers (one or more, separated by commas or new lines),
- colour (helps to identify the service in the flow list).

After adding a service, you can also edit it by clicking on the pencil icon next to the service name.

> [!WARNING]
> Note that if Shovel is stopped and restarted with `--build`, the configuration in web interface will be
> lost.

### Auto Refresh

It has been implemented an auto-refresh feature that allows to automatically refresh the flow list with an interval
equal to the `tickLength` specified in the `.env` file.
After updating, the interface will scroll to the previously selected flow (if any).

It is possible to temporarily disable the auto-refresh by clicking on the Auto-Update button in the top left corner.

## FAQs

### Is Suricata `flow_id` really unique?

`flow_id` is derived from timestamp (ms scale) and current flow parameters (such
as source and destination ports and addresses). See source code:
<https://github.com/OISF/suricata/blob/suricata-6.0.13/src/flow.h#L680>.

---

### How to setup traffic mirroring using OpenSSH?

Most CTF uses OpenVPN or Wireguard for the "game" network interface on the vulnbox,
which means you can duplicate the traffic to an OpenSSH `tun` tunnel.
Using this method, Shovel can run on another machine in live capture mode.

> [!WARNING]
> If you need to clone a physical Ethernet interface such as `eth0`,
> you will need to use `-o Tunnel=ethernet -w 5:5` in the SSH command line to create a `tap`.

To achieve traffic mirroring, you may use these steps as reference:

1. Enable SSH tunneling in vulnbox OpenSSH server:
   ```
   echo -e 'PermitTunnel yes' | sudo tee -a /etc/ssh/sshd_config
   systemctl restart ssh
   ```
2. Create `tun5` tunnel from the local machine to the vulnbox and up `tun5` on vulnbox:
   ```
   sudo ip tuntap add tun5 mode tun user $USER
   ssh -w 5:5 root@10.20.9.6 ip link set tun5 up
   ```
3. Up `tun5` on the local machine and start `tcpdump` to create pcap files:
   ```
   sudo ip link set tun5 up
   sudo tcpdump -n -i tun5 -G 30 -Z root -w trace-%Y-%m-%d_%H-%M-%S.pcap
   ```
4. Mirror `game` traffic to `tun5` on the vulnbox.
   This can be done using Nftables netdev `dup` option on `ingress` and `egress`.

---

### How do I reload rules without restarting Suricata?

You can edit suricata rules in `suricata/rules/suricata.rules`, then reload the rules
using:

```bash
pkill -USR2 suricata
```
