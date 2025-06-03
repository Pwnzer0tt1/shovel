#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import re
from datetime import datetime

ENV_FILE = ".env"
COMPOSE_FILES = {
    "A": "docker-compose-a.yml",
    "B": "docker-compose-b.yml",
    "C": "docker-compose-c.yml"
}


def write_env(start_date, target_ip, tick_length, refresh_rate):
    if not os.path.exists(ENV_FILE):
        print(f"[+] Warning: {ENV_FILE} file not found. Creating new file.")
        with open(ENV_FILE, "w") as f:
            f.write("")
    else:
        print(f"[+] Updating {ENV_FILE} file.")

    with open(ENV_FILE, "w") as f:
        content = ""

        # Ensure date has timezone information
        if not ('+' in start_date or '-' in start_date[10:]):
            formatted_date = f"{start_date}+02:00"
        else:
            formatted_date = start_date

        content += f"CTF_START_DATE={formatted_date}\n"
        content += f"TICK_LENGTH={tick_length}\n"
        content += f"TARGET_IP={target_ip}\n"
        content += f"REFRESH_RATE={refresh_rate}\n"

        f.write(content)

    print(f"     > Written CTF_START_DATE to {formatted_date} in {ENV_FILE}")
    print(f"     > Written TARGET_IP to {target_ip} in {ENV_FILE}")
    print(f"     > Written TICK_LENGTH to {tick_length} in {ENV_FILE}")
    print(f"     > Written REFRESH_RATE to {refresh_rate} in {ENV_FILE}")

    return


def validate_date_format(date_str):
    """Validate the date string to be written in the correct format"""
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


def update_compose(target_ip, key):
    """Update target IP and SSH key in docker-compose-c.yml"""
    compose_file = "docker-compose-c.yml"

    supported_algorithms = ["rsa", "ed25519", "ecdsa", "dsa"]
    if key.lower() not in [alg.lower() for alg in supported_algorithms]:
        print(f"[-] Error: Unsupported SSH key algorithm: {key}")
        print(f"    Supported algorithms are: {', '.join(supported_algorithms)}")
        sys.exit(1)

    if not os.path.exists(compose_file):
        print(f"Warning: {compose_file} file not found. Cannot update target IP.")
        return

    with open(compose_file, "r") as f:
        content = f.read()

    # Replace the Target IP
    ip_pattern = r"ssh root@[\d\.:]+ -oStrictHostKeyChecking=no"
    ip_replacement = f"ssh root@{target_ip} -oStrictHostKeyChecking=no"

    if re.search(ip_pattern, content):
        modified_content = re.sub(ip_pattern, ip_replacement, content)
        print(f"     > Updated SSH target IP to {target_ip} in {compose_file}")
    else:
        print(f"[-] Warning: Could not find SSH command pattern in {compose_file}")
        sys.exit(1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Replace the SSH key path
    key_pattern = r"~/.ssh/id_[a-zA-Z0-9_]+:/root/.ssh/id_[a-zA-Z0-9_]+:ro"
    key_replacement = f"~/.ssh/id_{key}:/root/.ssh/id_{key}:ro"

    if re.search(key_pattern, modified_content):
        modified_content = re.sub(key_pattern, key_replacement, modified_content)
        print(f"     > Updated SSH key path to use algorithm: {key}")
    else:
        print(f"[-] Warning: Could not find SSH key pattern in {compose_file}")
        sys.exit(1)

    with open(compose_file, "w") as f:
        f.write(modified_content)


def compose_down(compose_file):
    """Stop and remove containers defined in the specified docker-compose file"""
    cmd = ["docker", "compose", "-f", compose_file, "down"]
    print(f"[+] Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\n[+] Containers successfully stopped!\n")


def compose_up(compose_file, build):
    """Start containers defined in the specified docker-compose file"""
    cmd = ["docker", "compose", "-f", compose_file, "up", "-d"]
    if build:
        cmd.append("--build")

    print(f"[+] Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\n[+] Containers successfully started!\n")


def clear_suricata():
    """Clean the Suricata output directory"""
    cmd = "sudo rm -rf ./suricata/output/*"

    subprocess.run(cmd, check=True, shell=True)
    print(f"[+] Cleaning Suricata output directory...")
    print(f"    Suricata output directory cleaned successfully!")


def main():
    parser = argparse.ArgumentParser(description="Start Shovel using the specified mode")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--mode-a", action="store_true", help="Start in mode A (pcap replay)")
    mode_group.add_argument("--mode-b", action="store_true", help="Start in mode B (capture interface)")
    mode_group.add_argument("--mode-c", action="store_true", help="Start in mode C (PCAP-over-IP, default)")

    parser.add_argument("--down", dest="down", action="store_true", help="Stop containers listed in docker-compose")
    parser.add_argument("--build", "-b", dest="build", action="store_true", help="Rebuild images before starting them")
    parser.add_argument("--clear", "-c", dest="clear", action="store_true", help="Rebuild images before starting them")

    parser.add_argument("--date", dest="start_date",
                        help="Specify CTF start date (format: YYYY-MM-DDThh:mm+ZZ:zz, timezone +02:00 added if not specified)")
    parser.add_argument("--target-ip", "-ip", dest="target_ip", help="Specify target machine IP address (for mode C)")
    parser.add_argument("--refresh-rate", "-r", dest="refresh_rate", help="Specify refresh rate (in seconds)")
    parser.add_argument("--tick-length", "-t", dest="tick_length", help="Specify tick length (in seconds)")
    parser.add_argument("--key", "-k", dest="key", help="Specify algorithm for SSH key exchange (default: ed25519)")

    args = parser.parse_args()

    # Mode C as default if no mode is specified
    use_mode_c = not (args.mode_a or args.mode_b) or args.mode_c

    # Select the appropriate docker-compose file based on the mode
    compose_file = ""
    if args.mode_a:
        compose_file = COMPOSE_FILES["A"]
        print("[+] Starting in mode A (pcap replay)...")
    elif args.mode_b:
        compose_file = COMPOSE_FILES["B"]
        print("[+] Starting in mode B (capture interface)...")
    elif use_mode_c:
        compose_file = COMPOSE_FILES["C"]

        # If --down or --build is specified, stop the containers first
    if args.down or args.build:
        if os.path.exists(ENV_FILE): compose_down(compose_file)
        if args.down and not args.build:
            sys.exit(0)
    elif args.clear:
        if os.path.exists(ENV_FILE): compose_down(compose_file)
        clear_suricata()
        sys.exit(0)
    else:
        print("[-] No relevant action specified (down, build, clear). Use -h for help.")
        sys.exit(1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if args.mode_a:
        print("[+] Starting in mode A (pcap replay)...")
    elif args.mode_b:
        print("[+] Starting in mode B (capture interface)...")
    elif use_mode_c:
        print("[+] Starting in mode C (PCAP-over-IP)...")

        if not args.target_ip:
            print("[-] No target IP specified for mode C. Please provide --target-ip (or -ip) option.")
            sys.exit(1)

        # Validate start date format if provided
        if args.start_date and not validate_date_format(args.start_date):
            print(f"[-] Invalid start date format: {args.start_date}")
            print("    Please use ISO format: YYYY-MM-DDThh:mm (e.g. 2025-06-01T17:30)")
            print("    Timezone +02:00 will be added automatically if not specified")
            sys.exit(1)

        if not args.tick_length:
            print("[-] No tick length specified. Please provide --tick-length (or -t) option.")
            sys.exit(1)

        if not args.refresh_rate:
            print("[-] No refresh rate specified. Please provide --refresh-rate (or -r) option.")
            sys.exit(1)

        if not args.key:
            print("[-] No SSH key exchange algorithm specified.")
            sys.exit(1)

        # If target IP and date are specified, update '.env' and 'docker-compose-c.yml'
        write_env(
            start_date=args.start_date,
            target_ip=args.target_ip,
            tick_length=args.tick_length,
            refresh_rate=args.refresh_rate,
        )
        update_compose(
            target_ip=args.target_ip,
            key=args.key
        )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Create a new file 'services_config.json' empty
        json_config = "services_config.json"
        if not os.path.exists(json_config):
            print(f"[+] Creating empty {json_config} file.")
            with open(json_config, "w") as f:
                f.write("{}")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Start the containers using the selected docker-compose file
    compose_up(compose_file, args.build)

    print(f"\n[+] Shovel successfully started in mode {'A' if args.mode_a else 'B' if args.mode_b else 'C'}!")
    print(f"    Web interface is available at: http://127.0.0.1:8000")


if __name__ == "__main__":
    main()
