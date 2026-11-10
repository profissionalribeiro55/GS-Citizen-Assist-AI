"""Fluxo de atendimento, histórico, indicadores e CSV."""

import csv
import json
import time
from datetime import datetime
from pathlib import Path


class Assistente:
    CAMPOS_CSV = (
        "data", "origem", "pergunta", "id_orientacao", "encontrou",
        "ajudou", "tentativas", "tempo_segundos", "facilidade"
    )

    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.pasta_dados = Path(__file__).resolve().parent / "data"
        self.pasta_dados.mkdir(parents=True, exist_ok=True)
        self.caminho_historico = self.pasta_dados / "historico.json"
        self.caminho_csv = self.pasta_dados / "atendimentos.csv"
        self.historico = []
        self.registros_sessao = []
        self._carregar_historico()

    @staticmethod
    def contem_dados_pessoais(pergunta):
        # Regra exigida pelo PDF: @ ou 8 dígitos no total, mesmo separados.
        return "@" in pergunta or sum(c.isdigit() for c in pergunta) >= 8

    @staticmethod
    def _opcao(numero_maximo, texto="Escolha: "):
        while True:
            entrada = input(texto).strip()
            if entrada.isdigit() and 0 <= int(entrada) <= numero_maximo:
                return int(entrada)
            print(f"Entrada inválida. Digite um número entre 0 e {numero_maximo}.")

    @staticmethod
    def _sim_nao(texto):
        while True:
            resposta = input(texto).strip().lower()
            if resposta in ("s", "n"):
                return resposta == "s"
            print("Resposta inválida. Digite s para sim ou n para não.")

    def _carregar_historico(self):
        try:
            with self.caminho_historico.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list):
                raise ValueError("O histórico deve ser uma lista")
            self.historico = [item for item in dados if isinstance(item, dict)]
        except FileNotFoundError:
            self.historico = []
        except (OSError, json.JSONDecodeError, ValueError) as erro:
            print(f"Aviso: histórico indisponível ({erro}). Um novo histórico será iniciado.")
            self.historico = []

    def _salvar_historico(self):
        try:
            with self.caminho_historico.open("w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"Erro ao salvar histórico: {erro}")

    def registrar(self, origem, pergunta, orientacao, encontrou, ajudou, tentativas, inicio):
        if self.contem_dados_pessoais(pergunta):
            print("Atendimento com dados pessoais recusado e NÃO registrado.")
            return

        registro = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao.id if orientacao else None,
            "encontrou": bool(encontrou),
            "ajudou": bool(ajudou),
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
            "facilidade": None,
        }
        self.historico.append(registro)
        self.registros_sessao.append(registro)
        self._salvar_historico()

    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                if tentativas and ultima_pergunta:
                    self.registrar("pergunta", ultima_pergunta, None, False, False, tentativas, inicio)
                return
            if not pergunta:
                print("A pergunta não pode ficar vazia.")
                continue
            if self.contem_dados_pessoais(pergunta):
                print("Atenção: NÃO digite CPF, telefone ou e-mail. Reescreva a pergunta.")
                continue

            tentativas += 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)
            if not resultados or resultados[0][0] < 3:
                print("Não encontrei uma orientação. Tente outras palavras ou consulte as categorias.")
                continue

            pontos, orientacao = resultados[0]
            confianca = "ALTA" if pontos >= 6 else "MÉDIA"
            print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
            orientacao.exibir()

            alternativas = [(p, o) for p, o in resultados[1:] if p >= 3][:2]
            if alternativas:
                print("Outras orientações relacionadas:")
                for p, o in alternativas:
                    print(f"  - {o.titulo} ({p} pontos)")

            ajudou = self._sim_nao("Essa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("pergunta", pergunta, orientacao, True, ajudou, tentativas, inicio)
            return

    def navegar(self):
        inicio = time.time()
        while True:
            categorias = self.base.categorias()
            if not categorias:
                print("A base de conhecimento está vazia.")
                return

            print("\n=== CATEGORIAS ===")
            for indice, categoria in enumerate(categorias, 1):
                print(f"[{indice}] {categoria}")
            print("[0] Voltar")
            escolha = self._opcao(len(categorias))
            if escolha == 0:
                return
            categoria = categorias[escolha - 1]

            while True:
                orientacoes = self.base.por_categoria(categoria)
                print(f"\n=== {categoria.upper()} ===")
                for indice, orientacao in enumerate(orientacoes, 1):
                    print(f"[{indice}] {orientacao.titulo}")
                print("[0] Voltar")
                escolha_orientacao = self._opcao(len(orientacoes))
                if escolha_orientacao == 0:
                    break

                orientacao = orientacoes[escolha_orientacao - 1]
                orientacao.exibir()
                ajudou = self._sim_nao("Essa orientação respondeu sua dúvida? (s/n): ")
                self.registrar(
                    "categoria", orientacao.titulo, orientacao,
                    True, ajudou, 1, inicio
                )
                inicio = time.time()

    def indicadores(self):
        print("\n=== INDICADORES ===")
        total = len(self.historico)
        if total == 0:
            print("Nenhum atendimento registrado ainda.")
            return

        encontrados = sum(1 for r in self.historico if r.get("encontrou"))
        ajudaram = sum(1 for r in self.historico if r.get("ajudou"))
        tempo = sum(float(r.get("tempo_segundos") or 0) for r in self.historico)
        tentativas = sum(int(r.get("tentativas") or 0) for r in self.historico)
        notas = [r["facilidade"] for r in self.historico
                 if isinstance(r.get("facilidade"), int) and 1 <= r["facilidade"] <= 5]

        print(f"Atendimentos registrados: {total}")
        print(f"Resposta encontrada: {100 * encontrados / total:.1f}%")
        print(f"Taxa de acerto (ajudou): {100 * ajudaram / total:.1f}%")
        print(f"Tempo médio: {tempo / total:.1f} segundos")
        print(f"Tentativas por atendimento: {tentativas / total:.2f}")
        print(f"Facilidade média (1–5): {sum(notas) / len(notas):.2f}" if notas
              else "Facilidade média: ainda sem avaliações")
        print("\nDúvidas sem solução:")
        pendentes = [r["pergunta"] for r in self.historico
                     if not r.get("encontrou") or not r.get("ajudou")]
        if not pendentes:
            print("  - Nenhuma")
        else:
            for pergunta in dict.fromkeys(pendentes):
                print(f"  - {pergunta}")

    def exportar_csv(self):
        try:
            with self.caminho_csv.open("w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=self.CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
            print(f"CSV exportado: {self.caminho_csv}")
        except OSError as erro:
            print(f"Erro ao exportar CSV: {erro}")

    def finalizar(self):
        print("\nAntes de sair, avalie a facilidade de uso do assistente.")
        while True:
            entrada = input("Nota de 1 a 5: ").strip()
            if entrada in ("1", "2", "3", "4", "5"):
                nota = int(entrada)
                break
            print("Nota inválida. Digite um número de 1 a 5.")

        for registro in self.registros_sessao:
            registro["facilidade"] = nota
        if self.registros_sessao:
            self._salvar_historico()
        self.exportar_csv()
        print("Obrigado por utilizar o Citizen Assist AI!")
