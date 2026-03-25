#!/usr/bin/env python3
import sys
import os
import unittest
import tempfile
from pathlib import Path

# --- ROBUST IMPORT FIX FOR TESTS ---
# Dynamically add the 'src' directory to sys.path so tests can find the modules
TEST_DIR = Path(__file__).resolve().parent
SRC_DIR = TEST_DIR.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# -----------------------------------

from utils import is_valid_ip, parse_port_range, OutputLogger
from extractors import TextLogExtractor
from blacklist import FileBlacklist


class TestSecToolUtilities(unittest.TestCase):

    def setUp(self):
        """Set up a dummy logger to suppress actual file writing during tests."""
        self.dummy_logger = OutputLogger(filepath=None)

    def test_is_valid_ip(self):
        """Test the IP validation math securely."""
        # Valid IPs
        self.assertTrue(is_valid_ip("192.168.1.1"))
        self.assertTrue(is_valid_ip("10.0.0.5"))
        self.assertTrue(is_valid_ip("2001:db8::1"))  # IPv6 Support

        # Invalid IPs
        self.assertFalse(is_valid_ip("256.256.256.256"))  # Out of bounds
        self.assertFalse(is_valid_ip("192.168.1"))  # Incomplete
        self.assertFalse(is_valid_ip("not_an_ip"))  # String injection attempt
        self.assertFalse(is_valid_ip("127.0.0.1; rm -rf /"))  # Command injection attempt

    def test_parse_port_range(self):
        """Test the port range parser and bounds checking."""
        # Valid ranges
        self.assertEqual(parse_port_range("80", self.dummy_logger), [80])
        self.assertEqual(parse_port_range("22-25", self.dummy_logger), [22, 23, 24, 25])

        # Invalid ranges should trigger sys.exit(1)
        with self.assertRaises(SystemExit) as cm:
            parse_port_range("70000", self.dummy_logger)  # Out of bounds (Max 65535)
        self.assertEqual(cm.exception.code, 1)

        with self.assertRaises(SystemExit) as cm:
            parse_port_range("abc", self.dummy_logger)  # Non-integer injection
        self.assertEqual(cm.exception.code, 1)


class TestSecToolExtractorsAndBlacklist(unittest.TestCase):

    def setUp(self):
        """Create temporary files for testing to ensure no garbage is left on the OS."""
        self.dummy_logger = OutputLogger(filepath=None)

        # Create a temporary Log file
        self.temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_log.write("May 14 08:31:02 server sshd[1]: Failed password from 103.45.67.89 port 22\n")
        self.temp_log.write("May 14 08:32:00 server sshd[1]: Accepted publickey from 192.168.1.50\n")
        self.temp_log.close()

        # Create a temporary Blacklist file (TXT)
        self.temp_blacklist = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        self.temp_blacklist.write("103.45.67.89\n")  # Malicious IP
        self.temp_blacklist.write("8.8.8.8\n")  # Malicious IP
        self.temp_blacklist.close()

    def tearDown(self):
        """Clean up temporary files securely after tests."""
        os.unlink(self.temp_log.name)
        os.unlink(self.temp_blacklist.name)

    def test_text_log_extractor(self):
        """Test that the generator correctly extracts IPs without loading the whole file."""
        extractor = TextLogExtractor()
        results = list(extractor.extract_ips(Path(self.temp_log.name)))

        # We expect 2 IPs extracted from the 2 lines
        self.assertEqual(len(results), 2)

        # The generator yields tuples: (IP, Log_Context, Line_Number)
        ip1, context1, line1 = results[0]
        self.assertEqual(ip1, "103.45.67.89")
        self.assertEqual(line1, 1)
        self.assertTrue("Failed password" in context1)

    def test_file_blacklist_loading(self):
        """Test that the Blacklist dynamically loads IPs securely."""
        blacklist = FileBlacklist(self.temp_blacklist.name, self.dummy_logger)

        self.assertTrue(blacklist.is_blacklisted("103.45.67.89"))
        self.assertTrue(blacklist.is_blacklisted("8.8.8.8"))

        # 192.168.1.50 is in the log file, but NOT in the blacklist
        self.assertFalse(blacklist.is_blacklisted("192.168.1.50"))


if __name__ == '__main__':
    # Add verbosity for cleaner output during CI/CD pipelines
    unittest.main(verbosity=2)