"""Atendimento SERS integrado ao histórico, indicadores e CSV do assistente."""

import math
import time


def ler_numero(texto, padrao, minimo, maximo, inteiro=False):
    while True:
        entrada = input(f"{texto} [{padrao}] (Enter mantém; v volta): ").strip()
        if entrada.lower() == "v":
            return None
        if not entrada:
            return padrao
        # Aceita decimal brasileiro e impede que texto livre seja persistido.
        try:
            valor = float(entrada.replace(",", "."))
            if not math.isfinite(valor) or not minimo <= valor <= maximo:
                raise ValueError
            if inteiro and not valor.is_integer():
                raise ValueError
            return int(valor) if inteiro else valor
        except ValueError:
            print(f"Informe {'inteiro' if inteiro else 'número'} de {minimo} a {maximo}, sem dados pessoais.")


def atender_energia(assistente, modulo):
    inicio = time.time()
    print("\n=== ENERGIA E SUSTENTABILIDADE ===")
    print("Simulação de iluminação residencial: lâmpadas antigas, LED e LED + solar com bateria.")
    print("Valores iniciais são estimados. Não informe nome, CPF, endereço ou dados da conta.")
    parametros = modulo.cenario["parametros"]
    print(f"Hipótese fixa: lâmpadas atuais de {parametros['potencia_atual_w']:g} W "
          f"e LED de {parametros['potencia_led_w']:g} W com fluxo equivalente; "
          "consulte o cenário documentado antes de aplicar a outra instalação.")
    ajustes = {}
    for campo, texto, minimo, maximo, inteiro in (
        ("quantidade", "Quantidade de lâmpadas", 1, 100, True),
        ("horas_dia", "Horas de uso por dia", 0, 24, False),
        ("tarifa_kwh", "Custo variável em R$/kWh (hipótese se desconhecido)", 0, 10, False),
    ):
        valor = ler_numero(texto, modulo.cenario["parametros"][campo], minimo, maximo, inteiro)
        if valor is None:
            print("Simulação cancelada; nenhum atendimento registrado.")
            return
        ajustes[campo] = valor
    resultado = modulo.simular(**ajustes)
    print(modulo.relatorio(resultado))
    ajudou = assistente._sim_nao("A comparação ajudou a entender suas opções? (s/n): ")
    compreendeu = assistente._sim_nao("Ficou claro que os valores são estimativas? (s/n): ")
    comentarios = (
        "Não informou", "Tudo claro", "Dificuldade com kWh e potência",
        "Dificuldade com custos", "Dificuldade com energia solar", "Dificuldade com limitações",
    )
    print("Comentário opcional (sem texto livre nem identificação):")
    for i, comentario in enumerate(comentarios):
        print(f"[{i}] {comentario}")
    comentario = comentarios[assistente._opcao(len(comentarios) - 1)]
    detalhes = modulo.detalhes(resultado)
    detalhes["avaliacao"] = {"compreendeu_estimativas": compreendeu, "comentario": comentario}
    orientacao = next((o for o in assistente.base.orientacoes if o.id == 101), None)
    assistente.registrar(
        "energia", "Comparação de iluminação residencial", orientacao,
        True, ajudou, 1, inicio, detalhes=detalhes,
    )
