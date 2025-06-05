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
    print_separator()
    print(f"{Colors.BOLD}{Colors.CYAN}Mode Selection{Colors.END}".center(72))
    print_separator()

    show_mode_selection()

    while True:
        mode = prompt_styled("Enter mode (A/B/C)", default="C").strip().upper()
        if mode in ['A', 'B', 'C']:
            return mode
        print_error("Invalid mode. Please choose from: A, B, C")


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


def prompt_for_missing_params(args):
    """Prompt user for missing required parameters with styled interface"""

    now = datetime.now()
    example_date = f"{now.year}-{now.month:02d}-{now.day:02d}T{now.hour:02d}:"
    if now.minute < 30:
        example_date += "00"
    elif now.minute >= 30:
        example_date += "30"
    example_date += get_tz()

    print_separator()

    # Target IP
    if not args.target_ip:
        print_info("Target IP Configuration")
        while True:
            target_ip = prompt_styled("Enter target IP address")
            if target_ip:
                args.target_ip = target_ip
                break
            else:
                print_error("Target IP is required for mode C.")

    # No date added
    start_date = ""
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
                print_error("Invalid date format. Please use YYYY-MM-DDThh:mm format.")
            else:
                print_error("CTF start date is required for mode C.")
    else:
        # Check if added date is correct
        if not validate_date_format(args.start_date):
            print_error(f"Invalid date format: {args.start_date}")
            sys.exit(1)
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
            timezone = prompt_styled("Enter timezone", default=current_tz)
            args.start_date = start_date + timezone
            break

    # Tick length
    if not args.tick_length:
        print()
        print_info("Tick Length Configuration")
        while True:
            args.tick_length = prompt_styled("Enter tick length (seconds)", default="120")
            break

    # Refresh rate
    if not args.refresh_rate:
        print()
        print_info("Refresh Rate Configuration")
        while True:
            args.refresh_rate = prompt_styled("Enter refresh rate (seconds)", default="5")
            break

    # SSH key algorithm
    if not args.key:
        print()
        print_info("SSH Key Algorithm Configuration")
        supported_algorithms = ["rsa", "ed25519", "ecdsa", "dsa"]
        print_info(f"Available algorithms: {Colors.YELLOW}{', '.join(supported_algorithms)}{Colors.END}")
        while True:
            args.key = prompt_styled("Enter SSH key algorithm", default="ed25519")
            break

    print_success("Configuration completed successfully!")
    print()


def write_env(start_date, target_ip, tick_length, refresh_rate):
    if not os.path.exists(ENV_FILE):
        print_warning(f"{ENV_FILE} file not found. Creating new file.")
        with open(ENV_FILE, "w") as f:
            pass
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


def compose_up(compose_file, build=True):
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


def get_compose_file_for_mode(mode):
    """Get the appropriate compose file for the given mode"""
    return COMPOSE_FILES.get(mode.upper(), COMPOSE_FILES["C"])


def handle_start_command(args):
    """Handle the start command"""
    print_progress("Starting Shovel...")
    
    # Determine mode
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

    # Stop existing containers first
    if os.path.exists(ENV_FILE):
        compose_down(compose_file)

    # Handle clear option
    if args.no_build:
        print_info("Skipping build step...")
    else:
        while True:
            r = prompt_styled("Do you want to clear Suricata output directory? (y/n)",
                              required=False, default="n").strip().lower()
            if r in ['y', 'yes']:
                clear_suricata()
                print()
                break
            elif r in ['n', 'no', '']:
                print_warning("Suricata output directory will not be cleared.")
                break
            else:
                print_error("Invalid input. Please enter 'y' or 'n'.")

    print_separator()

    # Mode-specific initialization
    if mode == "A":
        print_progress("Initializing mode A (pcap replay)...")
    elif mode == "B":
        print_progress("Initializing mode B (capture interface)...")
    elif mode == "C":
        print_progress("Initializing mode C (PCAP-over-IP)...")

        # Prompt for missing parameters
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
    compose_up(compose_file, not args.no_build)

    print_separator("═", 60)
    print_success(f"Shovel successfully started in mode {mode}!")
    print(f"  {Colors.BOLD}Web interface:{Colors.END} {Colors.CYAN}http://127.0.0.1:8000{Colors.END}")
    print_separator("═", 60)


def handle_stop_command(args):
    """Handle the stop command"""
    print_progress("Stopping Shovel...")
    
    # Stop all compose files to be safe
    compose_down(COMPOSE_FILES["C"])
    
    print_success("Operation completed successfully!")


def handle_clear_command(args):
    """Handle the clear command with granular options"""
    print_progress("Clearing data...")
    
    # If no specific options, default to clearing output and stopping containers
    if not (args.all or args.config or args.output):
        print_info("No specific clear option provided. Clearing output and stopping containers...")
        # Stop containers first
        compose_down(COMPOSE_FILES["C"])
        # Clear Suricata output
        clear_suricata()
        print_success("Clear operation completed successfully!")
        return

    # Handle --all option
    if args.all:
        print_info("Clearing everything...")
        # Stop containers
        compose_down(COMPOSE_FILES["C"])
        # Clear Suricata output
        clear_suricata()
        # Clear config files
        clear_config_files()
        print_success("All data cleared successfully!")
        return
    
    # Handle granular options
    cleared_items = []
    
    if args.config:
        clear_config_files()
        cleared_items.append("config files")
    
    if args.output:
        # Stop containers first if clearing output
        compose_down(COMPOSE_FILES["C"])
        clear_suricata()
        cleared_items.append("Suricata output")
    
    if cleared_items:
        print_success(f"Cleared: {', '.join(cleared_items)}")
    else:
        print_info("Nothing to clear.")

def clear_config_files():
    """Clear configuration files"""
    files_to_clear = [ENV_FILE, "services_config.json"]
    cleared_files = []
    
    for file_path in files_to_clear:
        if os.path.exists(file_path):
            os.remove(file_path)
            cleared_files.append(file_path)
    
    if cleared_files:
        print_success(f"Cleared config files: {', '.join(cleared_files)}")
    else:
        print_info("No config files found to clear.")

def handle_status_command(args):
    """Handle the status command - show container status"""
    print_progress("Checking Shovel status...")
    
    # Default to mode C compose file
    compose_file = COMPOSE_FILES["C"]
    
    # Always show container status
    print_info("Container Status:")
    cmd = ["docker", "compose", "-f", compose_file, "ps"]
    subprocess.run(cmd)
    print()


def handle_logs_command(args):
    """Handle the logs command - follow container logs"""
    print_progress("Following container logs...")
    
    # Default to mode C compose file
    compose_file = COMPOSE_FILES["C"]
    
    # Build logs command - always start with -f for compatibility with --tail
    cmd = ["docker", "compose", "-f", compose_file, "logs", "-f"]
    
    # Add arguments directly from sys.argv instead of parsed args
    if len(sys.argv) > 2:  # If there are arguments after "logs"
        cmd.extend(sys.argv[2:])  # Take everything after "logs"
    
    print_progress(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def handle_exec_command(args):
    """Handle the exec command - execute commands in containers"""
    print_progress("Executing command in container...")
    
    # Default to mode C compose file
    compose_file = COMPOSE_FILES["C"]
    
    # Build exec command
    cmd = ["docker", "compose", "-f", compose_file, "exec"]
    if args.compose_args:
        cmd.extend(args.compose_args)
    else:
        print_error("Usage: ./start.py exec <service> <command>")
        print_info("Example: ./start.py exec shovel-web bash")
        sys.exit(1)
    
    print_progress(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

def handle_help_command(args):
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
  {Colors.CYAN}./start.py clear --output{Colors.END}                         # Clear only Suricata output
  {Colors.CYAN}./start.py status{Colors.END}                                 # Show container status
  {Colors.CYAN}./start.py logs{Colors.END}                                   # Follow all container logs
  {Colors.CYAN}./start.py logs shovel-webapp-1{Colors.END}                   # Follow specific container logs
  {Colors.CYAN}./start.py exec shovel-webapp-1 sh{Colors.END}                # Execute bash in container
  {Colors.CYAN}./start.py help{Colors.END}                                   # Show this help message
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Help command
    subparsers.add_parser("help", help="Show help information")

    # Start command
    parser_start = subparsers.add_parser("start", help="Start Shovel")
    mode_group = parser_start.add_mutually_exclusive_group()
    mode_group.add_argument("--mode-a", action="store_true", help="Start in mode A (pcap replay)")
    mode_group.add_argument("--mode-b", action="store_true", help="Start in mode B (capture interface)")
    mode_group.add_argument("--mode-c", action="store_true", help="Start in mode C (PCAP-over-IP)")
    
    parser_start.add_argument("--no-build", action="store_true", help="Skip building images")
    parser_start.add_argument("--date", dest="start_date", help="Specify CTF start date (format: YYYY-MM-DDThh:mm+ZZ:zz)")
    parser_start.add_argument("--target-ip", "-ip", dest="target_ip", help="Specify target machine IP address (for mode C)")
    parser_start.add_argument("--refresh-rate", "-r", dest="refresh_rate", help="Specify refresh rate (in seconds)")
    parser_start.add_argument("--tick-length", "-t", dest="tick_length", help="Specify tick length (in seconds)")
    parser_start.add_argument("--key", "-k", dest="key", help="Specify algorithm for SSH key exchange (default: ed25519)")

    # Stop command
    subparsers.add_parser("stop", help="Stop Shovel containers")

    # Clear command
    parser_clear = subparsers.add_parser("clear", help="Clean Suricata output and stop containers")
    parser_clear.add_argument(
        "--all", "-A", action="store_true", help="Clear everything (containers, output, config)"
    )
    parser_clear.add_argument(
        "--config", "-c", action="store_true", help="Clear config files (.env and services_config.json)"
    )
    parser_clear.add_argument(
        "--output", "-o", action="store_true", help="Clean Suricata output and stop containers"
    )

    # Status command - simple container status
    subparsers.add_parser("status", help="Show container status")

    subparsers.add_parser("logs", help="Follow container logs")

    # # Logs command - follow container logs
    # parser_logs = subparsers.add_parser("logs", help="Follow container logs")
    # parser_logs.add_argument(
    #     "compose_args",
    #     nargs=argparse.REMAINDER,
    #     help="Docker compose logs arguments (e.g., 'shovel-web', '--tail 100', '--since 1h')",
    #     default=[],
    # )

    # Exec command - execute commands in containers
    parser_exec = subparsers.add_parser("exec", help="Execute command in container")
    parser_exec.add_argument(
        "compose_args",
        nargs=argparse.REMAINDER,
        help="Container and command (e.g., 'shovel-web bash')",
        default=[],
    )

    return parser


def main():
    # Clear screen and show banner
    os.system('clear' if os.name == 'posix' else 'cls')
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
    
    # If no arguments provided, default to start
    if len(sys.argv) == 1:
        args = parser.parse_args(['start'])
    else:
        args = parser.parse_args()

    # Handle commands (logs is already handled above)
    if args.command == "help":
        handle_help_command(args)
    elif args.command == "start":
        handle_start_command(args)
    elif args.command == "stop":
        handle_stop_command(args)
    elif args.command == "clear":
        handle_clear_command(args)
    elif args.command == "status":
        handle_status_command(args)
    elif args.command == "exec":
        handle_exec_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()