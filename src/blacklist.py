import csv
import json
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from utils import is_valid_ip, COLORS, OutputLogger


class BlacklistProvider(ABC):
    @abstractmethod
    def is_blacklisted(self, ip: str) -> bool:
        pass


class FileBlacklist(BlacklistProvider):
    def __init__(self, filepath: str, logger: OutputLogger):
        self.blacklist_set = set()
        self.logger = logger
        self._load_file(filepath)

    def _load_file(self, filepath: str):
        path = Path(filepath).resolve()
        if not path.is_file():
            self.logger.print_msg(f"[-] Error: Blacklist file not found at {path}", COLORS.RED)
            sys.exit(1)

        try:
            ext = path.suffix.lower()
            if ext == '.json':
                self._load_json(path)
            elif ext == '.csv':
                self._load_csv(path)
            else:
                self._load_txt(path)
        except Exception as e:
            self.logger.print_msg(f"[-] Error reading blacklist securely: {e}", COLORS.RED)
            sys.exit(1)

    def _load_txt(self, path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                ip = line.strip()
                if is_valid_ip(ip):
                    self.blacklist_set.add(ip)

    def _load_csv(self, path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    ip = cell.strip()
                    if is_valid_ip(ip):
                        self.blacklist_set.add(ip)

    def _load_json(self, path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._extract_ips_from_json_node(data)

    def _extract_ips_from_json_node(self, node):
        if isinstance(node, dict):
            for val in node.values():
                self._extract_ips_from_json_node(val)
        elif isinstance(node, list):
            for item in node:
                self._extract_ips_from_json_node(item)
        elif isinstance(node, str):
            if is_valid_ip(node):
                self.blacklist_set.add(node.strip())

    def is_blacklisted(self, ip: str) -> bool:
        return ip in self.blacklist_set