#!/usr/bin/env python3
import sys
from pathlib import Path

# --- ROBUST IMPORT FIX ---
# Dynamically add the 'src' directory to sys.path so Python can find our modules
# no matter where the user runs the script from.
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# -------------------------

# Now we can import directly without 'src.' prefixes
from cli import parse_arguments
from scanner import run_port_scanner
from checker import run_blacklist_check
from utils import OutputLogger, COLORS, is_valid_ip, parse_port_range


def main():
    args, parser = parse_arguments()

    filepath = getattr(args, 'write', None)
    logger = OutputLogger(filepath)

    if args.command == "scan":
        if not is_valid_ip(args.ip):
            logger.print_msg("[-] Error: Invalid target IP address.", COLORS.RED)
            sys.exit(1)

        ports = parse_port_range(args.ports, logger)
        run_port_scanner(args.ip, ports, logger)
        logger.print_file_summary()

    elif args.command == "check":
        run_blacklist_check(args.target, args.type, args.blacklist, logger)
        logger.print_file_summary()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()