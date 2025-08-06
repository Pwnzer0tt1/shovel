#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

ENV_FILE = ".env"
COMPOSE_FILES = {
    "A": "docker-compose-a.yml",
    "B": "docker-compose-b.yml",
    "C": "docker-compose-c.yml",
}
OFFSET_PRINT = 77


# Terminal colors and formatting
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_banner():
    """Print a nice banner for the application"""
    terminal_width = shutil.get_terminal_size().columns
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                            SHOVEL                             ║
║           CTF Traffic Analysis Tool - by Pwnzer0tt1           ║
╚═══════════════════════════════════════════════════════════════╝
    """

    lines = banner.strip().split("\n")
    for line in lines:
        padding = (terminal_width - len(line)) // 2
        print(" " * max(0, padding) + Colors.CYAN + Colors.BOLD + line + Colors.END)
    print()


def print_separator(char="─", length=OFFSET_PRINT):
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


def prompt_styled(prompt_text, required=True, default=None, current=None):
    """Styled input prompt with validation"""
    if default:
        prompt_text += f" {Colors.YELLOW}(default: {default}){Colors.END}"
    if current:
        prompt_text += f" {Colors.YELLOW}(current: {current}){Colors.END}"
    prompt_text += f" {Colors.BOLD}→{Colors.END} "

    while True:
        try:
            user_input = input(prompt_text).strip()
            if not user_input and default:
                return default
            if not user_input and current:
                return current
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


def prompt_for_mode():
    """Prompt user for mode selection"""
    print_separator(char="═")
    print(f"{Colors.BOLD}{Colors.CYAN}Mode Selection{Colors.END}".center(OFFSET_PRINT + 12))
    print_separator()

    print_info("Choose a mode to start Shovel:")
    print(f"  {Colors.CYAN}A{Colors.END} - PCAP replay mode")
    print(f"  {Colors.CYAN}B{Colors.END} - Capture interface mode")
    print(f"  {Colors.CYAN}C{Colors.END} - PCAP-over-IP mode")
    print()

    while True:
        mode = prompt_styled("Enter mode (A/B/C)", default="C").strip().upper()
        if mode in ["A", "B", "C"]:
            print_separator(char="═")
            print()
            return mode
        print_error("Invalid mode. Please choose from: A, B, C")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def get_tz():
    """Get the current timezone in 00:00 format"""
    now = datetime.now()
    offset = now.astimezone().utcoffset()
    if offset is None:
        return "+00:00"
    
    total_seconds = offset.total_seconds()
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes = remainder // 60
    sign = "-" if total_seconds < 0 else "+"
    tz = f"{sign}{int(hours):02d}:{int(minutes):02d}"
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
    has_tz = "+" in date_str or "-" in date_str[16:]
    if not has_tz:
        return None

    try:
        if not re.match(r"^[+-]\d{2}:\d{2}$", date_str[16:]):
            return False

        datetime.fromisoformat(date_str)
        return True
    except (ValueError, IndexError):
        return False


def prompt_for_missing_params(args):
    """Prompt user for missing required parameters with styled interface"""

    now = datetime.now()
    example_date = f"{now.year}-{now.month:02d}-{now.day:02d}T{now.hour:02d}:"
    if now.minute < 30:
        example_date += "00"
    elif now.minute >= 30:
        example_date += "30"
    example_date += get_tz()

    print_separator(char="═")
    print(f"{Colors.BOLD}{Colors.CYAN}Configuration Setup for Mode C{Colors.END}".center(OFFSET_PRINT + 12))
    print_separator()

    # Target IP with validation
    if not args.target_ip:
        print_info("Target IP Configuration")
        while True:
            target_ip = prompt_styled("Enter target IP address")
            if target_ip:
                if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", target_ip):
                    octets = target_ip.split(".")
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

    # Start date with validation
    if not args.start_date:
        print()
        print_info("CTF Start Date Configuration")
        print_info(f"Format: {Colors.YELLOW}YYYY-MM-DDThh:mm+ZZ:zz {Colors.BLUE}(e.g., {example_date}){Colors.END}")

        while True:
            start_date = prompt_styled("Enter CTF start date")
            if start_date and validate_date_format(start_date):
                args.start_date = start_date
                break
            elif start_date:
                print_error("Invalid date format. Please use: YYYY-MM-DDThh:mm+ZZ:zz")
            else:
                print_error("Start date cannot be empty. Please try again.")
    else:
        # Check if added date is correct
        if not validate_date_format(args.start_date):
            print_error(f"Invalid date format: {args.start_date}")
            print_info(f"Format: {Colors.YELLOW}YYYY-MM-DDThh:mm {Colors.BLUE}(e.g., {example_date}){Colors.END}")

            while True:
                start_date = prompt_styled("Enter CTF start date")
                if start_date and validate_date_format(start_date):
                    args.start_date = start_date
                    break
                elif start_date:
                    print_error("Invalid date format. Please use: YYYY-MM-DDThh:mm+ZZ:zz")
                else:
                    print_error("Start date cannot be empty. Please try again.")
        else:
            start_date = args.start_date

    # Request for timezone, if not specified
    if not validate_timezone(start_date):
        print()
        print_warning("Timezone not inserted or wrong.")
        print()
        print_info("Timezone Configuration")
        current_tz = get_tz()
        print_info(f"Format: {Colors.YELLOW}+/-HH:MM {Colors.END}")

        while True:
            tz = prompt_styled("Enter timezone", current=current_tz)
            if validate_timezone(args.start_date + tz):
                args.start_date = f"{args.start_date}{tz}"
                break
            print_error(f"Invalid timezone format. Please use +/-HH:MM")

    # Tick length with validation
    if not args.tick_length:
        print()
        print_info("Tick Length Configuration")
        while True:
            tick_length = prompt_styled("Enter tick length (in seconds)", default="120")
            if tick_length and tick_length.isdigit():
                args.tick_length = tick_length
                break
            print_error("Tick length must be a positive number. Please try again.")

    # Refresh rate with validation
    if not args.refresh_rate:
        print()
        print_info("Refresh Rate Configuration")
        while True:
            refresh_rate = prompt_styled("Enter refresh rate (in seconds)", default="5")
            if refresh_rate and refresh_rate.isdigit():
                args.refresh_rate = refresh_rate
                break
            print_error("Refresh rate must be a positive number. Please try again.")

    # SSH key algorithm with validation
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
    print_progress("Stopping running containers...")
    
    # Check if ENV file exists
    if not os.path.exists(ENV_FILE):
        print_warning(f"{ENV_FILE} file not found. Skipping container stop operation.")
        print()
        return False
    
    # Check if compose file exists
    if not os.path.exists(compose_file):
        print_warning(f"Docker compose file not found: {compose_file}")
        print_info("Skipping container stop operation.")
        return False

    cmd = ["docker", "compose", "-f", compose_file, "down", "--remove-orphans"]
    print_progress(f"Executing: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print_success("Containers successfully stopped!")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to stop containers: {e}")
        print_info("Make sure Docker is running and accessible.")
        print()
        return False


def compose_up(compose_file, build=True):
    """Start containers defined in the specified docker-compose file"""
    
    # Check if compose file exists
    if not os.path.exists(compose_file):
        print_error(f"Docker compose file not found: {compose_file}")
        sys.exit(1)

    cmd = ["docker", "compose", "-f", compose_file, "up", "-d"]
    if build:
        cmd.append("--build")

    print_progress(f"Executing: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print_success("Containers successfully started!")
        print()
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start containers: {e}")
        print_info("Check if all required images and dependencies are available.")
        sys.exit(1)


def clear_suricata():
    """Clean the Suricata output directory"""
    if not os.path.exists("./suricata/output"):
        print_warning("Suricata output directory not found. Skipping clear operation.")
        os.makedirs("./suricata/output", exist_ok=True)
        return

    if not os.listdir("./suricata/output"):
        print_info("Suricata output directory already empty. Skipping clear operation.")
        return

    cmd = "sudo rm -rf ./suricata/output/*"
    print_progress("Cleaning Suricata output directory...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print_success("Suricata output directory cleaned successfully!")
        print()
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to clean Suricata output directory: {e}")
        print_warning("You may need to check permissions or run with appropriate privileges.")
        print()



def clear_config():
    """Clear configuration files"""
    
    files_to_clear = [ENV_FILE, "services_config.json"]
    cleared_files = []

    for file_path in files_to_clear:
        if os.path.exists(file_path):
            os.remove(file_path)
            cleared_files.append(file_path)

    if cleared_files:
        print_success(f"Cleared config files: {', '.join(cleared_files)}")
        print()
    else:
        print_info("No config files found to clear.")
        print()


def clear_pcap():
    """Clear PCAP files"""
    pcap_dir = "./tshark/dumps/"
    if not os.path.exists(pcap_dir):
        print_warning("PCAP directory not found. Skipping clear operation.")
        os.makedirs(pcap_dir, exist_ok=True)
        return

    if not os.listdir(pcap_dir):
        print_info("PCAP directory already empty. Skipping clear operation.")
        return

    cmd = f"sudo rm -rf {pcap_dir}/*"
    print_progress("Cleaning PCAP files...")

    try:
        subprocess.run(cmd, check=True, shell=True)
        print_success("PCAP files cleaned successfully!")
        print()
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to clean PCAP files: {e}")
        print()


def get_compose_file_for_mode(mode):
    """Get the appropriate compose file for the given mode"""
    return COMPOSE_FILES.get(mode.upper(), COMPOSE_FILES["C"])


def handle_start_command(args):
    """Handle the start command"""
    print_progress("Starting Shovel...\n")

    if args.mode_a:
        mode = "A"
    elif args.mode_b:
        mode = "B"
    elif args.mode_c:
        mode = "C"
    else:
        # Interactive mode selection
        mode = prompt_for_mode()

    compose_file = get_compose_file_for_mode(mode)

    # Stop existing containers
    compose_down(compose_file)

    # Handle clear option - skip if --no-clean is specified
    if args.no_clean:
        print_info("Skipping environment cleaning due to --no-clean flag...")
        print_warning("Suricata output directory will not be cleared.")
        print_warning("Config files will not be cleared.")
        print_warning("PCAP files will not be cleared.")
        print()
    elif not args.no_build:
        
        # Clear Suricata output
        while True:
            r = (
                prompt_styled(
                    "Do you want to clear Suricata output directory? (y/n)",
                    required=False,
                    default="n",
                )
                .strip()
                .lower()
            )
            if r in ["y", "yes"]:
                clear_suricata()
                break
            elif r in ["n", "no", ""]:
                print_warning("Suricata output directory will not be cleared.")
                print()
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")
        
        # Clear config files
        while True:
            r = (
                prompt_styled(
                    "Do you want to clear config files? (y/n)",
                    required=False,
                    default="n",
                )
                .strip()
                .lower()
            )
            if r in ["y", "yes"]:
                clear_config()
                break
            elif r in ["n", "no", ""]:
                print_warning("Config files will not be cleared.")
                print()
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")
        
        # Clear PCAP files
        while True:
            r = (
                prompt_styled(
                    "Do you want to clear pcap files? (y/n)",
                    required=False,
                    default="n",
                )
                .strip()
                .lower()
            )
            if r in ["y", "yes"]:
                clear_pcap()
                break
            elif r in ["n", "no", ""]:
                print_warning("PCAP files will not be cleared.")
                print()
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")

    # Mode-specific initialization
    if mode == "A":
        print_progress("Initializing mode A (pcap replay)...")
        if not os.path.exists(compose_file):
            print_error(f"Docker compose file not found: {compose_file}")
            sys.exit(1)

    elif mode == "B":
        print_progress("Initializing mode B (capture interface)...")
        if not os.path.exists(compose_file):
            print_error(f"Docker compose file not found: {compose_file}")
            sys.exit(1)

    elif mode == "C":
        print_progress("Initializing mode C (PCAP-over-IP)...\n")
        if not os.path.exists(compose_file):
            print_error(f"Docker compose file not found: {compose_file}")
            sys.exit(1)

        prompt_for_missing_params(args)

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
        update_compose(target_ip=args.target_ip, key=args.key)

        # Create a new file 'services_config.json' empty
        json_config = "services_config.json"
        if not os.path.exists(json_config):
            print_info(f"Creating empty {json_config} file.")
            with open(json_config, "w") as f:
                f.write("{}")

    print_separator(char="═")
    print_success("Configuration completed successfully!")
    print_separator(char="═")
    print()

    # Start the containers using the selected docker-compose file
    compose_up(compose_file, not args.no_build)

    print_separator(char="═")
    print_success(f"Shovel successfully started in mode {mode}!")
    print(f"  {Colors.BOLD}Web interface:{Colors.END} {Colors.CYAN}http://127.0.0.1:8000{Colors.END}")
    print_separator(char="═")


def handle_stop_command():
    """Handle the stop command"""
    print_progress("Stopping Shovel...")

    # Check if .env exists to determine which compose file to use
    if os.path.exists(ENV_FILE):
        compose_file = COMPOSE_FILES["C"]  # Default to C
        print_info("Stopping containers using default compose file...")
    else:
        print_warning("No configuration file found. Attempting to stop default containers...")
        compose_file = COMPOSE_FILES["C"]

    # Check if compose file exists
    if not os.path.exists(compose_file):
        print_error(f"Docker compose file not found: {compose_file}")
        print_info("Cannot determine which containers to stop.")
        sys.exit(1)

    compose_down(compose_file)
    print_success("Operation completed successfully!")


def handle_clear_command(args):
    """Handle the clear command with granular options"""
    print_progress("Clearing data...")

    # If no specific options, default to clearing output and stopping containers
    if not (args.all or args.config or args.suricata or args.pcap):
        print_info("No specific clear option provided.\n")

        # Stop containers first
        compose_file = COMPOSE_FILES["C"]
        compose_down(compose_file)

        # Clear Suricata output
        while True:
            r = (
                prompt_styled(
                    "Do you want to clear Suricata output directory? (y/n)",
                    required=False,
                    default="n",
                )
                .strip()
                .lower()
            )
            if r in ["y", "yes"]:
                clear_suricata()
                break
            elif r in ["n", "no", ""]:
                print_warning("Suricata output directory will not be cleared.")
                print()
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")

        # Clear config files
        while True:
            r = (
                prompt_styled(
                    "Do you want to clear config files? (y/n)",
                    required=False,
                    default="n",
                )
                .strip()
                .lower()
            )
            if r in ["y", "yes"]:
                clear_config()
                break
            elif r in ["n", "no", ""]:
                print_warning("Config files will not be cleared.")
                print()
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")

        # Clear PCAP files
        while True:
            r = (
                prompt_styled(
                    "Do you want to clear pcap files? (y/n)",
                    required=False,
                    default="n",
                )
                .strip()
                .lower()
            )
            if r in ["y", "yes"]:
                clear_pcap()
                break
            elif r in ["n", "no", ""]:
                print_warning("PCAP files will not be cleared.")
                print()
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")
        return

    # Handle --all option
    if args.all:
        print_info("Clearing everything...")

        # Stop containers - check if compose file exists
        compose_file = COMPOSE_FILES["C"]
        compose_down(compose_file)

        # Clear Suricata output
        clear_suricata()

        # Clear config files
        clear_config()

        # Clear PCAP files
        clear_pcap()

        print_success("All data cleared successfully!")
        return

    # Handle granular options
    cleared_items = []

    if args.config:
        clear_config()
        cleared_items.append("config files")

    if args.suricata:
        # Stop containers first if clearing output - check if compose file exists
        compose_file = COMPOSE_FILES["C"]
        compose_down(compose_file)

        clear_suricata()
        cleared_items.append("Suricata output")

    if args.pcap:
        # Clear PCAP files - check if directory exists
        clear_pcap()
        cleared_items.append("PCAP files")

    if cleared_items:
        print_success(f"Cleared: {', '.join(cleared_items)}")
    else:
        print_info("Nothing to clear.")


def handle_status_command():
    """Handle the status command - show container status"""
    print_progress("Checking Shovel status...")

    # Check if .env exists to provide context
    if not os.path.exists(ENV_FILE):
        print_warning("No configuration file found. Showing default container status...")

    # Default to mode C compose file
    compose_file = COMPOSE_FILES["C"]

    # Check if compose file exists
    if not os.path.exists(compose_file):
        print_error(f"Docker compose file not found: {compose_file}")
        print_info("Cannot check container status without compose file.")
        sys.exit(1)

    # Always show container status
    print_info("Container Status:")
    cmd = ["docker", "compose", "-f", compose_file, "ps"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to get container status: {e}")
        print_info("Make sure Docker is running and accessible.")
    print()


def handle_logs_command(args):
    """Handle the logs command - follow container logs"""
    print_progress("Following container logs...")

    # Check if .env exists to provide context
    if not os.path.exists(ENV_FILE):
        print_warning("No configuration file found. Using default compose file...")

    # Default to mode C compose file
    compose_file = COMPOSE_FILES["C"]

    # Check if compose file exists
    if not os.path.exists(compose_file):
        print_error(f"Docker compose file not found: {compose_file}")
        print_info("Cannot follow logs without compose file.")
        sys.exit(1)

    # Build logs command - always start with -f for compatibility with --tail
    cmd = ["docker", "compose", "-f", compose_file, "logs", "-f"]

    # Add arguments directly from sys.argv instead of parsed args
    if len(sys.argv) > 2:  # If there are arguments after "logs"
        cmd.extend(sys.argv[2:])  # Take everything after "logs"

    print_progress(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to follow logs: {e}")
        print_info("Make sure containers are running and Docker is accessible.")
        sys.exit(1)


def handle_help_command():
    """Handle the help command - show help information"""
    parser = create_parser()
    parser.print_help()


def create_parser():
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="Shovel - CTF Traffic Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # Disable default -h/--help
        epilog=f"""
{Colors.BOLD}Examples:{Colors.END}
  {Colors.CYAN}./start.py start --mode-a{Colors.END}                         # Start Shovel in mode A
  {Colors.CYAN}./start.py start --mode-c --target-ip 10.60.2.1 {Colors.END}  # Start mode C with target IP
  {Colors.CYAN}./start.py stop{Colors.END}                                   # Stop running containers
  {Colors.CYAN}./start.py clear{Colors.END}                                  # Clear output and stop containers
  {Colors.CYAN}./start.py clear --all{Colors.END}                            # Clear everything
  {Colors.CYAN}./start.py clear --config{Colors.END}                         # Clear only config files
  {Colors.CYAN}./start.py clear --suricata{Colors.END}                       # Clear only Suricata output
  {Colors.CYAN}./start.py clear --pcap{Colors.END}                           # Clear only PCAP files
  {Colors.CYAN}./start.py status{Colors.END}                                 # Show container status
  {Colors.CYAN}./start.py logs{Colors.END}                                   # Follow all container logs
  {Colors.CYAN}./start.py logs --tail 100{Colors.END}                        # Last 100 logs of all containers
  {Colors.CYAN}./start.py logs webapp --tail 50{Colors.END}                  # Last 50 logs of specific service
  {Colors.CYAN}./start.py help{Colors.END}                                   # Show this help message
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Help command
    subparsers.add_parser("help", help="Show help information")

    # Start command
    parser_start = subparsers.add_parser("start", help="Start Shovel")
    mode_group = parser_start.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--mode-a", action="store_true", help="Start in mode A (pcap replay)"
    )
    mode_group.add_argument(
        "--mode-b", action="store_true", help="Start in mode B (capture interface)"
    )
    mode_group.add_argument(
        "--mode-c", action="store_true", help="Start in mode C (PCAP-over-IP)"
    )

    parser_start.add_argument(
        "--no-build", action="store_true", help="Skip building images"
    )
    parser_start.add_argument(
        "--no-clean", action="store_true", help="Skip cleaning environment"
    )
    parser_start.add_argument(
        "--date",
        dest="start_date",
        help="Specify CTF start date (format: YYYY-MM-DDThh:mm+ZZ:zz)",
    )
    parser_start.add_argument(
        "--target-ip",
        "-ip",
        dest="target_ip",
        help="Specify target machine IP address (for mode C)",
    )
    parser_start.add_argument(
        "--refresh-rate",
        "-r",
        dest="refresh_rate",
        help="Specify refresh rate (in seconds)",
    )
    parser_start.add_argument(
        "--tick-length",
        "-t",
        dest="tick_length",
        help="Specify tick length (in seconds)",
    )
    parser_start.add_argument(
        "--key",
        "-k",
        dest="key",
        help="Specify algorithm for SSH key exchange (default: ed25519)",
    )

    # Stop command
    subparsers.add_parser("stop", help="Stop Shovel containers")

    # Clear command
    parser_clear = subparsers.add_parser(
        "clear", help="Clean Suricata output and stop containers"
    )
    parser_clear.add_argument(
        "--all",
        "-A",
        action="store_true",
        help="Clear everything (containers, output, config)",
    )
    parser_clear.add_argument(
        "--config",
        "-c",
        action="store_true",
        help="Clear config files (.env and services_config.json)",
    )
    parser_clear.add_argument(
        "--suricata",
        "-s",
        action="store_true",
        help="Clean Suricata output and stop containers",
    )
    parser_clear.add_argument(
        "--pcap",
        "-p",
        action="store_true",
        help="Clear PCAP files captured with Tshark",
    )

    # Status command - simple container status
    subparsers.add_parser("status", help="Show container status")

    # Logs command - NO ARGUMENTS, uses sys.argv directly
    subparsers.add_parser("logs", help="Follow container logs")

    return parser


def show_action_selection():
    """Display action selection menu"""
    print_info("Available actions:")
    print(f"  {Colors.BOLD}start{Colors.END} - Build and start containers")
    print(f"  {Colors.BOLD}stop{Colors.END} - Stop running containers, if any")
    print(f"  {Colors.BOLD}clear{Colors.END} - Clear Suricata's output, and stop containers")
    print(f"  {Colors.BOLD}status{Colors.END} - Show container status")
    print(f"  {Colors.BOLD}logs{Colors.END} - Follow container logs")
    print(f"  {Colors.BOLD}help{Colors.END} - Show help information")
    print()


def prompt_for_action():
    """Prompt user for action selection"""
    print_separator(char="═")
    print(f"{Colors.BOLD}{Colors.CYAN}Action Selection{Colors.END}".center(OFFSET_PRINT + 12))
    print_separator()

    show_action_selection()

    while True:
        action = (
            prompt_styled(
                "Enter action (start/stop/clear/status/logs/help)", default="start"
            )
            .strip()
            .lower()
        )
        if action in ["start", "stop", "clear", "status", "logs", "help"]:
            print_separator(char="═")
            print()
            return action
        print_error(
            "Invalid action. Please choose from: start, stop, clear, status, logs, help"
        )


def main():
    # Clear screen and show banner
    os.system("clear" if os.name == "posix" else "cls")
    print_banner()

    # Handle logs command BEFORE argparse to avoid --tail conflicts
    if len(sys.argv) >= 2 and sys.argv[1] == "logs":
        # Call logs handler directly with raw arguments
        class MockArgs:
            pass

        args = MockArgs()
        handle_logs_command(args)
        return

    parser = create_parser()

    # If no arguments provided, enter interactive mode
    if len(sys.argv) == 1:
        action = prompt_for_action()
        args = parser.parse_args([action])
    else:
        args = parser.parse_args()

    # Handle commands (logs is already handled above)
    if args.command == "help":
        handle_help_command()
    elif args.command == "start":
        handle_start_command(args)
    elif args.command == "stop":
        handle_stop_command()
    elif args.command == "clear":
        handle_clear_command(args)
    elif args.command == "status":
        handle_status_command()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
