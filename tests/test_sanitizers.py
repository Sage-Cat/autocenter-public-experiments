import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sanitize_adaptive_run import PrivacyMap  # noqa: E402
from sanitize_json import parse_replacements, sanitize  # noqa: E402


class PrivacyMapTests(unittest.TestCase):
    def test_private_ipv4_ranges_are_replaced_as_complete_addresses(self) -> None:
        privacy = PrivacyMap("private-run", "public-run")
        value = " ".join(
            ("10.1.2.3", "127.0.0.1", "169.254.2.3", "172.31.2.3", "192.168.2.3")
        )

        self.assertEqual(privacy.text(value), " ".join(["private-ip"] * 5))

    def test_public_ipv4_address_is_preserved(self) -> None:
        privacy = PrivacyMap("private-run", "public-run")

        self.assertEqual(privacy.text("198.51.100.7"), "198.51.100.7")


class GenericSanitizerTests(unittest.TestCase):
    def test_replacements_apply_recursively_to_keys_and_values(self) -> None:
        replacements = parse_replacements(["private=public"])

        self.assertEqual(
            sanitize({"private-key": ["private-value"]}, replacements),
            {"public-key": ["public-value"]},
        )

    def test_invalid_replacement_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_replacements(["missing-separator"])


if __name__ == "__main__":
    unittest.main()
