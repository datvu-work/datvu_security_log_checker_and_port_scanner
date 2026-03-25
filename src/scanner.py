import socket
import concurrent.futures
from utils import COLORS, OutputLogger


def get_service_name(port: int) -> str:
    try:
        return socket.getservbyport(port, 'tcp')
    except OSError:
        return "unknown"


def scan_single_port(ip: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        result = s.connect_ex((ip, port))
        state = "open" if result == 0 else "closed"
        return port, state


def run_port_scanner(ip: str, ports: list, logger: OutputLogger):
    logger.print_msg(f"[*] Starting scan on {ip} for {len(ports)} ports...")

    results = []
    open_ports = 0
    closed_ports = 0
    max_threads = min(50, len(ports))

    # Multi-threading remains intact here
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_single_port, ip, p): p for p in ports}
        for future in concurrent.futures.as_completed(futures):
            try:
                port, state = future.result()
                results.append((port, state))
                if state == "open":
                    open_ports += 1
                else:
                    closed_ports += 1
            except Exception:
                closed_ports += 1

    results.sort(key=lambda x: x[0])

    if open_ports == 0 and len(ports) > 20:
        logger.print_msg(f"[-] All {len(ports)} scanned ports are closed.", COLORS.RED)
        return

    logger.print_msg("")
    logger.print_msg(f"{'PORT':<9} {'STATE':<7} {'SERVICE'}")

    show_closed = len(ports) <= 20

    if not show_closed and closed_ports > 0:
        logger.print_msg(f"Not shown: {closed_ports} closed tcp ports (conn-refused)", COLORS.YELLOW)

    for port, state in results:
        if state == "closed" and not show_closed:
            continue

        service = get_service_name(port)
        port_str = f"{port}/tcp"

        row_text = f"{port_str:<9} {state:<7} {service}"
        row_color = COLORS.GREEN if state == "open" else COLORS.RED
        logger.print_msg(row_text, row_color)

    logger.print_msg(f"\n[*] Scan complete. Found {open_ports} open ports.")