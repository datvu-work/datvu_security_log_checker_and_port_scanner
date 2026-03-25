import sys
from pathlib import Path
from utils import is_valid_ip, COLORS, OutputLogger
from blacklist import FileBlacklist
from extractors import TextLogExtractor, CsvLogExtractor, JsonLogExtractor


def run_blacklist_check(target: str, log_type: str, blacklist_path: str, logger: OutputLogger):
    logger.print_msg(f"[*] Loading blacklist from: {blacklist_path}")
    blacklist = FileBlacklist(blacklist_path, logger)

    if is_valid_ip(target):
        logger.print_msg(f"[*] Checking single IP: {target}")
        if blacklist.is_blacklisted(target):
            logger.print_msg(f"1. [!] ALERT: IP {target} is BLACKLISTED.", COLORS.RED)
        else:
            logger.print_msg(f"[+] IP {target} is clean.", COLORS.GREEN)
        return

    log_path = Path(target).resolve()
    if not log_path.is_file():
        logger.print_msg(f"[-] Error: Target is neither a valid IP nor a found file: {target}", COLORS.RED)
        sys.exit(1)

    logger.print_msg(f"[*] Analyzing {log_type.upper()} log: {log_path.name}")
    logger.print_msg("-" * 60)

    if log_type == 'csv':
        extractor = CsvLogExtractor()
    elif log_type == 'json':
        extractor = JsonLogExtractor()
    else:
        extractor = TextLogExtractor()

    unique_malicious_ips = set()
    total_ips_scanned = 0
    hits_found = 0

    try:
        for ip, log_context, line_num in extractor.extract_ips(log_path):
            total_ips_scanned += 1
            if blacklist.is_blacklisted(ip):
                unique_malicious_ips.add(ip)
                hits_found += 1

                logger.print_msg(f"{hits_found}. [!] MATCH FOUND: {ip} (Line {line_num})", COLORS.RED)
                logger.print_msg(f"    Context : {log_context}")
                logger.print_msg("-" * 60)

        logger.print_msg(f"[*] Scan complete. Checked {total_ips_scanned} IP instances.")
        if not hits_found:
            logger.print_msg(f"[+] No blacklisted IPs found in the log file.", COLORS.GREEN)
        else:
            logger.print_msg(
                f"[!] Summary: Found {hits_found} log entries containing {len(unique_malicious_ips)} unique malicious IPs.",
                COLORS.RED)

    except PermissionError:
        logger.print_msg(f"[-] Error: Permission denied reading the log file.", COLORS.RED)
    except Exception as e:
        logger.print_msg(f"[-] Error processing log file securely: {e}", COLORS.RED)