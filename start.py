#!/usr/bin/env python3
import argparse
import argcomplete
import os
import subprocess
import sys
import re
from datetime import datetime


def update_env_file(target_ip=None, start_date=None):
    """Update the TARGET_IP and/or CTF_START_DATE in the .env file."""
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"Warning: {env_file} file not found. Creating new file.")
        with open(env_file, "w") as f:
            content = ""
            if start_date:
                # Ensure date has timezone information
                if not ('+' in start_date or '-' in start_date[10:]):
                    content += f"CTF_START_DATE={start_date}+02:00\n"
                else:
                    content += f"CTF_START_DATE={start_date}\n"
            if target_ip:
                content += f"TARGET_IP={target_ip}\n"
            f.write(content)
        return

    with open(env_file, "r") as f:
        content = f.read()

    # Update CTF_START_DATE if provided
    if start_date:
        # Ensure date has timezone information
        if not ('+' in start_date or '-' in start_date[10:]):
            formatted_date = f"{start_date}+02:00"
        else:
            formatted_date = start_date

        if "CTF_START_DATE=" in content:
            content = re.sub(r"CTF_START_DATE=.*", f"CTF_START_DATE={formatted_date}", content)
        else:
            content += f"\nCTF_START_DATE={formatted_date}\n"
        print(f"     > Updated CTF_START_DATE to {formatted_date} in {env_file}")

    # Update TARGET_IP if provided
    if target_ip:
        if "TARGET_IP=" in content:
            content = re.sub(r"TARGET_IP=.*", f"TARGET_IP={target_ip}", content)
        else:
            content += f"\nTARGET_IP={target_ip}\n"
        print(f"     > Updated TARGET_IP to {target_ip} in {env_file}")

    with open(env_file, "w") as f:
        f.write(content)


def validate_date_format(date_str):
    """Validate the date string to be written in the correct format."""
    try:
        # Check basic format first
        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(([+-]\d{2}:\d{2})|Z)?$", date_str):
            return False

        # If no timezone is specified, we'll add +02:00 later
        test_date = date_str
        if not ('+' in date_str or '-' in date_str[10:] or date_str.endswith('Z')):
            test_date = f"{date_str}+02:00"

        # Try to parse the date in ISO format
        datetime.fromisoformat(test_date.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def update_compose_c_file(target_ip):
    """Update the SSH target IP in the docker-compose-c.yml file."""
    compose_file = "docker-compose-c.yml"

    if not os.path.exists(compose_file):
        print(f"Warning: {compose_file} file not found. Cannot update SSH target IP.")
        return

    with open(compose_file, "r") as f:
        content = f.read()

    # Update SSH target IP in PCAP_COMMAND
    pattern = r"ssh root@[\d\.:]+ -oStrictHostKeyChecking=no"
    replacement = f"ssh root@{target_ip} -oStrictHostKeyChecking=no"

    if re.search(pattern, content):
        modified_content = re.sub(pattern, replacement, content)
        with open(compose_file, "w") as f:
            f.write(modified_content)
        print(f"     > Updated SSH target IP to {target_ip} in {compose_file}")
    else:
        print(f"Warning: Could not find SSH command pattern in {compose_file}")


def main():
    parser = argparse.ArgumentParser(description="Start Shovel using the specified mode")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--mode-a", action="store_true", help="Start in mode A (pcap replay)")
    mode_group.add_argument("--mode-b", action="store_true", help="Start in mode B (capture interface)")
    mode_group.add_argument("--mode-c", action="store_true", help="Start in mode C (PCAP-over-IP, default)")

    parser.add_argument("--down", action="store_true", help="Stop containers before starting them")
    parser.add_argument("--build", "-b", dest="build", action="store_true", help="Rebuild images before starting them")
    parser.add_argument("--target-ip", "-ip", dest="target_ip", help="Specify target machine IP address (for mode C)")
    parser.add_argument("--date", dest="start_date",
                        help="Specify CTF start date (format: YYYY-MM-DDThh:mm, timezone +02:00 added if not specified)")

    if 'argcomplete' in sys.modules:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # Validate start date format if provided
    if args.start_date and not validate_date_format(args.start_date):
        print(f"[-] Invalid start date format: {args.start_date}")
        print("    Please use ISO format: YYYY-MM-DDThh:mm (e.g. 2025-06-01T17:30)")
        print("    Timezone +02:00 will be added automatically if not specified")
        sys.exit(1)

    # Mode C as default if no mode is specified
    use_mode_c = not (args.mode_a or args.mode_b) or args.mode_c

    # Update CTF start date if specified (independent of mode)
    if args.start_date:
        print(f"[+] Updating CTF start date to: {args.start_date}")
        update_env_file(start_date=args.start_date)

    # Select the appropriate docker-compose file based on the mode
    if args.mode_a:
        compose_file = "docker-compose-a.yml"
        print("[+] Starting in mode A (pcap replay)...")
    elif args.mode_b:
        compose_file = "docker-compose-b.yml"
        print("[+] Starting in mode B (capture interface)...")
    elif use_mode_c:
        compose_file = "docker-compose-c.yml"

    # Build the docker compose command
    cmd = ["docker", "compose", "-f", compose_file]

    if args.down:
        down_cmd = cmd + ["down"]
        print(f"[+] Executing: {' '.join(down_cmd)}\n")
        subprocess.run(down_cmd, check=True)
    else:
        if use_mode_c:
            # If target IP is specified, update both the .env file and docker-compose-c.yml
            if args.target_ip:
                print("[+] Starting in mode C (PCAP-over-IP)...")
                update_env_file(target_ip=args.target_ip)
                update_compose_c_file(args.target_ip)
            else:
                print("[-] No target IP specified for mode C. Please provide --target-ip (or -ip) option.")
                sys.exit(1)

        if args.build:
            cmd.append("up")
            cmd.append("--build")
        else:
            cmd.append("up")

        cmd.append("-d")

        print(f"\n[+] Executing: {' '.join(cmd)}\n")
        subprocess.run(cmd, check=True)

        print(f"\n[+] Shovel successfully started in mode {'A' if args.mode_a else 'B' if args.mode_b else 'C'}!")
        print(f"    Web interface is available at: http://127.0.0.1:8000")


if __name__ == "__main__":
    main()
