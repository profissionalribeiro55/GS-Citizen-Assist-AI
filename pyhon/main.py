"""Ponto de entrada: execute com python main.py"""

from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def main():
    raiz = Path(__file__).resolve().parent
    base = BaseConhecimento(raiz / "data" / "base_conhecimento.json")
    base.carregar()
    assistente = Assistente("Citizen Assist AI", base)

    print("\nBem-vindo ao Citizen Assist AI!")
    print("Este assistente NÃO é um canal oficial.")
    print("Não informe CPF, telefone, e-mail ou outros dados pessoais.\n")

    while True:
        print("\n========= MENU PRINCIPAL =========")
        print("[1] Fazer uma pergunta")
        print("[2] Navegar por categorias")
        print("[3] Ver indicadores")
        print("[4] Exportar atendimentos para CSV")
        print("[0] Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            assistente.perguntar()
        elif opcao == "2":
            assistente.navegar()
        elif opcao == "3":
            assistente.indicadores()
        elif opcao == "4":
            assistente.exportar_csv()
        elif opcao == "0":
            assistente.finalizar()
            break
        else:
            print("Opção inválida. Escolha um número do menu.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrompido pelo usuário.")


        