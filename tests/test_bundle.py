"""Release-layout tests: bundled VMRX Core must be discoverable without PATH/network."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import node_process


class BundledNodeTests(unittest.TestCase):
    def test_no_bundled_daemon_is_not_silently_substituted(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_gui = Path(tmp) / "VMRX-Node-Miner.exe"
            with patch.object(node_process.sys, "frozen", True, create=True), patch.object(node_process.sys, "executable", str(fake_gui)):
                self.assertEqual(node_process.find_bundled_daemon(), "")

    def test_detects_bundled_core_next_to_gui(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_gui = Path(tmp) / "VMRX-Node-Miner.exe"
            core = Path(tmp) / "core"
            core.mkdir()
            daemon = core / "vmrxd.exe"
            daemon.write_bytes(b"test fixture, never executed")
            daemon.chmod(0o755)
            with patch.object(node_process.sys, "frozen", True, create=True), patch.object(node_process.sys, "executable", str(fake_gui)):
                self.assertEqual(node_process.find_bundled_daemon(), str(daemon.resolve()))

    def test_local_ports_and_priority_peers(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / ("vmrxd.exe" if os.name == "nt" else "vmrxd")
            exe.write_bytes(b"fixture")
            exe.chmod(0o755)
            args = node_process.build_args(str(exe), str(Path(tmp) / "chain"), 29781, 29780, "31.70.81.5:29780")
            self.assertIn("127.0.0.1", args)
            self.assertIn("--add-priority-node", args)
            self.assertNotIn("--add-exclusive-node", args)
            self.assertIn("31.70.81.5:29780", args)
            self.assertIn("217.154.93.20:29780", args)
            self.assertEqual(args.count("--add-priority-node"), 2)


if __name__ == "__main__":
    unittest.main()
