# SERS — Energia e sustentabilidade no Citizen Assist AI
# RM e integrantes:

Enzo Ribeiro RM: 569429
Gabriel de Paula Santos RM: 573195
Joao Lucas Silva Lopes RM: 573875

Contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis**, Global Solution 2026.2, Ciência da Computação/FIAP. Implementada conforme o enunciado `GS2026.2_SERS(2)(2).pdf`.


## Público, necessidade e proposta

O Citizen Assist AI atende cidadãos que procuram orientações sobre documentos, emprego e benefícios. Esta contribuição atende famílias desse público interessadas em reduzir despesas com **iluminação residencial**, com linguagem acessível e sem exigir cadastro.

Comparamos a manutenção de lâmpadas antigas com **duas alternativas**: LED alimentado pela rede e LED complementado por **energia solar fotovoltaica com bateria**. A necessidade é a mesma: iluminar os mesmos pontos por igual número de horas, com fluxo luminoso equivalente. O sistema solar mantém a rede como apoio, com transferência segura; não se considera venda de energia.

Todos os números iniciais são **hipóteses didáticas**, não dados medidos de famílias nem preços pesquisados. O problema é realista, mas a validação com o público ainda precisa ser realizada. A análise completa está em [ANALISE.md](ANALISE.md); cada parâmetro, origem e fonte está em [dados/cenario.json](dados/cenario.json).

## Executar e demonstrar

Na raiz do repositório, com Python 3 instalado:

```powershell
python .\pyhon\main.py
```

Também funciona com `cd pyhon` e `python main.py`. Se necessário, substitua `python` por `py`. Não requer pacotes externos, internet durante a execução ou chave de API. Mantenha `SERS` e `pyhon` juntas na raiz.

1. **Opção 5:** ajuste quantidade de lâmpadas, horas por dia e custo variável em R$/kWh. Enter mantém o exemplo; `v` cancela. Zero é aceito para horas e tarifa. São aceitos decimais com vírgula ou ponto.
2. Leia consumo, compra da rede, investimento, manutenção, custo total em 12 meses e retorno simples. A recomendação é recalculada; não se escolhe LED ou solar automaticamente em todos os cenários.
3. Responda sobre utilidade, compreensão das estimativas e, opcionalmente, escolha um comentário predefinido. Não há coleta de nomes, endereço ou texto livre nessa avaliação.
4. **Opção 1:** pergunte `como economizar na conta de luz`, `lampadas led` ou `energia solar`.
5. **Opção 2:** navegue por **Energia e sustentabilidade**. As respostas usam a mesma função de cálculo, com o cenário inicial.
6. **Opções 3 e 4:** consulte os indicadores gerais e exporte o histórico. Ao sair por `0`, a nota de facilidade é aplicada aos atendimentos da sessão.

O valor personalizado da opção 5 vale para aquele atendimento; não modifica o cenário inicial nem as respostas de perguntas/categorias. A comparação vale apenas para a iluminação selecionada, não para toda a residência. As potências e fluxos iniciais devem corresponder ao caso antes de aplicar os resultados.

## Arquitetura e integração

| Arquivo | Função |
| --- | --- |
| `dados/cenario.json` | Parâmetros, unidades nos nomes dos campos, premissas individuais e referências com data e finalidade. |
| `energia.py` | Validação, cálculos, relatório e três orientações geradas para a base. |
| `interface.py` | Entrada numérica, comparação e avaliação no atendimento existente. |
| `../pyhon/main.py` | Carrega SERS e adiciona a opção 5 ao menu. |
| `../pyhon/base_conhecimento.py` | Valida as orientações adicionais junto das dez originais e as inclui na busca e nas categorias. |
| `../pyhon/assistente.py` | Salva o atendimento de energia no mesmo histórico e exporta os detalhes como JSON na última coluna do CSV. |
| `testes/test_integracao.py` | Testes dos cálculos, validação, persistência, busca, categorias e execução completa. |
| `TESTES_USUARIOS.md` | Protocolo para testes reais, registros pendentes e ajustes a documentar. |
| `ROTEIRO_VIDEO.md` | Roteiro de até três minutos para o vídeo técnico. |
| `ENTREGA_MODELO.txt` | Modelo do único arquivo a enviar no portal; completar integrantes e vídeo. |

Os IDs de energia são 101, 102 e 103, reservados para evitar colisão com os dez registros originais. A base principal continua em `pyhon/data/base_conhecimento.json`; as respostas SERS são calculadas no início da execução. Reinicie após editar o cenário.

Atendimentos personalizados usam `origem=energia`. Os dados numéricos, resultados, versão do cenário, referências e avaliação ficam em `detalhes` de `pyhon/data/historico.json`. A exportação produz `pyhon/data/atendimentos.csv`, com `detalhes` em JSON na última coluna. Registros antigos sem esse campo continuam válidos. O arquivo antigo `atendimento.csv` (singular) não é usado pelo exportador.

O histórico comum e os indicadores incluem energia. A regra existente de recusa de perguntas com `@` ou oito algarismos continua ativa. Ela é limitada e não constitui anonimização completa. Na simulação são aceitos apenas números dentro das faixas; o texto digitado não é gravado. Um cancelamento não cria registro.

Não havia código de Computer Science nesta cópia do repositório: a integração implementada é com os módulos Python disponíveis. O vínculo conceitual com a decisão lógica está na recusa de perguntas com dados pessoais, validação de respostas e referências documentadas; **não há verificação online automática de fontes**.

## Dados e manutenção

Para mudar potência, fluxo, preço das LEDs, orçamento solar, bateria ou premissas solares, edite o JSON e atualize a justificativa correspondente. `hsp` representa horas de sol pleno, `rendimento_solar` é fator de conversão e `disponibilidade_solar` é uma hipótese separada de atendimento. A bateria é informada em **kWh úteis na carga**, não Ah nem capacidade nominal. A LED deve atender ao menos ao fluxo luminoso adotado como referência.

O programa rejeita parâmetros inválidos, ausências de premissas e referências incompletas. Se o arquivo de cenário estiver ausente ou inválido, avisa e mantém os serviços originais disponíveis. Isso não verifica a veracidade do conteúdo: a equipe deve conferir referências, etiquetas, dados locais e orçamentos. Preços e vida útil exigem validação antes de qualquer decisão real.

## Conferência dos requisitos do PDF

| Requisito | Evidência |
| --- | --- |
| Público e necessidade | Seção inicial deste README. |
| Dados, origem, unidades e período comum | JSON de cenário e análise de 30 dias / 12 meses iguais. |
| Duas alternativas, incluindo renovável | LED na rede versus LED + solar com bateria, comparados à situação atual. |
| Custos, viabilidade e ambiente | Relatório do programa e `ANALISE.md`. |
| Integração efetiva | Perguntas, categorias, opção 5, histórico, indicadores e CSV. |
| Referências e limitações | Exibidas nas respostas, JSON e análise. |
| Testes com usuários e ajustes | Instrumento implementado e protocolo pronto; **execução com pessoas pendente**. |
| Repositório organizado | Código e documentação nesta pasta; **publicação das alterações no GitHub pendente**. |
| Vídeo não listado de até 3 minutos | Roteiro pronto; **gravação e publicação pendentes**. |
| Arquivo `.txt` com integrantes e links | Modelo pronto; **preenchimento e conferência dos links pendentes**. |
