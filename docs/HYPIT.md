# Hypit no fluxo

Hypit é uma ferramenta separada do HyperFrames. O repositório oficial é [hypit-ai/hypit](https://github.com/hypit-ai/hypit), com [quickstart](https://github.com/hypit-ai/hypit/blob/main/docs/quickstart.md). O piloto Repo Reel usou HyperFrames para o render final. Nesta farm, Hypit entra como experimento reprodutível do próximo episódio, sem substituir automaticamente o editor ou o motor de render. O pacote é dependência fixada em `tools/hypit/package.json`, não código copiado do Hypit.

## Instalação isolada

```powershell
npm.cmd --prefix tools/hypit install
npm.cmd --prefix tools/hypit run hypit -- --version
```

Para `doctor`, `plan` e `build`, entre em `experiments/hypit-qm/` e siga seu [README](../experiments/hypit-qm/README.md); o perfil `hypit.runtime.json` pertence àquela pasta.

Node >=22.15, FFmpeg/FFprobe e um Chrome compatível são necessários para as funções de render. Fixe a versão e registre o build ID no episódio. Não coloque tokens no repositório; use variáveis de ambiente e `.env` local ignorado. Um perfil local pode usar `media.local` e `hyperframes.local` sem endpoint HypiHub quando a fonte não o exige. A licença do Hypit é Apache 2.0 modificada, com condições para redistribuição comercial e serviço multiempresa; leia a [licença oficial](https://github.com/hypit-ai/hypit/blob/main/LICENSE) antes de embutir o software em outro produto.

## Cache

O Hypit não reaproveita builds implicitamente. O cache de `farm.py` evita rerodar agentes quando a entrada relevante não mudou. Para reutilizar artefatos dentro do Hypit, declare `build-record` e `satisfy` no `.svrun` conforme a documentação oficial. Um build novo cria ID novo. A presença de um MP4 anterior não prova que o novo foi produzido pelo Hypit.

## Teste do próximo episódio

O piloto 04/14 é QM (`yc-software/qm`). O teste mínimo foi concluído em 28/09/2026 em `experiments/hypit-qm/`: Author Source `.svml`, pacote editável, `.svrun`, Runtime local e MP4 de **8 s, 540×960/30 fps**, sem endpoint pago. O build ID e SHA-256 estão em `MANIFEST.json`; o contato visual foi inspecionado. O arquivo é uma dramatização textual ilustrativa da arquitetura QM, sem voz, CTA ou prova social. O Reel final continua em produção com HyperFrames. O teste não demonstra importação automática entre os motores.
