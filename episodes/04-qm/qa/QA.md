# QA — Repo Radar 04/14 · QM

**Estado em 28/09/2026:** master técnico privado concluído para avaliação. Voz e direitos ainda dependem de avaliação humana. Não publicado.

## Arquivos finais e medição

| Arquivo | Vídeo | Áudio integrado | Pico verdadeiro |
| --- | --- | ---: | ---: |
| `delivery/04-qm-com-musica.mp4` | H.264, 1080 × 1920, 60 fps, 38,000 s | −15,0 LUFS | −2,8 dBFS |
| `delivery/04-qm-limpo.mp4` | H.264, 1080 × 1920, 60 fps, 38,000 s | −15,0 LUFS | −2,6 dBFS |

Medições feitas com `ffprobe` e `ffmpeg ebur128=peak=true`; detalhes em `qa/metrics.json`. O render HyperFrames em lote terminou com 2/2 variantes e zero falhas. O master com música recebeu mix final por remux de áudio do master limpo normalizado com o bed original a volume 0,5; o stream H.264 foi copiado. A composição em `index.html` registra o mesmo volume para próximos renders. Música original tem média −28,2 dBFS e voz Vlad média −15,4 dBFS; a regulagem de 0,5 coloca o bed cerca de 19 dB abaixo da voz antes do mix final. A versão limpa mantém voz e SFX, sem o bed musical. Não houve escuta humana do balanço, efeitos ou dicção.

## Visual e movimento

- O check HyperFrames final passou com 0 erros de execução, 0 problemas de layout, 0 avisos de movimento e 91/91 verificações de contraste aprovadas. Há 8 avisos de estrutura do Studio: cenas monolíticas recomendadas como subcomposições e mídia duplicada descoberta. Eles não bloquearam o render; são limite de edição fina no Studio.
- Inspeção de frames do master em 0,5; 14,2; 18; 23,5; 24; 25,7; 28; 33 e 37,5 s cobriu gancho, Reddit, Muretai, aplicação e CTA. O defeito de nota Muretai com terceira linha coberta no primeiro render foi corrigido; nos MP4s finais a nota cabe em duas linhas acima da legenda. O Head também fez inspeção independente desses tempos e aprovou a legibilidade.
- Capturas de GitHub mantêm proporção. O nome QM fica visível desde o início. Legendas usam tarja noir sólida acima da zona inferior da interface social. Capa de 2,3 s e contato do master final foram inspecionados visualmente.

## Copy, prova e aplicação

- O [README oficial do QM](https://github.com/yc-software/qm/blob/main/README.md) e a [documentação](https://qm.ycombinator.com/) sustentam a descrição de workspaces por pessoa e sala, memória, arquivos, permissões, sandbox, Slack e web. São claims do fornecedor; a produção não implantou QM nem auditou isolamento.
- O [comentário Reddit](https://www.reddit.com/r/ycombinator/comments/1vc6plb/comment/p1b5k72/) aparece com autor, trecho literal curto, tradução identificada e selo **RELATO DE USO · SEM LOG ANEXADO**. O usuário relata que um agente apontou bug no atualizador dele. Esse relato não valida isolamento, segurança ou desempenho geral do QM. A issue #130 se refere a outro problema e não é apresentada como prova do bug do atualizador.
- A [skill Muretai](https://github.com/muretai/muretai-qm-skill) é rotulada como **skill de terceiro** e fonte separada. Não há identidade verificada entre usuário do Reddit e mantenedor do GitHub.
- A cena de aplicação marca “EXEMPLO ILUSTRATIVO” e mostra sala → documentos permitidos → PR para revisão humana. O WhatsApp também é ilustrativo, sem conversas ou contatos reais.
- CTA visual exato: **“Esse e outros repos estão na nossa Guilda gratuita. Segue pra ter acesso.”** Sem “link na bio”. O red team editorial aceitou a formulação com o limite explícito do relato.

## Voz candidata e limites para publicação

O take selecionado é `Vlad`, preset Higgsfield `text2speech_v2`/ElevenLabs. SHA-256 do MP3 usado: `BD9A6197A41FCE19C489E17D0A95406A9EE0B69681FABCF012D63F8E85B3C427`. Duração 36,996 s; corpo ajustado a 1,50× e CTA a 1,20×. A maior pausa interna medida foi 0,253 s. Foram testadas três vozes Edge PT-BR e alternativas de ritmo Vlad; relatório em `work/voice-casting/VOICE-CASTING.md` (privado). A cotação do job foi 1,95 créditos estimados, sem recibo do débito efetivo. Nenhuma credencial foi gravada no projeto.

ASR reconheceu `Guilda` e o sentido das fontes, mas transcreveu QM como “o que M”, `skill` como “esquil” e `repos` como “rapos”; as grafias corretas estão na tela. O catálogo acessível não comprova localidade nativa PT-BR do preset Vlad. **Sotaque brasileiro, personalidade, nomes técnicos, ritmo percebido e mix devem ser ouvidos por uma pessoa no celular antes de aceitar ou publicar.** A publicação também depende de revisão de direitos das capturas de páginas públicas. Nenhum aceite humano nem publicação foi alegado.
