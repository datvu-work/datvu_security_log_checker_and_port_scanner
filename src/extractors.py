import csv
import json
from pathlib import Path
from abc import ABC, abstractmethod
from utils import is_valid_ip, IP_PATTERN

class LogExtractor(ABC):
    @abstractmethod
    def extract_ips(self, filepath: Path):
        pass

class TextLogExtractor(LogExtractor):
    def extract_ips(self, filepath: Path):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for match in IP_PATTERN.findall(line):
                    if is_valid_ip(match):
                        yield (match, line.strip(), line_num)

class CsvLogExtractor(LogExtractor):
    def extract_ips(self, filepath: Path):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            for line_num, row in enumerate(reader, 1):
                row_context = " | ".join(row)
                for cell in row:
                    for match in IP_PATTERN.findall(cell):
                        if is_valid_ip(match):
                            yield (match, row_context, line_num)

class JsonLogExtractor(LogExtractor):
    def extract_ips(self, filepath: Path):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                data = json.load(f)
                yield from self._parse_node(data, "JSON Data Block", "N/A")
            except json.JSONDecodeError:
                f.seek(0)
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            yield from self._parse_node(data, line.strip(), line_num)
                        except json.JSONDecodeError:
                            continue

    def _parse_node(self, node, context_str, line_num):
        if isinstance(node, dict):
            for val in node.values():
                yield from self._parse_node(val, context_str, line_num)
        elif isinstance(node, list):
            for item in node:
                yield from self._parse_node(item, context_str, line_num)
        elif isinstance(node, str):
            for match in IP_PATTERN.findall(node):
                if is_valid_ip(match):
                    yield (match, context_str, line_num)