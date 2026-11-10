"""Carregamento de orientações e busca baseada em regras."""

import json
import re
import unicodedata
from pathlib import Path

from orientação import Orientacao


def normalizar(texto):
    """Minúsculas, sem acentos/pontuação e com espaços normalizados."""
    sem_acentos = unicodedata.normalize("NFKD", texto.lower())
    sem_acentos = "".join(
        caractere for caractere in sem_acentos
        if not unicodedata.combining(caractere)
    )
    palavras = re.findall(r"[a-z0-9]+", sem_acentos)
    return " " + " ".join(palavras) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []

    def carregar(self):
        try:
            with self.caminho.open("r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
            if not isinstance(registros, list):
                raise ValueError("O JSON precisa conter uma lista de orientações")
        except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError, ValueError) as erro:
            print(f"Não foi possível carregar a base: {erro}")
            self.orientacoes = []
            return False

        self.orientacoes = []
        ids_vistos = set()
        for indice, dados in enumerate(registros, 1):
            try:
                if not isinstance(dados, dict):
                    raise ValueError("O registro precisa ser um dicionário")
                orientacao = Orientacao(dados)
                if orientacao.id in ids_vistos:
                    raise ValueError("ID duplicado")
                self.orientacoes.append(orientacao)
                ids_vistos.add(orientacao.id)
            except (TypeError, ValueError) as erro:
                print(f"Aviso: ignorado registro {indice}: {erro}")

        print(f"Base carregada: {len(self.orientacoes)} orientações válidas.")
        return bool(self.orientacoes)

    def categorias(self):
        return sorted({orientacao.categoria for orientacao in self.orientacoes})

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta_norm = normalizar(pergunta)
        titulo_norm = set(normalizar(orientacao.titulo).split())
        pontos = 0

        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            # O uso de espaços nas bordas evita casar 'sus' dentro de outra palavra.
            if chave_norm.strip() and chave_norm in pergunta_norm:
                pontos += 3

        for palavra in set(pergunta_norm.split()):
            if len(palavra) >= 4 and palavra in titulo_norm:
                pontos += 1

        return pontos

    def buscar(self, pergunta):
        resultados = [(self.pontuar(pergunta, o), o) for o in self.orientacoes]
        return sorted(resultados, key=lambda item: item[0], reverse=True)