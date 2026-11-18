# Análise energética — iluminação residencial

**Data do cenário:** 17/11/2026. **Natureza:** estudo didático estimado, sem levantamento de campo ou cotação comercial. Os resultados são reproduzidos por `ModuloEnergia.simular()` em `energia.py`. A fonte dos números é a hipótese explícita em `dados/cenario.json`; as referências sustentam os conceitos, não os valores de preços e hábitos.

## Serviço comparado

Cinco pontos de luz, 800 lúmens por ponto e 5 horas diárias de uso noturno. A situação atual supõe lâmpadas antigas de 60 W já existentes; não se recomenda comprar essa tecnologia. As alternativas usam LEDs de 9 W com fluxo equivalente assumido. A equivalência deve ser conferida na etiqueta, na distribuição luminosa e na iluminância real do ambiente.

As três opções são avaliadas por **30 dias** e por **12 meses iguais, totalizando 360 dias de referência**. O cálculo não pretende representar a sazonalidade de um ano civil.

## Hipóteses principais

| Grandeza | Valor assumido | Justificativa e condição |
| --- | ---: | --- |
| Quantidade / uso | 5 lâmpadas / 5 h por dia | Exemplo simples de residência pequena; ajustar ao caso. |
| Potência atual / LED | 60 W / 9 W | Comparação didática; conferir etiquetas. |
| Fluxo por ponto | 800 lm em ambas | Mesma necessidade luminosa, sem reduzir serviço para alegar economia. |
| Preço variável da energia | R$ 1,00/kWh | Hipótese, não tarifa de uma distribuidora. |
| LED | R$ 15 por unidade | Orçamento ilustrativo, substituição em soquete compatível existente. |
| Sistema solar adicional | R$ 2.500 | Hipótese incluindo painel, bateria, controlador, conversão, proteções, instalação e transferência de fontes; precisa de cotação. |
| Manutenção solar | R$ 100 por 12 meses | Provisão ilustrativa, sem substituição futura da bateria. |
| Painel | 0,10 kWp | Sistema dedicado à iluminação, não à casa inteira. |
| Sol pleno | 4,5 HSP/dia | Não é dado local; pesquisar dados mensais antes de dimensionar. |
| Rendimento global solar | 75% | Perdas de conversão e armazenamento agregadas; hipótese. |
| Bateria útil | 0,30 kWh por ciclo diário | Energia entregável à carga, já descontadas perdas e limites de descarga. |
| Disponibilidade adicional | 80% | Hipótese de atendimento do limite diário, sem pretensão de modelar o clima. |

## Cálculos

**Consumo:** `E = quantidade × potência em W × horas/dia × dias ÷ 1000`.

- Atual: `5 × 60 × 5 × 30 ÷ 1000 = 45 kWh/mês`.
- LED: `5 × 9 × 5 × 30 ÷ 1000 = 6,75 kWh/mês`.
- Redução da demanda das lâmpadas: `45 − 6,75 = 38,25 kWh/mês`, ou **85% apenas para esta iluminação e estas potências**.
- Eficácia luminosa assumida: atual `800/60 ≈ 13,33 lm/W`; LED `800/9 ≈ 88,89 lm/W`. Não confundir potência (W), energia (kWh) e fluxo luminoso (lm).

**Solar:** `G = potência em kWp × HSP × rendimento × dias`.

- Geração potencial líquida: `0,10 × 4,5 × 0,75 × 30 = 10,125 kWh/mês`.
- Limite mensal da bateria com um ciclo por dia: `0,30 × 30 = 9 kWh`.
- Uso solar estimado: `mínimo(6,75; 10,125; 9) × 0,80 = 5,40 kWh/mês`.
- Compra residual da rede: `6,75 − 5,40 = 1,35 kWh/mês`.

A geração potencial não equivale automaticamente a economia: o modelo limita o aproveitamento pelo consumo e pela bateria, e depois aplica disponibilidade. A bateria é necessária para o uso noturno assumido. A rede cobre a parcela não suprida, mediante projeto de transferência segura, sem paralelismo improvisado. Não há compensação nem venda de excedentes.

O fator de 80% é uma hipótese adicional sobre atendimento, não outra eficiência da bateria. A aproximação de um ciclo diário ignora sequências de dias nublados, carga inicial, envelhecimento e curvas horárias. Portanto, não comprova autonomia, atendimento integral ou capacidade real de instalação. Uma decisão real exige simulação temporal e dimensionamento por profissional.

## Custos no mesmo período

| Indicador | Situação atual | LED na rede | LED + solar e bateria |
| --- | ---: | ---: | ---: |
| Consumo das lâmpadas (kWh/mês) | 45,00 | 6,75 | 6,75 |
| Compra da rede (kWh/mês) | 45,00 | 6,75 | 1,35 |
| Energia da rede (R$/mês) | 45,00 | 6,75 | 1,35 |
| Investimento inicial (R$) | 0,00 | 75,00 | 2.575,00 |
| Manutenção em 12 meses (R$) | 0,00 | 0,00 | 100,00 |
| Total dos primeiros 12 meses (R$) | 540,00 | 156,00 | 2.691,20 |
| Economia operacional líquida vs. atual em 12 meses (R$), antes do investimento | 0,00 | 459,00 | 423,80 |
| Retorno simples vs. atual (meses) | Não se aplica | 1,96 | 72,91 |

`Total inicial = investimento + 12 × custo mensal da rede + manutenção`.

`Economia operacional líquida = 12 × (custo atual da rede − custo da alternativa) − manutenção`.

`Retorno simples = investimento ÷ (economia operacional líquida / 12)`, somente com economia positiva. O retorno solar de 72,91 meses é uma **extrapolação das hipóteses**, fora do horizonte comparativo de 12 meses. Ignora degradação, substituições, juros, inflação e valor do dinheiro no tempo; pode nunca ser atingido. Não deve ser usado como promessa de retorno de investimento.

## Recomendação e viabilidade

No cenário inicial, **LED na rede tem o menor custo no primeiro período de 12 meses**. O investimento de R$ 75 reduz o custo modelado de R$ 540 para R$ 156, diferença de R$ 384 já considerando a compra das lâmpadas.

O solar reduz ainda mais a compra de energia da rede, mas seu investimento adicional não se justifica economicamente neste cenário: sobre a alternativa LED, economiza `5,40 × 12 × R$ 1,00 = R$ 64,80` em energia, abaixo da manutenção hipotética de R$ 100. O ganho operacional incremental é **negativo em R$ 35,20 por 12 meses**, antes de pagar os R$ 2.500 adicionais. É uma alternativa renovável a avaliar, não a recomendação automática para toda família.

LED requer verificação de fluxo, tensão, soquete e qualidade. Solar exige espaço adequado, avaliação de sombras, compatibilidade de equipamentos, acesso para manutenção, orçamento e instalação profissional. Para imóvel alugado ou orçamento reduzido, custo inicial e autorização para instalação são limitações relevantes. Não há instruções de montagem elétrica neste protótipo.

## Sensibilidade da hipótese solar

Mantendo os demais parâmetros:

| Disponibilidade assumida | Solar útil (kWh/mês) | Rede (kWh/mês) | Custo total solar nos primeiros 12 meses |
| --- | ---: | ---: | ---: |
| 0% | 0,00 | 6,75 | R$ 2.756,00 |
| 80% | 5,40 | 1,35 | R$ 2.691,20 |
| 100% | 6,75 | 0,00 | R$ 2.675,00 |

Mesmo o extremo favorável de 100% não torna esse sistema solar mais barato que só usar LED nos primeiros 12 meses. Se o usuário informar zero hora de uso ou tarifa zero, não há economia positiva que justifique os investimentos no critério econômico adotado; o programa não calcula divisão por zero nem promete retorno.

## Impactos ambientais e limitações

LED diminui demanda elétrica quando substitui maior potência com iluminação equivalente. A parcela fotovoltaica usa fonte renovável e reduz a energia retirada da rede. Isso não permite afirmar redução proporcional de emissões: depende da geração substituída e do ciclo de vida.

Lâmpadas, painéis, eletrônica e baterias exigem matérias-primas, produção, transporte e destinação adequada. A bateria também pode exigir reposições. Sem inventário de ciclo de vida e fator de emissão adequado ao período, não calculamos toneladas de CO2 evitadas nem atribuímos impacto zero ao solar.

O estudo trata apenas do custo variável de iluminação. Não inclui demais equipamentos da casa, cobranças fixas, descontos ou benefícios tarifários, intervenções não orçadas, inflação, financiamento, substituições futuras, falhas e degradação. A manutenção da situação atual e das LEDs foi assumida zero nesse primeiro horizonte, não para toda a vida útil. Valores reais devem vir de etiquetas, hábitos observados, tarifas aplicáveis, clima local e cotações.

## Referências e rastreabilidade

Consultadas em 17/11/2026; os links e a finalidade específica também aparecem nas respostas do assistente.

- [Centro Paula Souza — Energia](https://pets.cps.sp.gov.br/entenda-os-conceitos-energia/): potência, energia e relação `E = P × t`.
- [Inmetro — Eficiência das lâmpadas](https://www.gov.br/inmetro/pt-br/acesso-a-informacao/perguntas-frequentes/avaliacao-da-conformidade/lampadas-e-luminarias-led-portaria-inmetro-no-231-2026-consumidores/para-pagar-uma-conta-de-energia-mais-barata-devo-comprar-lampadas-e-luminarias-de-luz-201cfria201d): eficácia em lm/W e avaliação da etiqueta.
- [CEPEL/CRESESB — SunData](https://www.cresesb.cepel.br/?section=sundata): fonte para futura obtenção de dados locais e mensais de irradiação, não origem do valor assumido de 4,5 HSP.
- [CEPEL/CRESESB — Casa Solar Eficiente](https://cresesb.cepel.br/index.php?catid=91&lang=pt&section=com_content): função de baterias e controladores no atendimento noturno. As duas páginas do CEPEL foram localizadas em busca, mas a abertura direta esteve indisponível durante a consulta.
- [EPE — Energia Renovável, 2016](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-172/Energia%20Renov%C3%A1vel%20-%20Online%2016maio2016.pdf): impactos na fabricação de componentes fotovoltaicos e gestão ambiental de resíduos.
