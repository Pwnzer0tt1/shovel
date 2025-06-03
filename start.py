#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import re
from datetime import datetime
import shutil

ENV_FILE = ".env"
COMPOSE_FILES = {
    "A": "docker-compose-a.yml",
    "B": "docker-compose-b.yml",
    "C": "docker-compose-c.yml"
}


# Terminal colors and formatting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_banner():
    """Print a nice banner for the application"""
    terminal_width = shutil.get_terminal_size().columns
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                       SHOVEL - SURICATA                       ║
║           CTF Traffic Analysis Tool - by Pwnzer0tt1           ║
╚═══════════════════════════════════════════════════════════════╝
    """

    lines = banner.strip().split('\n')
    for line in lines:
        padding = (terminal_width - len(line)) // 2
        print(" " * max(0, padding) + Colors.CYAN + Colors.BOLD + line + Colors.END)
    print()


def print_separator(char="─", length=60):
    """Print a separator line"""
    print(Colors.BLUE + char * length + Colors.END)


def print_success(message):
    """Print success message with green color"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_info(message):
    """Print info message with blue color"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_warning(message):
    """Print warning message with yellow color"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_error(message):
    """Print error message with red color"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_progress(message):
    """Print progress message with cyan color"""
    print(f"{Colors.CYAN}▶ {message}{Colors.END}")


def prompt_styled(prompt_text, required=True, default=None):
    """Styled input prompt with validation"""
    if default:
        prompt_text += f" {Colors.YELLOW}(default: {default}){Colors.END}"
    prompt_text += f" {Colors.BOLD}→{Colors.END} "

    while True:
        try:
            user_input = input(prompt_text).strip()
            if not user_input and default:
                return default
            if user_input or not required:
                return user_input
            print_error("This field cannot be empty. Please try again.")
        except KeyboardInterrupt:
            print("\n")
            print_error("Operation cancelled by user.")
            sys.exit(1)


def show_mode_selection():
    """Display mode selection menu"""
    print_info("Available modes:")
    print(f"  {Colors.BOLD}A{Colors.END} - PCAP Replay Mode")
    print(f"  {Colors.BOLD}B{Colors.END} - Capture Interface Mode")
    print(f"  {Colors.BOLD}C{Colors.END} - PCAP-over-IP Mode (default)")
    print()


def prompt_for_missing_params(args, use_mode_c):
    """Prompt user for missing required parameters with styled interface"""

    now = datetime.now()
    example_minute = 30
    if now.minute < 30:
        example_hour = now.hour - 1 if now.hour > 0 else 23
        example_minute = 0
    elif now.minute >= 30:
        example_hour = now.hour
    example_date = f"{now.year}-{now.month:02d}-{now.day:02d}T{example_hour:02d}:{example_minute:02d}"

    if use_mode_c:
        print_separator()
        print(f"{Colors.BOLD}{Colors.CYAN}Configuration Setup for Mode C{Colors.END}")
        print_separator()

        # Target IP
        if not args.target_ip:
            print_info("Target IP Configuration")
            while True:
                target_ip = prompt_styled("Enter target IP address")
                if target_ip:
                    args.target_ip = target_ip
                    break
                print_error("Target IP cannot be empty. Please try again.")

        # Start date
        if not args.start_date:
            print()
            print_info("CTF Start Date Configuration")
            print_info(
                f"Format: {Colors.YELLOW}YYYY-MM-DDThh:mm{Colors.END} {Colors.BLUE}(e.g., {example_date}){Colors.END}")
            while True:
                start_date = prompt_styled("Enter CTF start date")
                if start_date and validate_date_format(start_date):
                    args.start_date = start_date
                    break
                elif start_date:
                    print_error("Invalid date format. Please use: YYYY-MM-DDThh:mm")
                else:
                    print_error("Start date cannot be empty. Please try again.")

        # Tick length
        if not args.tick_length:
            print()
            print_info("Tick Length Configuration")
            while True:
                tick_length = prompt_styled("Enter tick length (in seconds)")
                if tick_length and tick_length.isdigit():
                    args.tick_length = tick_length
                    break
                print_error("Tick length must be a positive number. Please try again.")

        # Refresh rate
        if not args.refresh_rate:
            print()
            print_info("Refresh Rate Configuration")
            while True:
                refresh_rate = prompt_styled("Enter refresh rate (in seconds)")
                if refresh_rate and refresh_rate.isdigit():
                    args.refresh_rate = refresh_rate
                    break
                print_error("Refresh rate must be a positive number. Please try again.")

        # SSH key algorithm
        if not args.key:
            print()
            print_info("SSH Key Algorithm Configuration")
            supported_algorithms = ["rsa", "ed25519", "ecdsa", "dsa"]
            print_info(f"Available algorithms: {Colors.YELLOW}{', '.join(supported_algorithms)}{Colors.END}")
            while True:
                key = prompt_styled("Enter SSH key algorithm", default="ed25519")
                if key.lower() in [alg.lower() for alg in supported_algorithms]:
                    args.key = key.lower()
                    break
                print_error(f"Unsupported algorithm. Choose from: {', '.join(supported_algorithms)}")

        print_separator()
        print_success("Configuration completed successfully!")
        print()


def write_env(start_date, target_ip, tick_length, refresh_rate):
    if not os.path.exists(ENV_FILE):
        print_warning(f"{ENV_FILE} file not found. Creating new file.")
        with open(ENV_FILE, "w") as f:
            f.write("")
    else:
        print_info(f"Updating {ENV_FILE} file.")

    with open(ENV_FILE, "w") as f:
        content = ""

        # Ensure date has timezone information
        if not ('+' in start_date or '-' in start_date[10:]):
            formatted_date = f"{start_date}+02:00"
        else:
            formatted_date = start_date

        content += f"CTF_START_DATE={formatted_date}\n"
        content += f"CTF_TICK_LENGTH={tick_length}\n"
        content += f"TARGET_IP={target_ip}\n"
        content += f"REFRESH_RATE={refresh_rate}\n"

        f.write(content)

    print_success(f"Environment variables written to {ENV_FILE}")
    print(f"  {Colors.CYAN}CTF_START_DATE{Colors.END} = {formatted_date}")
    print(f"  {Colors.CYAN}TARGET_IP{Colors.END} = {target_ip}")
    print(f"  {Colors.CYAN}CTF_TICK_LENGTH{Colors.END} = {tick_length}")
    print(f"  {Colors.CYAN}REFRESH_RATE{Colors.END} = {refresh_rate}")
    print()


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
        print_error(f"Unsupported SSH key algorithm: {key}")
        print(f"    Supported algorithms are: {', '.join(supported_algorithms)}")
        sys.exit(1)

    if not os.path.exists(compose_file):
        print_warning(f"{compose_file} file not found. Cannot update target IP.")
        return

    with open(compose_file, "r") as f:
        content = f.read()

    # Replace the Target IP
    ip_pattern = r"ssh root@[\d\.:]+ -oStrictHostKeyChecking=no"
    ip_replacement = f"ssh root@{target_ip} -oStrictHostKeyChecking=no"

    if re.search(ip_pattern, content):
        modified_content = re.sub(ip_pattern, ip_replacement, content)
        print_success(f"Updated SSH target IP to {target_ip} in {compose_file}")
    else:
        print_error(f"Could not find SSH command pattern in {compose_file}")
        sys.exit(1)

    # Replace the SSH key path
    key_pattern = r"~/.ssh/id_[a-zA-Z0-9_]+:/root/.ssh/id_[a-zA-Z0-9_]+:ro"
    key_replacement = f"~/.ssh/id_{key}:/root/.ssh/id_{key}:ro"

    if re.search(key_pattern, modified_content):
        modified_content = re.sub(key_pattern, key_replacement, modified_content)
        print_success(f"Updated SSH key path to use algorithm: {key}")
    else:
        print_error(f"Could not find SSH key pattern in {compose_file}")
        sys.exit(1)

    with open(compose_file, "w") as f:
        f.write(modified_content)


def compose_down(compose_file):
    """Stop and remove containers defined in the specified docker-compose file"""
    cmd = ["docker", "compose", "-f", compose_file, "down"]
    print_progress(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print_success("Containers successfully stopped!")
    print()


def compose_up(compose_file, build):
    """Start containers defined in the specified docker-compose file"""
    cmd = ["docker", "compose", "-f", compose_file, "up", "-d"]
    if build:
        cmd.append("--build")

    print_progress(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print_success("Containers successfully started!")
    print()


def clear_suricata():
    """Clean the Suricata output directory"""
    cmd = "sudo rm -rf ./suricata/output/*"

    subprocess.run(cmd, check=True, shell=True)
    print_progress("Cleaning Suricata output directory...")
    print_success("Suricata output directory cleaned successfully!")


def main():
    # Clear screen and show banner
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()

    parser = argparse.ArgumentParser(
        description="Start Shovel using the specified mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BOLD}Examples:{Colors.END}
  {Colors.CYAN}./start.py --build{Colors.END}                    # Start in mode C with build
  {Colors.CYAN}./start.py --mode-a{Colors.END}                   # Start in mode A
  {Colors.CYAN}./start.py --down{Colors.END}                     # Stop containers
  {Colors.CYAN}./start.py --clear{Colors.END}                    # Clean and stop
  {Colors.CYAN}./start.py --mode-c --target-ip 192.168.1.10{Colors.END}  # Start mode C with IP
        """
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--mode-a", action="store_true", help="Start in mode A (pcap replay)")
    mode_group.add_argument("--mode-b", action="store_true", help="Start in mode B (capture interface)")
    mode_group.add_argument("--mode-c", action="store_true", help="Start in mode C (PCAP-over-IP, default)")

    parser.add_argument("--down", dest="down", action="store_true", help="Stop containers listed in docker-compose")
    parser.add_argument("--build", "-b", dest="build", action="store_true", help="Rebuild images before starting them")
    parser.add_argument("--clear", "-c", dest="clear", action="store_true",
                        help="Clean Suricata output and stop containers")

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
        print_info("Starting in mode A (pcap replay)...")
    elif args.mode_b:
        compose_file = COMPOSE_FILES["B"]
        print_info("Starting in mode B (capture interface)...")
    elif use_mode_c:
        compose_file = COMPOSE_FILES["C"]

    # Handle special actions
    if args.down or args.build:
        if os.path.exists(ENV_FILE):
            compose_down(compose_file)
        if args.down and not args.build:
            print_success("Operation completed successfully!")
            sys.exit(0)
    elif args.clear:
        if os.path.exists(ENV_FILE):
            compose_down(compose_file)
        clear_suricata()
        print_success("Clean operation completed successfully!")
        sys.exit(0)
    else:
        print_error("No relevant action specified (down, build, clear).")
        print(f"Use {Colors.YELLOW}-h{Colors.END} for help.")
        sys.exit(1)

    print_separator()

    if args.mode_a:
        print_progress("Initializing mode A (pcap replay)...")
    elif args.mode_b:
        print_progress("Initializing mode B (capture interface)...")
    elif use_mode_c:
        print_progress("Initializing mode C (PCAP-over-IP)...")

        # Prompt for missing parameters instead of exiting
        prompt_for_missing_params(args, use_mode_c)

        # Validate start date format after prompting
        if args.start_date and not validate_date_format(args.start_date):
            print_error(f"Invalid start date format: {args.start_date}")
            print("This should not happen as validation is done during prompting.")
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

        # Create a new file 'services_config.json' empty
        json_config = "services_config.json"
        if not os.path.exists(json_config):
            print_info(f"Creating empty {json_config} file.")
            with open(json_config, "w") as f:
                f.write("{}")

    print_separator()

    # Start the containers using the selected docker-compose file
    compose_up(compose_file, args.build)

    print_separator("═", 60)
    print_success(f"Shovel successfully started in mode {'A' if args.mode_a else 'B' if args.mode_b else 'C'}!")
    print(f"  {Colors.BOLD}Web interface:{Colors.END} {Colors.CYAN}http://127.0.0.1:8000{Colors.END}")
    print_separator("═", 60)


if __name__ == "__main__":
    main()
