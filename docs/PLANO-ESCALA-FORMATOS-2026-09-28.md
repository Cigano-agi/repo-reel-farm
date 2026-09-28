# Plano de escala dos formatos — 28/09/2026

**Estado:** plano de implementação, não benchmark concluído. “Rios” no pedido foi interpretado como Reels/Repo Reel. A meta é reduzir espera e repetição sem perder prova, ritmo, legibilidade e revisão humana. O código existente continua funcional; nenhuma publicação ou produção em lote é autorizada por este plano.

## 1. O que existe hoje

| Formato | Fonte atual | Contrato e estado | Gargalo observado |
| --- | --- | --- | --- |
| Twitter Card | `ventures-apps/tycoonclaws/conteudo/cigano/formatos/tweet-video-card/` | Card 4:5 com tweet autoral, vídeo atribuído, `post.json`, validador, render e fila sequencial; piloto Unitree local. | Fila renderiza cada post inteiro; captura e direitos são manuais; formato vive fora da farm. |
| Carrossel de vídeo-notícia | Skill local `carrossel-video-noticia` e piloto Jev | 3:4, padrão ≥8 slides, fonte/roteiro/blueprint/HTML/FFmpeg/galeria/QA; export por slide permite refazer só o afetado. | Muitos scripts e schemas históricos; a direção visual e o QA ainda demandam revisão por slide. |
| Repo Reel | Este repositório e Hypit V4 no projeto original | 9:16, pesquisa→roteiro→browser/prova/aplicação→voz/SFX→dois masters→QA; `farm.py` já tem oito papéis, gates, cache por hash e lote mock. | O piloto QM foi dirigido manualmente; farm real exercida em um papel, não no lote completo. Com música e limpo renderizaram o mesmo vídeo duas vezes. |
| Demo Cut | Nota Punk de formatos modulares | Modo previsto para selecionar e explicar trechos de vídeo real. | Ainda não implementado; não entra na primeira rodada de otimização. |

**Medidas disponíveis:** no QM, os dois renders HyperFrames de 38 s levaram 186,060 s e 187,504 s no mesmo host, total de **373,564 s** de render de imagem. A tarefa real `facts_product` com Codex levou 176,78 s. O lote simulado passou, mas tempo e tokens totais de produção não foram medidos. No spike anterior de Repo Reel de 15 s, HyperFrames levou 46,49 s; não extrapolar esse número para outros episódios. Fontes: `episodes/04-qm/delivery/manifest.json`, `CHECKPOINT.md` e nota Punk de formatos modulares.

## 2. Produto interno: uma pauta, três saídas possíveis

Um **registro de pauta** guarda URL, autor, data de acesso, claims, evidências, direitos, artefato visual e possível aplicação. A mesma pesquisa pode alimentar Twitter Card, carrossel ou Repo Reel; cada formato escolhe sua própria história, proporção, duração, CTA e QA. Não converter 4:5 em 3:4 ou 9:16 por crop automático.

```text
Fonte/snapshot → pauta e claims verificados → escolha do formato
                                       ├─ Twitter Card 4:5
                                       ├─ Carrossel 3:4
                                       └─ Repo Reel 9:16
                           → preview → revisão → master → QA → aceite
```

Contrato comum proposto: `content_id`, `format`, `sourceLedger[]` (URL, autor, data, trecho, natureza da prova, limite, direitos), `claimIds[]`, `story`, `assets[]` com hash/licença, `cta`, `status`, `revision`, `parentRevision`, `renderProfile` e `qaReceipt`. Extensões por formato preservam `tweet`, `slides[]` ou `beats[]`; migração importa os manifests existentes, sem reescrever os pilotos. Fonte de prova, hipótese de aplicação e simulação visual são tipos distintos no schema.

### CRUD seguro

| Operação | Comportamento proposto |
| --- | --- |
| Criar | `farm content new --format ... --source ...`: ID estável, pasta isolada, brief curto e schema válido. |
| Ler/listar | `farm content list/show`: filtro por formato, status, data, fonte, direitos e último QA; galeria local aponta para o render exato. |
| Atualizar | `farm content update`: nova revisão, diff de claims/roteiro/voz/assets, invalidação somente dos nós dependentes; nunca sobrescreve master aceito. |
| Arquivar | `farm content archive`: retira da fila ativa com motivo e data; preserva fontes e revisões. Exclusão física só com pedido explícito e alvo verificado. |

Estados distintos: `candidate → researched → scripted → previewed → rendered → qa_passed → human_accepted → published`, com `blocked` e `archived`. `qa_passed` não implica direitos ou publicação. Receitas/template têm versão própria; episódio fixa a versão usada.

## 3. Biblioteca que acelera sem produzir vídeos iguais

**Camada de dados:** fontes e claims reutilizáveis; snapshots com data; capturas indexadas por URL/viewport/hash; léxico PT-BR e take de voz por hash; SFX e trilhas com licença/nível registrados. Assets privados e mídia de terceiros ficam fora do Git público.

**Camada visual editável:** blocos `browser-reveal`, `quote-proof`, `real-video-proof`, `mechanism-diagram`, `application-demo`, `whatsapp-illustration`, `caption-safe`, `source-chip`, `cta-live` e `sfx-cue`. Cada bloco tem contrato de entrada, duração mínima de leitura, zona segura, variantes de layout/motion, teste de contraste e exemplo. A peça só usa blocos relevantes; a prova real determina a montagem. Três gramáticas iniciais: **artefato primeiro**, **browser investigativo** e **antes→troca→resultado**. O editor escolhe por evidência; não alternar aleatoriamente para parecer variado.

**Direção de edição:** cortes em pausas não intencionais detectadas por VAD/ASR, conferidos pelo editor; alinhamento palavra→legenda; movimento de browser com função; SFX curtos com cue e ganho; música sob voz com medição, ducking quando necessário; transições apenas quando ajudam a localizar a mudança. Exigir gancho compreensível sem áudio em 0–3 s, nome visível na primeira fala, prova narrada por tempo suficiente e aplicação concreta marcada como real ou ilustrativa. Reutilizar o timbre Vlad como candidato de casting, após escuta/aceite; não clonar voz de Fabrício nem de terceiros.

**Estrutura proposta no repo atual:**

```text
content/                 # pautas e revisões, sem mídia privada
formats/twitter-card/    # adapter do formato existente
formats/carousel/        # adapter do método existente
formats/repo-reel/       # adapter do episódio atual
blocks/                  # componentes visuais e SFX versionados
schemas/                 # contrato comum e extensões
benchmarks/              # tempos, tokens, custo, cache, QA
docs/                   # contratos, decisões e migração
```

Não copiar automaticamente scripts, fonts ou assets do projeto original para o repo público: conferir licença e retirar dados privados antes de cada importação. Hypit fica como ferramenta opcional para prototipar blocos ou adaptar referência quando ele agregar valor; o teste QM de 8 s não demonstrou integração automática com a composição HyperFrames.

## 4. Caminho crítico, custo e render

1. **Pesquisa compartilhada por pauta.** Capturar uma vez, separar extração mecânica de decisão editorial e guardar pacote curto de evidências. A LLM recebe somente claims e trechos pertinentes ao papel; cada resultado cita URL/artefato. Revalidar fonte volátil por prazo e registrar timestamp de cache.
2. **Agentes por necessidade.** Pesquisa social e fatos em paralelo; copy só após gate factual; motion após copy; um editor por composição; QA visual e red team em paralelo depois do master. Não disparar oito conversas longas para um Twitter Card simples. Prompt estático versionado + delta da pauta, outputs tipados e limites de contexto/tokens por função. Modelo mais caro fica para decisões editoriais difíceis, não para renomear arquivos ou medir MP4.
3. **Prévia em segundos como alvo medido.** Gerar storyboard/contato e amostras de cenas em resolução menor antes da exportação final. “Em segundos” vale para abrir uma pauta, alterar texto e obter prévia curta quando assets estão em cache; master completo profissional continuará dependente de duração, mídia, hardware e revisão.
4. **Uma imagem, dois áudios.** Benchmark de QM: renderizar a imagem uma vez, criar mix com música e mix limpo, copiar o stream de vídeo para dois MP4. Comparar sincronismo, loudness, true peak, hashes de frames e tempo com o processo atual. Só substituir o fluxo após equivalência visual/sonora. A documentação oficial do [HyperFrames](https://github.com/heygen-com/hyperframes/blob/main/docs/developers/cli.mdx) já prevê batch/variáveis/snapshot; [FFmpeg](https://ffmpeg.org/ffmpeg.html) suporta streamcopy e sua documentação de filtros cobre medição/normalização de áudio.
5. **Cache fino.** Chaves independentes para fonte, captura, voz, alinhamento, bloco visual, render de imagem e mix. CTA alterado deve refazer somente cenas/áudio afetados quando a composição permitir; medir antes de prometer. Hash inclui versão do template, fonte, direitos e software. Cache hit não mascara fonte velha.
6. **QA em dois níveis.** Checagem rápida em preview detecta crop, safe zone, pausas, texto sobre mídia e cena parada. Master passa decode integral, dimensões/fps, LUFS/true peak, contato, frames de transições, revisão sem áudio/com áudio/em celular, claims e direitos. Defeitos viram correção concreta e regressão automatizável quando possível.

## 5. Implementação em quatro entregas pequenas

| Entrega | Construir | Aceite verificável |
| --- | --- | --- |
| A — linha de base | Instrumentar `farm.py` e os três adapters sem mudar visual: tempo por etapa, tempo humano, tokens de entrada/saída, custo declarado, cache hits, renders repetidos e defeitos de QA. Rodar um exemplar de cada formato. | Relatório comparável com máquina, versão, fonte, qualidade e gargalo; sem inferir velocidade de mock. |
| B — contrato e CRUD | Schema comum, importadores sem perda, `new/list/show/update/archive`, revisão imutável, ledger de direitos e galeria local. | Criar/editar/arquivar/reabrir uma pauta de cada formato; pilotos antigos intactos; testes de migração e isolamento. |
| C — biblioteca e render | 5–8 blocos primeiro (gancho, browser, prova real, diagrama, legenda, SFX, CTA), preview leve e um render de imagem com dois mixes de áudio. | QM reproduzido a partir do template com frames e áudio equivalentes; mudança de CTA não refaz pesquisa; export final passa QA. |
| D — lote real | Produzir três pautas diferentes (uma por formato) com fontes novas, subagentes e revisão independente; ajustar componentes a partir dos defeitos. | Todos com fonte/limite, edição legível, pacote editável, QA e status separado de publicação; relatório antes/depois de tempo e tokens. |

**Metas de teste, não resultados:** reduzir ≥30% do tempo de máquina por Reel quando forem necessários dois masters; reduzir ≥30% dos tokens por pauta com contexto seletivo e cache, sem aumento de retrabalho de QA. Preview curta deve aparecer em menos de 15 s num caso com assets locais e máquina registrada. Se qualquer meta falhar, manter a variante com melhor qualidade e registrar causa. Um único vídeo não valida a farm para 14 pautas; medir pelo menos três temas e uma revisão tardia de roteiro/CTA.

## 6. Decisões e limites

- Primeiro otimizar o Repo Reel QM, onde há medição e vídeo de referência; depois conectar Twitter Card e carrossel pelos adapters. Demo Cut vem após o CRUD e a biblioteca básica.
- O visual café/noir+cobalto pertence ao Repo Reel atual; Twitter Card mantém linguagem do X e carrossel adapta o design system do assunto. Assinatura editorial, fonte visível e QA são comuns.
- “Nível CapCut” é um critério de acabamento observado no vídeo final: cortes motivados, áudio limpo, legendas sincronizadas, movimento dirigido e SFX funcionais. Nenhuma ferramenta recebe esse selo só por existir no pipeline.
- Hipótese comercial: vídeos podem gerar descoberta e entrada para a Guilda. Medir retenção, salvamentos/alcance, compartilhamentos/alcance, follows e conversas qualificadas por formato e janela, quando houver dados do perfil. Views isoladas não provam receita. Não automatizar publicação nesta fase.

## Fontes usadas

- Código e medições locais: `farm.py`, `episodes/04-qm/delivery/manifest.json`, `episodes/04-qm/qa/QA.md`, `CHECKPOINT.md`.
- Twitter Card: `ventures-apps/tycoonclaws/conteudo/cigano/formatos/tweet-video-card/README.md` e `scripts/render-queue.ps1`.
- Carrossel: skill local `carrossel-video-noticia/SKILL.md` e `references/passo-a-passo.md`.
- Punk Records: `wiki/concepts/cigano-formatos-modulares-radar-repo-reel-2026-09-26.md` e `wiki/concepts/cigano-hypit-v4-processo-producao-2026-09-28.md`.
- Documentação primária: [HyperFrames CLI](https://github.com/heygen-com/hyperframes/blob/main/docs/developers/cli.mdx), [render](https://github.com/heygen-com/hyperframes/blob/main/docs/guides/rendering.mdx), [Hypit quickstart](https://github.com/hypit-ai/hypit/blob/main/docs/quickstart.md), [FFmpeg](https://ffmpeg.org/ffmpeg.html).
