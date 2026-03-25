import argparse
from pathlib import Path

# Dynamically map the path: src_folder -> parent_folder -> data -> blacklist
SRC_DIR = Path(__file__).resolve().parent
DEFAULT_BLACKLIST_FILE = SRC_DIR.parent / "data" / "blacklist" / "main_blacklist.txt"


def parse_arguments():
    main_desc = """
======================================================================
 SecTool: Security Port Scanner & Log Blacklist Analysis
======================================================================
A modular security utility designed for incident responders.
It provides secure port scanning and robust log extraction to hunt 
for malicious IP addresses using custom threat intelligence files.

Use 'python3 src/main.py <module> -h' for detailed help on a specific module.
"""

    scan_desc = """
Module: Port Scanner
----------------------------------------------------------------------
Securely scans a target IP address for open TCP ports.
Mimics Nmap output (PORT, STATE, SERVICE).

Examples:
  python3 src/main.py scan 192.168.1.1                 (Scans default ports 1-1024)
  python3 src/main.py scan 10.0.0.5 -p 22,80,443       (Scans specific ports)
  python3 src/main.py scan 127.0.0.1 -p 80-443         (Scans a specific port range)
  python3 src/main.py scan 8.8.8.8 -p 53 -w report.txt (Saves findings to a file)
"""

    check_desc = f"""
Module: Blacklist Checker
----------------------------------------------------------------------
Checks a single IP address OR extracts all IPs from a log file to see 
if they exist in a threat intelligence blacklist. 

Examples:
  python3 src/main.py check 8.8.8.8
  python3 src/main.py check data/samples/sample_auth.log
  python3 src/main.py check firewall.csv -t csv -b data/blacklist/blacklist.csv
"""

    parser = argparse.ArgumentParser(
        description=main_desc,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available modules: 'scan' or 'check'")

    # --- Scanner CLI ---
    scan_parser = subparsers.add_parser("scan", help="Scan open ports on a target IP", description=scan_desc,
                                        formatter_class=argparse.RawTextHelpFormatter)
    scan_parser.add_argument("ip", help="Target IP address to scan (e.g., 192.168.1.50)")
    scan_parser.add_argument("-p", "--ports", default="1-1024",
                             help="Port range (e.g., '22' or '1-1024'). Default: 1-1024")
    scan_parser.add_argument("-w", "--write", help="Path to save the output text file (e.g., scan_results.txt)")

    # --- Checker CLI ---
    check_parser = subparsers.add_parser("check", help="Check an IP or log file against a blacklist",
                                         description=check_desc, formatter_class=argparse.RawTextHelpFormatter)
    check_parser.add_argument("target", help="A single IP address OR the path to a log file")
    check_parser.add_argument("-t", "--type", choices=["text", "csv", "json"], default="text",
                              help="Format of the log file. Default: text")
    check_parser.add_argument("-b", "--blacklist", default=str(DEFAULT_BLACKLIST_FILE),
                              help=f"Path to the blacklist file. Default: {DEFAULT_BLACKLIST_FILE.name}")
    check_parser.add_argument("-w", "--write", help="Path to save the output text file")

    return parser.parse_args(), parser