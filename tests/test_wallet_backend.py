"""Wallet-RPC payload, isolation, recovery and backup unit tests.

Mocked RPC tests verify adapter behavior only. They do NOT certify real seed
restoration, receive, spend, network consensus or wallet-engine binaries.
"""
from pathlib import Path
from urllib.request import HTTPPasswordMgrWithDefaultRealm, Request
import json
import tempfile
import unittest
from unittest.mock import Mock, patch

from wallet_backend import WalletError, WalletRpc, WalletService, vmrx_amount, wallet_name, verify_vmrx_daemon, VMRX_GENESIS, NativeWalletDigestAuthHandler


class JsonResponse:
    def __init__(self, value):
        self.value = value
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def read(self, *_):
        return json.dumps(self.value).encode("utf-8")


class WalletUnitTests(unittest.TestCase):
    def rpc(self, result):
        client = WalletRpc(29782, "user", "secret")
        client.opener.open = Mock(return_value=JsonResponse({"jsonrpc": "2.0", "id": "vmrx", "result": result}))
        return client

    def test_native_digest_algorithm_header_is_unquoted_token(self):
        password_manager = HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, "http://127.0.0.1:29882/json_rpc", "test", "secret")
        handler = NativeWalletDigestAuthHandler(password_manager)
        request = Request("http://127.0.0.1:29882/json_rpc", data=b"{}", method="POST")
        value = handler.get_authorization(request, {"realm": "monero-rpc", "nonce": "nonce",
                                                    "algorithm": "MD5", "qop": "auth"})
        self.assertIn("algorithm=MD5", value)
        self.assertNotIn('algorithm="MD5"', value)
        self.assertIn("qop=auth", value)

    def test_rpc_only_loopback_and_digest(self):
        client = self.rpc({"address": "E" + "a" * 94})
        self.assertEqual(client.address(), "E" + "a" * 94)
        req = client.opener.open.call_args.args[0]
        self.assertEqual(req.full_url, "http://127.0.0.1:29782/json_rpc")
        self.assertEqual(json.loads(req.data)["method"], "get_address")

    def test_rpc_does_not_reflect_secret_on_http_failure(self):
        client = self.rpc({})
        client.opener.open.side_effect = OSError("MY_SUPER_SECRET_SEED should not leak")
        with self.assertRaises(WalletError) as caught:
            client.restore("wallet1", "password123456", "word " * 25)
        self.assertNotIn("MY_SUPER_SECRET", str(caught.exception))

    def test_invalid_method_rejected(self):
        with self.assertRaises(WalletError):
            self.rpc({}).call("get_private_keys")

    def test_name_does_not_allow_traversal(self):
        for name in ("../secret", "..", "/tmp/foo", "hello.ext", " space", "a" * 49):
            with self.subTest(name=name), self.assertRaises(WalletError):
                wallet_name(name)
        self.assertEqual(wallet_name("Wallet_01"), "Wallet_01")

    def test_amount_integer_precision(self):
        self.assertEqual(vmrx_amount("0.000000000001"), 1)
        self.assertEqual(vmrx_amount("1.25"), 1_250_000_000_000)
        for amount in ("-1", "NaN", "0", "1.0000000000001", "abc", "Infinity"):
            with self.subTest(amount=amount), self.assertRaises(WalletError):
                vmrx_amount(amount)

    def test_create_wallet_rpc_payload(self):
        client = self.rpc({})
        client.address = Mock(return_value="E" * 95)
        self.assertEqual(client.create("test1", "pw123456789012"), "E" * 95)
        req = json.loads(client.opener.open.call_args.args[0].data)
        self.assertEqual(req["method"], "create_wallet")
        self.assertEqual(req["params"]["filename"], "test1")
        self.assertEqual(req["params"]["language"], "English")

    def test_restore_rpc_uses_original_core_mnemonic(self):
        client = self.rpc({"address": "E" * 95})
        addr = client.restore("restore1", "pw123456789012", "word " * 25, 0)
        self.assertEqual(addr, "E" * 95)
        req = json.loads(client.opener.open.call_args.args[0].data)
        self.assertEqual(req["method"], "restore_deterministic_wallet")
        self.assertEqual(req["params"]["restore_height"], 0)
        self.assertEqual(len(req["params"]["seed"].split()), 25)

    def test_restore_rejects_short_seed_and_bad_height(self):
        client = self.rpc({})
        with self.assertRaises(WalletError):
            client.restore("wallet1", "password", "one two three")
        with self.assertRaises(WalletError):
            client.restore("wallet1", "password", "word " * 25, -1)

    def test_prepare_transaction_is_not_broadcast(self):
        client = self.rpc({"tx_metadata": "ab12cd34", "tx_hash": "dead", "fee": 210})
        tx = client.prepare_transfer("E" + "a" * 94, "0.5")
        self.assertEqual(tx["amount"], 500_000_000_000)
        self.assertEqual(tx["fee"], 210)
        req = json.loads(client.opener.open.call_args.args[0].data)
        self.assertEqual(req["method"], "transfer")
        self.assertTrue(req["params"]["do_not_relay"])
        self.assertTrue(req["params"]["get_tx_metadata"])

    def test_no_implicit_broadcast(self):
        client = self.rpc({"tx_metadata": "aabb"})
        client.prepare_transfer("E" + "a" * 94, "1")
        self.assertEqual(client.opener.open.call_count, 1)

    def test_vmrx_genesis_pin_only(self):
        with patch("urllib.request.build_opener") as make:
            make.return_value.open.return_value = JsonResponse({
                "result": {"block_header": {"hash": VMRX_GENESIS}}
            })
            verify_vmrx_daemon(29781)
            request = make.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, "http://127.0.0.1:29781/json_rpc")
        with patch("urllib.request.build_opener") as make:
            make.return_value.open.return_value = JsonResponse({
                "result": {"block_header": {"hash": "0" * 64}}
            })
            with self.assertRaises(WalletError):
                verify_vmrx_daemon(29781)

    def test_backup_copies_wallet_and_keys_without_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            original = Path(d, "original")
            original.mkdir()
            (original / "alice").write_bytes(b"wallet-cache")
            (original / "alice.keys").write_bytes(b"encrypted-private-key-file")
            backup = Path(d, "backup")
            service = WalletService()
            service.directory = original
            service.child = Mock()
            service.child.poll.return_value = None
            service.client = Mock()
            self.assertEqual(Path(service.backup("alice", str(backup))).resolve(), backup.resolve())
            self.assertEqual((backup / "alice.keys").read_bytes(), b"encrypted-private-key-file")
            service.client.store.assert_called_once()
            with self.assertRaises(WalletError):
                service.backup("alice", str(backup))

    def test_engine_does_not_auto_launch_and_binds_loopback(self):
        service = WalletService()
        self.assertIsNone(service.child)
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d, "vmrx-wallet-rpc")
            exe.write_bytes(b"test-placeholder")
            exe.chmod(0o700)
            with patch("wallet_backend.verify_vmrx_daemon") as verify, patch("subprocess.Popen") as popen:
                popen.return_value.pid = 1234
                popen.return_value.poll.return_value = None
                service.start(str(exe), str(Path(d, "wallets")), 29781)
                verify.assert_called_once_with(29781)
                argv = popen.call_args.args[0]
                self.assertEqual(argv[argv.index("--rpc-bind-ip") + 1], "127.0.0.1")
                self.assertEqual(argv[argv.index("--daemon-address") + 1], "127.0.0.1:29781")
                self.assertEqual(argv[argv.index("--rpc-bind-port") + 1], "29882")
                self.assertIn("--rpc-login", argv)
                self.assertNotIn("--disable-rpc-login", argv)
                self.assertFalse(popen.call_args.kwargs["shell"])


if __name__ == "__main__":
    unittest.main()
