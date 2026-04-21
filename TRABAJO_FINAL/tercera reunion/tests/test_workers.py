"""
Tests para la lógica de workers.
"""
import unittest
from workers.validation import validar_reserva
from utils.exceptions import ValidationError


class TestValidacionReserva(unittest.TestCase):
    """Tests para validación de reservas"""

    def test_reserva_valida(self):
        """Test: reserva con datos válidos"""
        request = {
            "cliente_id": "cliente_001",
            "cancha_id": "cancha_1",
            "horario": "10:00-11:00",
            "precio": 50.0,
            "fecha": "2026-04-20"
        }

        # No debería lanzar excepción
        validar_reserva(request)

    def test_precio_negativo(self):
        """Test: precio negativo debe fallar"""
        request = {
            "cliente_id": "cliente_001",
            "cancha_id": "cancha_1",
            "horario": "10:00-11:00",
            "precio": -10.0,
            "fecha": "2026-04-20"
        }

        with self.assertRaises(ValidationError):
            validar_reserva(request)

    def test_falta_cancha_id(self):
        """Test: falta cancha_id debe fallar"""
        request = {
            "cliente_id": "cliente_001",
            "horario": "10:00-11:00",
            "precio": 50.0,
            "fecha": "2026-04-20"
        }

        with self.assertRaises(ValidationError):
            validar_reserva(request)


if __name__ == "__main__":
    unittest.main()
