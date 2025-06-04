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


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_tz():
    """Get the current timezone in 00:00 format"""
    now = datetime.now()
    tz = now.astimezone().strftime('%:z')
    return tz


def validate_date_format(date_str):
    """Validate the date string format (YYYY-MM-DDThh:mm) without timezone validation"""
    # Check basic format first (date + time)
    try:
        basic_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"
        if not re.match(basic_pattern, date_str):
            return False

        datetime.fromisoformat(date_str[:16])
        return True
    except ValueError:
        return False


def validate_timezone(date_str):
    """Validate the timezone string in format +/-HH:MM"""
    has_tz = ('+' in date_str or '-' in date_str[16:])
    if not has_tz:
        return None

    try:
        if not re.match(r"^[+-]\d{2}:\d{2}$", date_str[16:]):
            return False

        datetime.fromisoformat(date_str)
        return True
    except (ValueError, IndexError):
        return False


def prompt_for_missing_params(args, use_mode_c):
    """Prompt user for missing required parameters with styled interface"""

    now = datetime.now()
    example_date = f"{now.year}-{now.month:02d}-{now.day:02d}T{now.hour}:"
    if now.minute < 30:
        example_date += "00"
    elif now.minute >= 30:
        example_date += "30"
    example_date += get_tz()

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
                    if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target_ip):
                        octets = target_ip.split('.')
                        valid_octets = all(0 <= int(octet) <= 255 for octet in octets)
                        if valid_octets:
                            args.target_ip = target_ip
                            break
                        else:
                            print_error("IP address octets must be between 0-255. Please try again.")
                    else:
                        print_error("Invalid IP address format. Please use format: xxx.xxx.xxx.xxx")
                else:
                    print_error("Target IP cannot be empty. Please try again.")

        # No date added
        wrong_tz = False
        if not args.start_date:
            print()
            print_info("CTF Start Date Configuration")
            print_info(f"Format: {Colors.YELLOW}YYYY-MM-DDThh:mm {Colors.BLUE}(e.g., {example_date}){Colors.END}")

            while True:
                start_date = prompt_styled("Enter CTF start date")
                if start_date and validate_date_format(start_date):
                    args.start_date = start_date
                    break
                elif start_date:
                    print_error("Invalid date format. Please use: YYYY-MM-DDThh:mm")
                else:
                    print_error("Start date cannot be empty. Please try again.")

            if not validate_timezone(start_date):
                wrong_tz = True
        else:
            # Check if added date is correct
            if not validate_date_format(args.start_date):
                print_error(f"Invalid date format: {args.start_date}")
                print_info(f"Format: {Colors.YELLOW}YYYY-MM-DDThh:mm {Colors.BLUE}(e.g., {example_date}){Colors.END}")

                while True:
                    start_date = prompt_styled("Enter CTF start date: ")
                    if start_date and validate_date_format(start_date):
                        args.start_date = start_date
                        break
                    elif start_date:
                        print_error("Invalid date format. Please use: YYYY-MM-DDThh:mm")
                    else:
                        print_error("Start date cannot be empty. Please try again.")

                if not validate_timezone(start_date):
                    wrong_tz = True
            else:
                if not validate_timezone(args.start_date):
                    wrong_tz = True

        # Request for timezone, if not specified
        if wrong_tz:
            print()
            print_warning("Timezone not inserted or wrong.")
            print()
            print_info("Timezone Configuration")
            current_tz = get_tz()
            print_info(f"Format: {Colors.YELLOW}+/-HH:MM {Colors.END}")

            while True:
                tz = prompt_styled("Enter timezone", default=current_tz)
                if validate_timezone(args.start_date + tz):
                    args.start_date = f"{args.start_date}{tz}"
                    break
                print_error(f"Invalid timezone format. Please use +/-HH:MM")

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

        # Everything has been already validated
        content += f"CTF_START_DATE={start_date}\n"
        content += f"CTF_TICK_LENGTH={tick_length}\n"
        content += f"TARGET_IP={target_ip}\n"
        content += f"REFRESH_RATE={refresh_rate}\n"

        f.write(content)

    print_success(f"Environment variables written to {ENV_FILE}")
    print(f"  {Colors.CYAN}CTF_START_DATE{Colors.END} = {start_date}")
    print(f"  {Colors.CYAN}TARGET_IP{Colors.END} = {target_ip}")
    print(f"  {Colors.CYAN}CTF_TICK_LENGTH{Colors.END} = {tick_length}")
    print(f"  {Colors.CYAN}REFRESH_RATE{Colors.END} = {refresh_rate}")
    print()


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
    cmd = ["docker", "compose", "-f", compose_file, "down", "--remove-orphans"]
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


def show_action_selection():
    """Display action selection menu"""
    print_info("Available actions:")
    print(f"  {Colors.BOLD}build{Colors.END} - Build and start containers")
    print(f"  {Colors.BOLD}down{Colors.END} - Stop containers")
    print(f"  {Colors.BOLD}clear{Colors.END} - Clean Suricata output and stop containers")
    print()


def prompt_for_action():
    """Prompt user for action selection"""
    print_separator()
    print(f"{Colors.BOLD}{Colors.CYAN}Action Selection{Colors.END}")
    print_separator()
    
    show_action_selection()
    
    while True:
        action = prompt_styled("Enter action (build/down/clear)").strip().lower()
        if action in ['build', 'down', 'clear']:
            return action
        print_error("Invalid action. Please choose from: build, down, clear")


def main():
    # Clear screen and show banner
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()

    parser = argparse.ArgumentParser(
        description="Start Shovel using the specified mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BOLD}Examples:{Colors.END}
  {Colors.CYAN}./start.py --build{Colors.END}                               # Start in mode C with build
  {Colors.CYAN}./start.py --mode-a{Colors.END}                              # Start in mode A
  {Colors.CYAN}./start.py --down{Colors.END}                                # Stop containers
  {Colors.CYAN}./start.py --clear{Colors.END}                               # Clean and stop
  {Colors.CYAN}./start.py -b --mode-c --target-ip 192.168.1.10{Colors.END}  # Start mode C with IP
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

    parser.add_argument("--date", dest="start_date", help="Specify CTF start date (format: YYYY-MM-DDThh:mm+ZZ:zz)")
    parser.add_argument("--target-ip", "-ip", dest="target_ip", help="Specify target machine IP address (for mode C)")
    parser.add_argument("--refresh-rate", "-r", dest="refresh_rate", help="Specify refresh rate (in seconds)")
    parser.add_argument("--tick-length", "-t", dest="tick_length", help="Specify tick length (in seconds)")
    parser.add_argument("--key", "-k", dest="key", help="Specify algorithm for SSH key exchange (default: ed25519)")

    args = parser.parse_args()

    # Check if any action argument was provided
    action_provided = args.build or args.down or args.clear
    
    # If no action is provided, enter interactive mode
    if not action_provided:
        action = prompt_for_action()
        # Set the appropriate flag based on user choice
        if action == 'build':
            args.build = True
        elif action == 'down':
            args.down = True
        elif action == 'clear':
            args.clear = True

    # Mode C as default if no mode is specified
    use_mode_c = not (args.mode_a or args.mode_b) or args.mode_c

    # Select the appropriate docker-compose file based on the mode
    compose_file = COMPOSE_FILES["C"]
    if args.mode_a:
        compose_file = COMPOSE_FILES["A"]
        print_info("Starting in mode A (pcap replay)...")
    elif args.mode_b:
        compose_file = COMPOSE_FILES["B"]
        print_info("Starting in mode B (capture interface)...")
    elif use_mode_c:
        compose_file = COMPOSE_FILES["C"]

    # Now we know an action is set (either from args or interactive mode)
    if os.path.exists(ENV_FILE):
        compose_down(compose_file)

    if args.down and not args.build:
        print_success("Operation completed successfully!")
        sys.exit(0)

    if args.build:
        while True:
            r = prompt_styled("Do you want to clear Suricata output directory? (y/n)",
                              required=False, default="n").strip().lower()
            if r in ['y', 'yes']:
                clear_suricata()
                args.clear = False
                print()
                break
            elif r in ['n', 'no', '']:
                print_warning("Suricata output directory will not be cleared.")
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")

    if args.clear:
        clear_suricata()
        sys.exit(0)

    print_separator()

    if args.mode_a:
        print_progress("Initializing mode A (pcap replay)...")
    elif args.mode_b:
        print_progress("Initializing mode B (capture interface)...")
    elif use_mode_c:
        print_progress("Initializing mode C (PCAP-over-IP)...")

        # Prompt for missing parameters
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
