"""Execute da raiz: python -B -m unittest discover -s SERS/testes -v.

Históricos temporários; nenhum atendimento fictício entra nos dados de uso.
"""

import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "pyhon"))

from SERS.energia import ModuloEnergia, carregar_cenario
from SERS.interface import atender_energia, ler_numero
from assistente import Assistente
from base_conhecimento import BaseConhecimento


class CalculosTest(unittest.TestCase):
    def setUp(self):
        self.modulo = ModuloEnergia()

    def test_cenario_padrao_conferido_manualmente(self):
        r = self.modulo.simular()
        atual, led, solar = r["alternativas"]
        self.assertAlmostEqual(atual["consumo_kwh_mes"], 45)
        self.assertAlmostEqual(led["consumo_kwh_mes"], 6.75)
        self.assertAlmostEqual(r["geracao_solar_potencial_kwh_mes"], 10.125)
        self.assertAlmostEqual(r["solar_util_kwh_mes"], 5.4)
        self.assertAlmostEqual(solar["rede_kwh_mes"], 1.35)
        self.assertAlmostEqual(atual["custo_primeiro_ano"], 540)
        self.assertAlmostEqual(led["custo_primeiro_ano"], 156)
        self.assertAlmostEqual(solar["custo_primeiro_ano"], 2691.20)
        self.assertAlmostEqual(r["ganho_solar_sobre_led_ano"], -35.20)
        self.assertAlmostEqual(led["retorno_simples_meses"], 75 / 38.25)
        self.assertEqual(r["menor_custo_primeiro_ano"], "LED na rede")

    def test_zero_uso_ou_tarifa_nao_promete_retorno(self):
        for ajustes in ({"horas_dia": 0}, {"tarifa_kwh": 0}):
            with self.subTest(ajustes=ajustes):
                r = self.modulo.simular(**ajustes)
                self.assertEqual(r["menor_custo_primeiro_ano"], "Situação atual")
                for a in r["alternativas"]:
                    self.assertIsNone(a["retorno_simples_meses"])

    def test_solar_limitado_por_consumo_geracao_e_bateria(self):
        for ajustes in (
            {"bateria_util_kwh": 0}, {"bateria_util_kwh": 0.01},
            {"hsp": 0}, {"hsp": 0.1}, {"quantidade": 100},
            {"quantidade": 1, "potencia_solar_kwp": 100},
            {"disponibilidade_solar": 0}, {"disponibilidade_solar": 1},
        ):
            with self.subTest(ajustes=ajustes):
                r = self.modulo.simular(**ajustes)
                util = r["solar_util_kwh_mes"]
                led, solar = r["alternativas"][1:]
                self.assertGreaterEqual(util, 0)
                self.assertLessEqual(util, led["consumo_kwh_mes"])
                self.assertLessEqual(util, r["geracao_solar_potencial_kwh_mes"])
                self.assertLessEqual(util, r["limite_bateria_kwh_mes"])
                self.assertAlmostEqual(util + solar["rede_kwh_mes"], led["consumo_kwh_mes"])

    def test_validacao_de_valores_e_equivalencia(self):
        for ajustes in (
            {"horas_dia": -1}, {"horas_dia": 25}, {"tarifa_kwh": float("nan")},
            {"tarifa_kwh": float("inf")}, {"quantidade": True}, {"quantidade": 1.5},
            {"quantidade": 0}, {"tarifa_kwh": "1"}, {"fluxo_led_lm": 500},
            {"disponibilidade_solar": 1.1}, {"rendimento_solar": -0.1}, {"erro": 1},
        ):
            with self.subTest(ajustes=ajustes), self.assertRaises(ValueError):
                self.modulo.simular(**ajustes)

    def test_recomendacao_muda_e_nao_altera_cenario(self):
        r = self.modulo.simular(preco_led=1000)
        self.assertEqual(r["menor_custo_primeiro_ano"], "Situação atual")
        self.assertEqual(self.modulo.simular()["parametros"]["preco_led"], 15)

    def test_cenario_sem_fonte_ou_premissa_e_recusado(self):
        for campo, valor in (("referencias", []), ("premissas", {}), ("parametros", None)):
            with self.subTest(campo=campo), tempfile.TemporaryDirectory() as pasta:
                cenario = dict(self.modulo.cenario)
                cenario[campo] = valor
                caminho = Path(pasta) / "cenario.json"
                caminho.write_text(json.dumps(cenario), encoding="utf-8")
                with self.assertRaises(ValueError):
                    carregar_cenario(caminho)


class IntegracaoTest(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.modulo = ModuloEnergia()
        self.base = BaseConhecimento(RAIZ / "pyhon/data/base_conhecimento.json")
        self.saida = io.StringIO()
        with redirect_stdout(self.saida):
            self.base.carregar(self.modulo.orientacoes())
        self.assistente = Assistente("Teste", self.base, self.temporario.name)

    def test_busca_categorias_e_base_antiga(self):
        self.assertEqual(len(self.base.orientacoes), 13)
        for pergunta, esperado in (("como tirar cpf", 2), ("vagas de emprego", 7),
                                  ("conta de luz", 101), ("lampadas led", 102),
                                  ("energia solar", 103)):
            with self.subTest(pergunta=pergunta):
                pontos, orientacao = self.base.buscar(pergunta)[0]
                self.assertGreaterEqual(pontos, 3)
                self.assertEqual(orientacao.id, esperado)
        self.assertEqual(len(self.base.por_categoria("Energia e sustentabilidade")), 3)
        with redirect_stdout(self.saida):
            self.base.carregar(self.modulo.orientacoes())
        self.assertEqual(len(self.base.orientacoes), 13)

    def test_simulacao_historico_indicadores_csv_e_reabertura(self):
        with patch("builtins.input", side_effect=["", "", "1,00", "s", "s", "1"]), redirect_stdout(self.saida):
            atender_energia(self.assistente, self.modulo)
        registro = self.assistente.historico[0]
        self.assertEqual(registro["origem"], "energia")
        self.assertEqual(registro["id_orientacao"], 101)
        self.assertTrue(registro["detalhes"]["avaliacao"]["compreendeu_estimativas"])
        self.assertAlmostEqual(registro["detalhes"]["resultado"]["solar_util_kwh_mes"], 5.4)
        with patch("builtins.input", return_value="4"), redirect_stdout(self.saida):
            self.assistente.indicadores()
            self.assistente.finalizar()
        self.assertIn("Atendimentos registrados: 1", self.saida.getvalue())
        novo = Assistente("Teste", self.base, self.temporario.name)
        self.assertEqual(novo.historico[0]["facilidade"], 4)
        with novo.caminho_csv.open(encoding="utf-8-sig", newline="") as arquivo:
            linha = next(csv.DictReader(arquivo))
        self.assertEqual(json.loads(linha["detalhes"])["resultado"], registro["detalhes"]["resultado"])

    def test_cancelamento_nao_grava_atendimento(self):
        with patch("builtins.input", side_effect=["", "v"]), redirect_stdout(self.saida):
            atender_energia(self.assistente, self.modulo)
        self.assertEqual(self.assistente.historico, [])
        self.assertFalse(self.assistente.caminho_historico.exists())

    def test_entrada_invalida_decimal_e_zero(self):
        with patch("builtins.input", side_effect=["nan", "inf", "-1", "25", "ana@example.com", "2,5"]), redirect_stdout(self.saida):
            self.assertEqual(ler_numero("Horas", 5, 0, 24), 2.5)
        with patch("builtins.input", return_value="0"):
            self.assertEqual(ler_numero("Horas", 5, 0, 24), 0)
        with patch("builtins.input", side_effect=["2.5", "3"]), redirect_stdout(self.saida):
            self.assertEqual(ler_numero("Quantidade", 5, 1, 100, True), 3)

    def test_pergunta_com_dados_pessoais_e_recusada(self):
        with patch("builtins.input", side_effect=["energia ana@example.com", "energia 1234 5678", "0"]), redirect_stdout(self.saida):
            self.assistente.perguntar()
        self.assertEqual(self.assistente.historico, [])

    def test_resposta_energia_por_pergunta_e_categoria(self):
        with patch("builtins.input", side_effect=["energia solar", "s"]), redirect_stdout(self.saida):
            self.assistente.perguntar()
        categoria = self.base.categorias().index("Energia e sustentabilidade") + 1
        with patch("builtins.input", side_effect=[str(categoria), "1", "s", "0", "0"]), redirect_stdout(self.saida):
            self.assistente.navegar()
        self.assertEqual([r["origem"] for r in self.assistente.historico], ["pergunta", "categoria"])
        self.assertIn("2691,20", self.saida.getvalue())
        self.assertIn("Referências:", self.saida.getvalue())

    def test_historico_legado_exporta_sem_detalhes(self):
        legado = {"data": "2026-11-10", "origem": "pergunta", "pergunta": "como tirar cpf",
                  "id_orientacao": 2, "encontrou": True, "ajudou": True,
                  "tentativas": 1, "tempo_segundos": 2, "facilidade": 5}
        self.assistente.caminho_historico.write_text(json.dumps([legado]), encoding="utf-8")
        novo = Assistente("Teste", self.base, self.temporario.name)
        with redirect_stdout(self.saida):
            novo.exportar_csv()
        with novo.caminho_csv.open(encoding="utf-8-sig", newline="") as arquivo:
            linha = next(csv.DictReader(arquivo))
        self.assertEqual(linha["detalhes"], "")
        self.assertEqual(novo.historico, [legado])


class ProgramaTest(unittest.TestCase):
    def test_programa_completo_de_qualquer_pasta_e_falha_isolada_sers(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            for nome in ("pyhon", "SERS"):
                shutil.copytree(RAIZ / nome, raiz / nome, ignore=shutil.ignore_patterns("__pycache__"))
            ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
            entradas = "5\n\n\n\ns\ns\n1\n1\ncomo tirar cpf\ns\n3\n4\n0\n5\n"
            processo = subprocess.run(
                [sys.executable, "-B", str(raiz / "pyhon/main.py")], cwd=raiz,
                input=entradas, text=True, encoding="utf-8", capture_output=True,
                env=ambiente, timeout=20,
            )
            self.assertEqual(processo.returncode, 0, processo.stderr)
            self.assertIn("2691,20", processo.stdout)
            self.assertIn("Fazer a inscrição no CPF", processo.stdout)
            self.assertIn("Obrigado por utilizar", processo.stdout)
            # Execução dentro de pyhon deve resolver o pacote irmão SERS.
            processo = subprocess.run(
                [sys.executable, "-B", "main.py"], cwd=raiz / "pyhon",
                input="5\nv\n0\n5\n", text=True, encoding="utf-8", capture_output=True,
                env=ambiente, timeout=20,
            )
            self.assertEqual(processo.returncode, 0, processo.stderr)
            self.assertIn("Simulação cancelada", processo.stdout)
            (raiz / "SERS/dados/cenario.json").write_text("{", encoding="utf-8")
            processo = subprocess.run(
                [sys.executable, "-B", str(raiz / "pyhon/main.py")], cwd=raiz,
                input="5\n1\ncomo tirar cpf\ns\n0\n5\n", text=True, encoding="utf-8",
                capture_output=True, env=ambiente, timeout=20,
            )
            self.assertEqual(processo.returncode, 0, processo.stderr)
            self.assertIn("SERS indisponível", processo.stdout)
            self.assertIn("Fazer a inscrição no CPF", processo.stdout)


if __name__ == "__main__":
    unittest.main()
