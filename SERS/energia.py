"""Modelo didático de iluminação: cálculos puros, fontes e respostas comuns."""

import json
import math
from copy import deepcopy
from pathlib import Path


CAMINHO_CENARIO = Path(__file__).resolve().parent / "dados" / "cenario.json"

# Limites do protótipo residencial, não limites técnicos universais.
LIMITES = {
    "quantidade": (1, 100), "potencia_atual_w": (0.1, 1000),
    "potencia_led_w": (0.1, 1000), "fluxo_atual_lm": (1, 100000),
    "fluxo_led_lm": (1, 100000), "horas_dia": (0, 24),
    "dias_mes": (1, 31), "meses": (12, 12), "tarifa_kwh": (0, 10),
    "preco_led": (0, 10000), "custo_solar": (0, 1000000),
    "manutencao_solar_ano": (0, 100000), "potencia_solar_kwp": (0, 100),
    "hsp": (0, 24), "rendimento_solar": (0, 1),
    "bateria_util_kwh": (0, 1000), "disponibilidade_solar": (0, 1),
}


def validar_parametros(parametros):
    if not isinstance(parametros, dict):
        raise ValueError("Parâmetros devem ser um objeto JSON.")
    for nome, (minimo, maximo) in LIMITES.items():
        valor = parametros.get(nome)
        if (isinstance(valor, bool) or not isinstance(valor, (int, float))
                or not math.isfinite(valor) or not minimo <= valor <= maximo):
            raise ValueError(f"{nome}: informe um número entre {minimo} e {maximo}.")
    for nome in ("quantidade", "dias_mes", "meses"):
        if int(parametros[nome]) != parametros[nome]:
            raise ValueError(f"{nome} deve ser inteiro.")
    if parametros["fluxo_led_lm"] < parametros["fluxo_atual_lm"]:
        raise ValueError("A LED deve atender ao menos ao fluxo luminoso de referência.")


def carregar_cenario(caminho=CAMINHO_CENARIO):
    with Path(caminho).open(encoding="utf-8") as arquivo:
        cenario = json.load(arquivo)
    if not isinstance(cenario, dict):
        raise ValueError("Cenário deve ser um objeto JSON.")
    validar_parametros(cenario.get("parametros"))
    for nome in ("versao", "data_referencia", "publico", "necessidade", "origem"):
        if not isinstance(cenario.get(nome), str) or not cenario[nome].strip():
            raise ValueError(f"Cenário sem {nome}.")
    premissas = cenario.get("premissas")
    if not isinstance(premissas, dict) or any(
        not isinstance(premissas.get(nome), str) or not premissas[nome].strip()
        for nome in LIMITES
    ):
        raise ValueError("Cada parâmetro precisa de uma premissa documentada.")
    referencias = cenario.get("referencias")
    if not isinstance(referencias, list) or not referencias:
        raise ValueError("Cenário precisa de referências.")
    for ref in referencias:
        if not isinstance(ref, dict) or any(
            not isinstance(ref.get(campo), str) or not ref[campo].strip()
            for campo in ("titulo", "url", "uso", "acesso")
        ):
            raise ValueError("Referência incompleta.")
        if not ref["url"].startswith("https://"):
            raise ValueError("Referência deve ter URL HTTPS.")
    return cenario


def comparar(parametros):
    """Compara a mesma iluminação por 30 dias (padrão) e 12 meses iguais.

    Toda energia solar considerada passa pela bateria (uso noturno).
    Não há injeção na rede, crédito de excedentes nem economia duplicada.
    """
    validar_parametros(parametros)
    p = dict(parametros)
    tempo = p["quantidade"] * p["horas_dia"] * p["dias_mes"] / 1000
    consumo_atual = p["potencia_atual_w"] * tempo
    consumo_led = p["potencia_led_w"] * tempo
    geracao = p["potencia_solar_kwp"] * p["hsp"] * p["rendimento_solar"] * p["dias_mes"]
    limite_bateria = p["bateria_util_kwh"] * p["dias_mes"]
    solar_util = min(consumo_led, geracao, limite_bateria) * p["disponibilidade_solar"]
    investimento_led = p["quantidade"] * p["preco_led"]
    alternativas = []
    for codigo, nome, consumo, rede, investimento, manutencao in (
        ("atual", "Situação atual", consumo_atual, consumo_atual, 0, 0),
        ("led", "LED na rede", consumo_led, consumo_led, investimento_led, 0),
        ("solar", "LED + solar com bateria", consumo_led, max(0, consumo_led - solar_util),
         investimento_led + p["custo_solar"], p["manutencao_solar_ano"]),
    ):
        custo_rede = rede * p["tarifa_kwh"]
        economia_bruta = (consumo_atual - rede) * p["tarifa_kwh"]
        economia_liquida = economia_bruta * p["meses"] - manutencao
        alternativas.append({
            "codigo": codigo, "nome": nome, "consumo_kwh_mes": consumo,
            "rede_kwh_mes": rede, "custo_rede_mes": custo_rede,
            "investimento": investimento, "manutencao_ano": manutencao,
            "custo_primeiro_ano": investimento + custo_rede * p["meses"] + manutencao,
            "economia_bruta_mes": economia_bruta,
            "economia_liquida_ano": economia_liquida,
            "retorno_simples_meses": (
                investimento / (economia_liquida / p["meses"])
                if codigo != "atual" and economia_liquida > 0 else None
            ),
        })
    menor_custo = min(alternativas, key=lambda a: a["custo_primeiro_ano"])
    # O solar precisa também ser comparado a apenas trocar as lâmpadas.
    ganho_solar_sobre_led = solar_util * p["tarifa_kwh"] * p["meses"] - p["manutencao_solar_ano"]
    return {
        "parametros": p, "alternativas": alternativas,
        "geracao_solar_potencial_kwh_mes": geracao,
        "solar_util_kwh_mes": solar_util,
        "limite_bateria_kwh_mes": limite_bateria,
        "ganho_solar_sobre_led_ano": ganho_solar_sobre_led,
        "menor_custo_primeiro_ano": menor_custo["nome"],
    }


def numero(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def formatar_relatorio(resultado):
    p = resultado["parametros"]
    linhas = [
        "SIMULAÇÃO ESTIMADA — somente iluminação, não a conta inteira.",
        f"{p['quantidade']:g} lâmpadas; {p['horas_dia']:g} h/dia; {p['dias_mes']:g} dias/mês; "
        f"{p['meses']:g} meses iguais ({p['dias_mes'] * p['meses']:g} dias de referência).",
        f"Potências: {p['potencia_atual_w']:g} W atual e {p['potencia_led_w']:g} W LED; "
        f"fluxos assumidos: {p['fluxo_atual_lm']:g} e {p['fluxo_led_lm']:g} lm por lâmpada.",
        f"Custo variável assumido: R$ {numero(p['tarifa_kwh'])}/kWh.",
        "Consumo (kWh) = quantidade × potência (W) × horas/dia × dias ÷ 1000.",
    ]
    for a in resultado["alternativas"]:
        retorno = a["retorno_simples_meses"]
        linhas.extend([
            f"\n{a['nome']}:",
            f"  Consumo das lâmpadas: {numero(a['consumo_kwh_mes'])} kWh/mês; "
            f"compra da rede: {numero(a['rede_kwh_mes'])} kWh/mês.",
            f"  Energia da rede: R$ {numero(a['custo_rede_mes'])}/mês; "
            f"investimento: R$ {numero(a['investimento'])}; "
            f"manutenção: R$ {numero(a['manutencao_ano'])}/12 meses.",
            f"  Custo total dos primeiros 12 meses: R$ {numero(a['custo_primeiro_ano'])}.",
            f"  Economia operacional líquida vs. atual: R$ {numero(a['economia_liquida_ano'])}/12 meses "
            "(antes do investimento).",
        ])
        if a["codigo"] != "atual":
            linhas.append(
                f"  Retorno simples vs. atual: {numero(retorno)} meses (extrapolação, não garantia)."
                if retorno is not None else "  Sem retorno simples: economia operacional não positiva."
            )
    linhas.extend([
        "\nSolar: geração potencial = kWp × HSP × rendimento × dias.",
        f"Hipóteses: {p['potencia_solar_kwp']:g} kWp; {p['hsp']:g} HSP; "
        f"rendimento {p['rendimento_solar']:.0%}; bateria útil {numero(p['bateria_util_kwh'])} kWh; "
        f"disponibilidade {p['disponibilidade_solar']:.0%}.",
        "Solar útil = mínimo(consumo LED, geração potencial, bateria útil × dias) × disponibilidade.",
        f"Geração potencial: {numero(resultado['geracao_solar_potencial_kwh_mes'])} kWh/mês; "
        f"solar efetivamente atribuído à iluminação: {numero(resultado['solar_util_kwh_mes'])} kWh/mês.",
        "A rede supre o restante por transferência segura de fontes. Não há venda nem crédito de excedentes.",
        f"\nMenor custo estimado nos primeiros 12 meses: {resultado['menor_custo_primeiro_ano']}.",
        f"Ganho operacional do solar sobre LED na rede: R$ {numero(resultado['ganho_solar_sobre_led_ano'])}/12 meses, "
        "antes do investimento solar adicional.",
        "Recomendação: use essa comparação como triagem, confirme o mesmo nível de iluminação "
        "e obtenha orçamento antes de investir. Solar exige área sem sombra, bateria, "
        "compatibilidade elétrica e avaliação profissional.",
        "Impactos: LED reduz demanda quando substitui maior potência com iluminação equivalente. "
        "Solar substitui parte da energia da rede, mas painéis, lâmpadas e baterias demandam materiais "
        "e destinação adequada ao fim da vida útil. Não calculamos CO2 evitado nem impacto ambiental zero.",
        "Limitações: preços, horas de uso e geração são hipóteses; não há simulação horária/climática. "
        "Não inclui cobranças fixas, efeitos de descontos tarifários, juros, inflação, "
        "degradação ou trocas futuras de bateria/lâmpadas. Bateria não garante autonomia em apagões. "
        "Economia na fatura pode ser menor que o custo variável estimado.",
    ])
    return "\n".join(linhas)


class ModuloEnergia:
    def __init__(self, caminho=CAMINHO_CENARIO):
        self.cenario = carregar_cenario(caminho)

    def simular(self, **ajustes):
        desconhecidos = set(ajustes) - set(LIMITES)
        if desconhecidos:
            raise ValueError(f"Parâmetros desconhecidos: {', '.join(sorted(desconhecidos))}")
        parametros = dict(self.cenario["parametros"])
        parametros.update(ajustes)
        return comparar(parametros)

    def fontes(self):
        return "\n".join(
            f"- {ref['titulo']}: {ref['url']} (consulta {ref['acesso']}). {ref['uso']}"
            for ref in self.cenario["referencias"]
        )

    def relatorio(self, resultado):
        return formatar_relatorio(resultado) + "\n\nReferências:\n" + self.fontes()

    def detalhes(self, resultado):
        return {
            "tipo": "simulacao_energia", "versao_cenario": self.cenario["versao"],
            "natureza": "estimativa didática, não medição nem garantia",
            "resultado": deepcopy(resultado),
            "referencias": deepcopy(self.cenario["referencias"]),
        }

    def orientacoes(self):
        """Registros compatíveis com Orientacao, recalculados ao iniciar a base."""
        relatorio = self.relatorio(self.simular())
        temas = (
            (101, "Economizar energia e comparar a conta de luz",
             ["energia", "conta de luz", "economizar luz", "consumo", "iluminacao", "sers"],
             "Compare a mesma iluminação antes de escolher uma alternativa."),
            (102, "Trocar lâmpadas por LED com iluminação equivalente",
             ["led", "lampada", "lampadas", "eficiencia energetica"],
             "Confira o fluxo luminoso em lúmens e a potência em watts na etiqueta. "
             "A cor da luz, sozinha, não determina a eficiência."),
            (103, "Energia solar com bateria para iluminação noturna",
             ["energia solar", "painel solar", "solar", "bateria", "renovavel", "fotovoltaica"],
             "O cenário usa bateria porque a iluminação foi considerada noturna. "
             "O sistema solar complementa o LED; compare seu custo adicional com apenas usar LED."),
        )
        return [{
            "id": codigo, "categoria": "Energia e sustentabilidade", "titulo": titulo,
            "palavras_chave": chaves,
            "resposta": introducao + "\n\n" + relatorio + "\n\nUse a opção 5 para ajustar quantidade, uso e tarifa.",
            "documentos": ["Etiqueta das lâmpadas para conferir potência e fluxo luminoso; não informe dados pessoais."],
            "onde": "Citizen Assist AI — opção 5: Comparar alternativas de energia",
            "fonte": "; ".join(ref["url"] for ref in self.cenario["referencias"]),
            "verificado_em": self.cenario["data_referencia"],
        } for codigo, titulo, chaves, introducao in temas]
