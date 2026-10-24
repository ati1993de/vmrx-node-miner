import json
import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rpc_client import VMRXRpc, RpcError, valid_mining_address
from node_process import checked_peer

class Response:
    def __init__(self, value): self.value = value
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, *_): return json.dumps(self.value).encode()

class RPCClientTests(unittest.TestCase):
    def test_loopback_rpc_only(self):
        with patch('urllib.request.urlopen', return_value=Response({'status': 'OK', 'height': 69})) as req:
            x = VMRXRpc(29781).info()
            self.assertEqual(x['height'], 69)
            self.assertEqual(req.call_args.args[0].full_url, 'http://127.0.0.1:29781/get_info')
    def test_mining_payload(self):
        with patch('urllib.request.urlopen', return_value=Response({'status': 'OK'})) as req:
            VMRXRpc(29791).start_mining('E' + 'a'*94, 1)
            body = json.loads(req.call_args.args[0].data)
            self.assertEqual(body['threads_count'], 1)
            self.assertEqual(body['miner_address'], 'E' + 'a'*94)
            self.assertFalse(body['ignore_battery'])
    def test_busy_is_failure(self):
        with patch('urllib.request.urlopen', return_value=Response({'status': 'BUSY'})):
            with self.assertRaises(RpcError): VMRXRpc().start_mining('E' + 'a'*94, 1)
    def test_address_rejects_bad(self):
        self.assertFalse(valid_mining_address('bad'))
        self.assertFalse(valid_mining_address('E' + 'O'*94))
    def test_rpc_port_rejects(self):
        with self.assertRaises(ValueError): VMRXRpc(80)
    def test_peer_isolated(self):
        self.assertEqual(checked_peer(''), '127.0.0.1:1')
    def test_monero_peer_reject(self):
        with self.assertRaises(ValueError): checked_peer('getmonero.org:18080')

if __name__ == '__main__': unittest.main()
