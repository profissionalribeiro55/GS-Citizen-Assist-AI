"""Testes da regra, das representações e da interface de terminal."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from computer import main as modulo


class TestDecisao(unittest.TestCase):
    def test_todas_as_combinacoes(self):
        esperado = [(0, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 1, 1, 1),
                    (1, 0, 0, 0), (1, 0, 1, 0), (1, 1, 0, 0), (1, 1, 1, 0)]
        self.assertEqual(modulo.tabela_verdade(), esperado)
        for p, r, f, s in esperado:
            with self.subTest(p=p, r=r, f=f):
                self.assertEqual(modulo.forma_canonica(p, r, f), s)
                self.assertEqual(modulo.pela_condicao_de_bloqueio(p, r, f), s)
                self.assertIn(f"S = {s}", modulo.orientacao(p, r, f))

    def test_mapa_na_ordem_gray(self):
        self.assertEqual(modulo.mapa_karnaugh(), [[0, 0, 1, 0], [0, 0, 0, 0]])

    def test_rejeita_valores_invalidos_em_todas_as_posicoes(self):
        for valor in (-1, 2, 0.0, 1.0, "0", "sim", None, [], float("nan")):
            for posicao in range(3):
                entradas = [0, 1, 1]
                entradas[posicao] = valor
                with self.subTest(valor=valor, posicao=posicao):
                    with self.assertRaises(ValueError):
                        modulo.decidir(*entradas)

    def executar_menu(self, entradas):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), redirect_stdout(saida):
            modulo.main()
        return saida.getvalue()

    def test_menu_invalido_e_consulta_com_correcao(self):
        saida = self.executar_menu(["99", "1", "sim", "2", "", " 0 ", "1", "1", "0"])
        self.assertIn("Opção inválida", saida)
        self.assertEqual(saida.count("Entrada inválida"), 3)
        self.assertIn("S = 1 — Orientação autorizada", saida)

    def test_cancelamento_e_encerramento(self):
        self.assertIn("Consulta cancelada", self.executar_menu(["1", "v", "0"]))
        self.assertIn("encerrado pelo usuário", self.executar_menu([EOFError()]))
        self.assertIn("encerrado pelo usuário", self.executar_menu([KeyboardInterrupt()]))

    def test_opcoes_didaticas_e_verificacao(self):
        saida = self.executar_menu(["2", "3", "4", "5", "0"])
        for trecho in ("TABELA-VERDADE", "Σm(3)", "De Morgan", "dupla negação", "G1", "8/8"):
            self.assertIn(trecho, saida)

    def test_bloqueio_informa_todos_os_motivos(self):
        mensagem = modulo.orientacao(1, 0, 0)
        for trecho in ("Dados pessoais identificados", "Resposta não encontrada", "Fonte não verificada"):
            self.assertIn(trecho, mensagem)


if __name__ == "__main__":
    unittest.main()
