"""Módulo didático de decisão lógica do Citizen Assist AI"""

from itertools import product


def validar_entradas(p, r, f):
    """Aceita apenas inteiros 0/1 ou booleanos, sem converter textos ou decimais"""
    for nome, valor in zip("PRF", (p, r, f)):
        if type(valor) not in (int, bool) or valor not in (0, 1):
            raise ValueError(f"{nome} deve ser 0 ou 1.")


def decidir(p, r, f):
    """Implementa S = NÃO P E R E F; retorna o inteiro 0 ou 1"""
    validar_entradas(p, r, f)
    return int((not p) and r and f)


def forma_canonica(p, r, f):
    """Soma de mintermos: somente m3 (011, na ordem PRF) autoriza"""
    validar_entradas(p, r, f)
    indice = 4 * p + 2 * r + f
    return int(indice in (3,))


def pela_condicao_de_bloqueio(p, r, f):
    validar_entradas(p, r, f)
    bloqueado = p or not r or not f
    return int(not bloqueado)


def tabela_verdade():
    """Gera todas as 2³ combinações em ordem binária PRF"""
    return [(p, r, f, decidir(p, r, f)) for p, r, f in product((0, 1), repeat=3)]


def mapa_karnaugh():
    """Linhas P=0/1; colunas RF=00,01,11,10 (código Gray)"""
    colunas = ((0, 0), (0, 1), (1, 1), (1, 0))
    return [[decidir(p, r, f) for r, f in colunas] for p in (0, 1)]


def orientacao(p, r, f):
    if decidir(p, r, f):
        return (
            "S = 1 — Orientação autorizada\n"
            "Apresente a resposta encontrada junto da fonte oficial conferida\n"
            "Este módulo demonstra a autorização; não consulta serviços públicos"
        )
    motivos = []
    if p:
        motivos.append("Dados pessoais identificados: remova-os e reformule a pergunta")
    if not r:
        motivos.append("Resposta não encontrada: reformule a dúvida ou procure o canal oficial")
    if not f:
        motivos.append("Fonte não verificada: confira uma fonte oficial antes de orientar")
    return "S = 0 — Orientação não autorizada.\n" + "\n".join(motivos)


def mostrar_tabela():
    print("\nTABELA-VERDADE COMPLETA — 2³ = 8 combinações")
    print("P: dados pessoais; R: resposta encontrada; F: fonte verificada")
    print("0 = falso; 1 = verdadeiro; S = autorização da orientação")
    print("P | R | F | NÃO P | S")
    for p, r, f, s in tabela_verdade():
        print(f"{p} | {r} | {f} |   {int(not p)}   | {s}")


def mostrar_algebra():
    mintermos = [4 * p + 2 * r + f for p, r, f, s in tabela_verdade() if s]
    print("\nFORMA CANÔNICA — SOMA DE MINTERMOS")
    print(f"Mintermos com saída 1: {mintermos} (ordem das variáveis: P, R, F)")
    print("011 em binário = 3. Logo, S = Σm(3) = ¬P · R · F")
    print("¬ = NÃO; · = E; + = OU.")
    print("\nÁLGEBRA BOOLEANA")
    print("Condição de bloqueio: B = P + ¬R + ¬F.")
    print("S = ¬B = ¬(P + ¬R + ¬F)                 [negação do bloqueio]")
    print("S = ¬P · ¬(¬R) · ¬(¬F)                  [lei de De Morgan]")
    print("S = ¬P · R · F                           [dupla negação]")
    print("A derivação confirma a forma canônica; não reduz o número de literais.")
    print("Ela já é mínima: retirar ¬P autorizaria 111; retirar R autorizaria 001;")
    print("retirar F autorizaria 010. Essas três combinações devem resultar em 0")


def mostrar_mapa():
    print("\nMAPA DE KARNAUGH — colunas RF em código Gray")
    print("P / RF | 00 | 01 |   11   | 10")
    for p, linha in enumerate(mapa_karnaugh()):
        celulas = ["1 (G1)" if s else "0" for s in linha]
        print(f"   {p}   | {celulas[0]:2} | {celulas[1]:2} | {celulas[2]:6} | {celulas[3]:2}")
    print("G1 é o agrupamento de uma única célula: P=0, R=1, F=1")
    print("Não há outro 1 adjacente. Nenhum zero pode ser incluído no grupo")
    print("Todas as entradas são consideradas; não há condições indiferentes (X)")
    print("G1 mantém ¬P, R e F: S = ¬P · R · F")
    print("Conclusão: mesmo resultado da álgebra; não há simplificação adicional")


def verificar_combinacoes():
    """Compara três representações com os resultados esperados explicitamente"""
    esperados = (0, 0, 0, 1, 0, 0, 0, 0)
    mapa = mapa_karnaugh()
    coluna_rf = {(0, 0): 0, (0, 1): 1, (1, 1): 2, (1, 0): 3}
    print("\nVERIFICAÇÃO DAS OITO COMBINAÇÕES")
    print("PRF | Esperado | Canônica | Lógica | Bloqueio | Mapa | Resultado")
    aprovados = 0
    for (p, r, f, s), esperado in zip(tabela_verdade(), esperados):
        canonica = forma_canonica(p, r, f)
        bloqueio = pela_condicao_de_bloqueio(p, r, f)
        k = mapa[p][coluna_rf[(r, f)]]
        ok = all(valor == esperado for valor in (canonica, s, bloqueio, k))
        aprovados += int(ok)
        print(f"{p}{r}{f} |    {esperado}     |    {canonica}     |   {s}    |    {bloqueio}     |  {k}   | {'OK' if ok else 'FALHA'}")
    print(f"Resultado: {aprovados}/8 combinações corretas")
    return aprovados == 8


def ler_bit(nome, descricao):
    while True:
        entrada = input(f"{nome} — {descricao} (0=não, 1=sim; v=voltar): ").strip()
        if entrada.lower() == "v":
            return None
        if entrada in ("0", "1"):
            return int(entrada)
        print("Entrada inválida. Digite somente 0, 1 ou v para voltar")


def consultar():
    print("\nInforme apenas os valores booleanos; não digite dados pessoais reais")
    valores = []
    for nome, descricao in (
        ("P", "Foram identificados dados pessoais?"),
        ("R", "Foi encontrada uma resposta?"),
        ("F", "A fonte foi verificada?"),
    ):
        valor = ler_bit(nome, descricao)
        if valor is None:
            print("Consulta cancelada.")
            return
        valores.append(valor)
    print("\n" + orientacao(*valores))


def main():
    print("Citizen Assist AI — Computer Science")
    print("Simulação didática: as condições são informadas por você")
    print("Não detecta dados pessoais nem verifica fontes automaticamente")
    acoes = {"1": consultar, "2": mostrar_tabela, "3": mostrar_algebra,
             "4": mostrar_mapa, "5": verificar_combinacoes}
    try:
        while True:
            print("\n1 — Consultar decisão\n2 — Tabela-verdade completa")
            print("3 — Forma canônica e álgebra\n4 — Mapa de Karnaugh")
            print("5 — Verificar as oito combinações\n0 — Sair")
            opcao = input("Escolha: ").strip()
            if opcao == "0":
                print("Programa encerrado.")
                return
            acao = acoes.get(opcao)
            if acao is None:
                print("Opção inválida. Escolha um número de 0 a 5")
            else:
                acao()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma encerrado pelo usuário")


if __name__ == "__main__":
    main()
