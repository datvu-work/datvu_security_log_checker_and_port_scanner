import re
import sys
import threading
import ipaddress
from pathlib import Path

# Regex for rough IP extraction
IP_PATTERN = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')


class COLORS:
    """ANSI Color Codes for Linux CLI"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'


class OutputLogger:
    """Handles thread-safe console printing and clean file exporting."""

    def __init__(self, filepath=None):
        self.lock = threading.Lock()
        self.filepath = filepath

        if self.filepath:
            path = Path(self.filepath).resolve()
            if path.is_dir():
                print(f"{COLORS.RED}[-] Error: Output path is a directory, please specify a file.{COLORS.RESET}")
                sys.exit(1)
            try:
                # Initialize and clear the file securely
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("--- SecTool Automated Report ---\n\n")
            except PermissionError:
                print(f"{COLORS.RED}[-] Error: Permission denied writing to {path}{COLORS.RESET}")
                sys.exit(1)
            self.filepath = path

    def print_msg(self, text: str, color: str = None):
        """Prints color to terminal, but writes clean plain-text to the file safely."""
        with self.lock:
            # 1. Console Output
            if color:
                print(f"{color}{text}{COLORS.RESET}")
            else:
                print(text)

            # 2. File Output (Clean ASCII, no color codes)
            if self.filepath:
                try:
                    with open(self.filepath, 'a', encoding='utf-8') as f:
                        f.write(text + "\n")
                except Exception:
                    pass

    def print_file_summary(self):
        """Prints the final file write confirmation to the console only."""
        if self.filepath:
            print(f"{COLORS.GREEN}[*] Successfully wrote into [{self.filepath.name}]{COLORS.RESET}")


def is_valid_ip(ip_str: str) -> bool:
    """Securely validate if a string is a valid IPv4/IPv6 address."""
    try:
        ipaddress.ip_address(ip_str.strip())
        return True
    except ValueError:
        return False


def parse_port_range(port_str: str, logger: OutputLogger) -> list:
    """Safely parse port ranges (e.g., '80' or '1-1024')."""
    ports = []
    try:
        if '-' in port_str:
            start, end = map(int, port_str.split('-'))
            if start < 1 or end > 65535 or start > end:
                raise ValueError
            ports = list(range(start, end + 1))
        else:
            port = int(port_str)
            if port < 1 or port > 65535:
                raise ValueError
            ports = [port]
    except ValueError:
        logger.print_msg("[-] Error: Invalid port range. Use 1-65535.", COLORS.RED)
        sys.exit(1)
    return ports