"""
Tests para handlers de cliente.
"""
import unittest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from server.handlers import handle_client


class TestHandleClient(unittest.TestCase):
    """Tests para handle_client"""

    def test_json_valido(self):
        """Test: procesar JSON válido"""
        # TODO: mock asyncio readers/writers
        pass

    def test_json_invalido(self):
        """Test: rechazar JSON inválido"""
        # TODO: mock asyncio readers/writers
        pass


if __name__ == "__main__":
    unittest.main()
