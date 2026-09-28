# Ponto de integração Hypit

O Reel principal de **38 s** é produzido em HyperFrames. Uma prova curta de **8 s** foi renderizada separadamente em Hypit, em `../../experiments/hypit-qm/`; ela não substitui o render principal nem gerou o Reel inteiro.

Conforme auditoria de 28/09/2026 em `hypit-v4-integracao.md` (projeto de pesquisa original), o executável é `@hypit/hypit@0.2.16`, requer Node >=22.15, FFmpeg/FFprobe. O fluxo previsto é `hypit check`, `hypit plan`, `hypit runtime up`, `hypit build --follow`, `hypit get <id> --output final.video --to final.mp4`. O `final.svrun` deve apontar para `main.svml` e para `<target output="final.video"/>`.

**Estado em 28/09/2026:** o agente de fatos resolveu o Chrome Headless Shell e executou um build local de oito segundos, 540 × 960, 30 fps, três requests locais e zero pagos. Build ID: `bld_20260928T153840532Z_EFF8C009EF`. Arquivo privado: `../../experiments/hypit-qm/output/qm-local-proof-ptbr.mp4`. O contato em `work/hypit-proof-contact.jpg` mostra uma interface ilustrativa de equipe e QM com textos sobre escopo; não é captura do produto QM.

O trecho não será embutido no Reel principal: seu visual difere do padrão editorial aprovado e poderia ser confundido com interface real do QM. O resultado comprova somente que este projeto local conseguiu planejar/renderizar uma prova curta por Hypit sem request pago. Fidelidade, edição no Studio, uso de media de terceiros e produção do episódio completo por Hypit continuam não testados. O render HyperFrames em `delivery/` é o piloto principal.
