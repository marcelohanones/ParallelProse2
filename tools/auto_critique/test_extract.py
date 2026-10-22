"""T1: extração por marcadores, sem chamada ao modelo."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver import extract  # noqa: E402


class ExtractTest(unittest.TestCase):
    def test_pega_so_o_trecho_entre_marcadores(self):
        self.assertEqual(extract("<<<MSG\nolá dsh\nMSG>>>"), "olá dsh")

    def test_status_fora_dos_marcadores_nao_entra(self):
        texto = "Status: enviando ao dsh\n<<<MSG\nX\nMSG>>>\nfim"
        self.assertEqual(extract(texto), "X")

    def test_sem_marcador_recusa(self):
        self.assertIsNone(extract("só texto, sem marcador"))

    def test_marcador_sem_fechamento_recusa(self):
        self.assertIsNone(extract("<<<MSG\nX sem fechar"))

    def test_trecho_vazio_recusa(self):
        self.assertIsNone(extract("<<<MSG\n   \nMSG>>>"))

    def test_entrada_nula_recusa(self):
        self.assertIsNone(extract(None))


if __name__ == "__main__":
    unittest.main()
