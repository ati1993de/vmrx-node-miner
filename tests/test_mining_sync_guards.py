"""Regression tests: never mine on an isolated or unsynchronized VMRX node."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import app
from rpc_client import RpcError


class MiningPeerGateTests(unittest.TestCase):
    def make_job(self, info):
        pending = []
        view = SimpleNamespace(
            address=SimpleNamespace(get=lambda: "valid-vmrx-mining-address-test-only"),
            threads=SimpleNamespace(get=lambda: 1),
            rpc_port=SimpleNamespace(get=lambda: "29781"),
            background_mining=SimpleNamespace(get=lambda: False),
            _task=lambda name, fn: pending.append(fn),
        )
        client = MagicMock()
        client.info.return_value = info
        with (patch.object(app, "valid_mining_address", return_value=True),
              patch.object(app.messagebox, "askyesno", return_value=True),
              patch.object(app.VMRXRpc, return_value=client)):
            app.App.start_mining(view)
        self.assertEqual(len(pending), 1)
        return pending[0], client

    def test_zero_peers_mining_is_denied_even_if_flag_says_synced(self):
        job, client = self.make_job({
            "synchronized": True,
            "incoming_connections_count": 0,
            "outgoing_connections_count": 0,
        })
        with self.assertRaisesRegex(RpcError, "ISOLATED"):
            job()
        client.start_mining.assert_not_called()

    def test_unsynced_peer_connected_mining_is_denied(self):
        job, client = self.make_job({
            "synchronized": False,
            "incoming_connections_count": 0,
            "outgoing_connections_count": 1,
        })
        with self.assertRaisesRegex(RpcError, "not synchronized"):
            job()
        client.start_mining.assert_not_called()

    def test_sync_with_peer_allows_local_mining_rpc(self):
        job, client = self.make_job({
            "synchronized": True,
            "incoming_connections_count": 0,
            "outgoing_connections_count": 1,
        })
        self.assertIn("started", job())
        client.start_mining.assert_called_once_with(
            "valid-vmrx-mining-address-test-only", 1, False
        )


if __name__ == "__main__":
    unittest.main()
