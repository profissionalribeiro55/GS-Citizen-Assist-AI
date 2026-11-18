# Computer Science — Citizen Assist AI

# RM e integrantes:

Enzo Ribeiro RM: 569429
Gabriel de Paula Santos RM: 573195
Joao Lucas Silva Lopes RM: 573875

Programa de terminal que demonstra a regra **S = (negado)P ∧ R ∧ F**. A orientação é autorizada somente quando não há dados pessoais identificados (P=0), existe resposta (R=1) e a fonte está verificada (F=1).

## Executar

Na raiz do projeto, com Python 3:

```powershell
python .\computer\main.py
```

Também é possível abrir a pasta `computer` e executar `python main.py`. Se necessário, substitua `python` por `py` Não precisa instalar bibliotecas

| Opção | Requisito implementado |
| --- | --- |
| 1 | Recebe P, R e F e apresenta autorização ou motivos do bloqueio. |
| 2 | Gera as oito combinações da tabela-verdade, com ¬P e S. |
| 3 | Obtém a soma de mintermos Σm(3); mostra De Morgan, dupla negação e a justificativa de minimalidade. |
| 4 | Gera o mapa em código Gray, indica o grupo unitário G1 e compara com a álgebra. |
| 5 | Verifica as oito combinações contra saídas esperadas e compara as representações. |
| 0 | Encerra o programa. |

A consulta aceita somente `0` ou `1`; `v` volta ao menu. Valores inválidos geram uma mensagem e uma nova tentativa. Ctrl+C ou fim da entrada encerram sem traceback.

## Exemplos e interpretação

- P=0, R=1, F=1: orientação autorizada.
- P=1, R=1, F=1: bloqueio por dados pessoais.
- P=0, R=0, F=1: resposta não encontrada.
- P=0, R=1, F=0: fonte não verificada.

O mapa usa linhas P=0/1 e colunas RF=00,01,11,10. O único 1 é o grupo G1 na linha P=0 e coluna RF=11. A função já é mínima: não existe redução adicional em relação à forma canônica. A derivação por De Morgan confirma a equivalência, sem inventar uma redução de literais.

Este é um módulo didático independente: as condições são informadas manualmente; ele não analisa perguntas, não verifica fontes nem consulta a base de atendimento. A orientação exibida explica a decisão e o próximo passo. Nenhum dado é gravado. A representação de circuitos ficou fora do código, conforme solicitado.

## Testes

Execute na raiz do projeto:

```powershell
python -m unittest discover -s computer -p "test_*.py" -v
```

Os testes cobrem a tabela completa, a ordem do mapa, a equivalência das expressões, entradas inválidas, motivos do bloqueio, cancelamento e as opções do menu.
