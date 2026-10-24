"""Ensure bundled-core discovery only selects a deliberate adjacent executable."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from node_process import find_bundled_daemon


class BundledCoreTest(unittest.TestCase):
    def test_no_core_means_manual_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_exe = Path(tmp) / "VMRX-Node-Miner.exe"
            with patch("node_process.sys.executable", str(fake_exe)), patch("node_process.sys.frozen", True, create=True):
                self.assertEqual(find_bundled_daemon(), "")

    def test_only_core_subdirectory_is_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "core" / "monerod.exe"
            candidate.parent.mkdir()
            candidate.write_bytes(b"test-only")
            candidate.chmod(0o755)
            with patch("node_process.sys.executable", str(root / "VMRX-Node-Miner.exe")), patch("node_process.sys.frozen", True, create=True):
                self.assertEqual(Path(find_bundled_daemon()).resolve(), candidate.resolve())

    def test_unrelated_executable_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "monerod.exe").write_bytes(b"wrong-directory")
            with patch("node_process.sys.executable", str(root / "VMRX-Node-Miner.exe")), patch("node_process.sys.frozen", True, create=True):
                self.assertEqual(find_bundled_daemon(), "")


if __name__ == "__main__":
    unittest.main()
