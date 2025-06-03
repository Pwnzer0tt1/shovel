#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import re
import shutil
from datetime import datetime


def write_env(start_date, target_ip, tick_length, refresh_rate):
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"[+] Warning: {env_file} file not found. Creating new file.")
        os.makedirs(os.path.dirname(env_file))

    with open(env_file, "w") as f:
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

    print(f"     > Written CTF_START_DATE to {formatted_date} in {env_file}")
    print(f"     > Written TARGET_IP to {target_ip} in {env_file}")
    print(f"     > Written TICK_LENGTH to {tick_length} in {env_file}")
    print(f"     > Written REFRESH_RATE to {refresh_rate} in {env_file}")

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


def update_compose(target_ip):
    """Update the SSH target IP in the docker-compose-c.yml file"""
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
        cmd.append("build")

    print(f"[+] Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\n[+] Containers successfully started!\n")


def clear_suricata():
    """Clean the Suricata output directory by recursively removing all files and subdirectories"""
    suricata_output_path = "./suricata/output/"

    if os.path.exists(suricata_output_path):
        print(f"[+] Cleaning Suricata output directory: {suricata_output_path}")

        for filename in os.listdir(suricata_output_path):
            file_path = os.path.join(suricata_output_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
            except Exception as e:
                print(f"\n[-] Failed to delete {file_path}. Reason: {e}")

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

    args = parser.parse_args()

    # Mode C as default if no mode is specified
    use_mode_c = not (args.mode_a or args.mode_b) or args.mode_c

    # Select the appropriate docker-compose file based on the mode
    compose_file = "docker-compose-c.yml"
    if args.mode_a:
        compose_file = "docker-compose-a.yml"
        print("[+] Starting in mode A (pcap replay)...")
    elif args.mode_b:
        compose_file = "docker-compose-b.yml"
        print("[+] Starting in mode B (capture interface)...")
    elif use_mode_c:
        compose_file = "docker-compose-c.yml"

    # If --down or --build is specified, stop the containers first
    if args.down or args.build:
        compose_down(compose_file)
        if args.down and not args.build:
            sys.exit(0)
    elif args.clear:
        compose_down(compose_file)
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

        # If target IP and date are specified, update '.env' and 'docker-compose-c.yml'
        write_env(
            start_date=args.start_date,
            target_ip=args.target_ip,
            tick_length=args.tick_length,
            refresh_rate=args.refresh_rate
        )
        update_compose(args.target_ip)

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
