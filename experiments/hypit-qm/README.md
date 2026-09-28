# Prova QM no Hypit

Prova técnica local de 8 segundos, feita em 28/09/2026 com `@hypit/hypit@0.2.16`. O MP4 está em `output/qm-local-proof-ptbr.mp4` e o contato de quadros em `output/qm-contact-ptbr.jpg` (ambos ignorados pelo Git). O build completo e hash estão em `MANIFEST.json`.

O conteúdo é uma dramatização textual, sem conversa real: QM oferece escopos pessoais e compartilhados, com memória, arquivos e permissões por pessoa ou sala. Fonte: [README oficial do QM](https://github.com/yc-software/qm#what-is-qm). A composição adapta o [exemplo oficial de chat do Hypit](https://github.com/hypit-ai/hypit/tree/main/examples/semantic-composition), sujeito à [licença do Hypit](https://github.com/hypit-ai/hypit/blob/main/LICENSE).

## Reproduzir

Requer Node >=22.15, FFmpeg e FFprobe. O perfil usa Chrome já instalado em `C:/Program Files/Google/Chrome/Application/chrome.exe` e não seleciona HypiHub. Altere `chromePath` se o navegador estiver em outro local.

```powershell
npm.cmd install --ignore-scripts --no-audit --no-fund
npx.cmd tsc -p packages/chat-scene/tsconfig.json
node node_modules/@hypit/hypit/bin/hypit.mjs runtime use hypit.runtime.json
node node_modules/@hypit/hypit/bin/hypit.mjs check main.svml --json
node node_modules/@hypit/hypit/bin/hypit.mjs plan final.svrun --json
node node_modules/@hypit/hypit/bin/hypit.mjs runtime up --json
node node_modules/@hypit/hypit/bin/hypit.mjs build final.svrun --title qm-local-proof-ptbr --follow --json
node node_modules/@hypit/hypit/bin/hypit.mjs get <build-id> --output final.video --to output/qm-local-proof-ptbr.mp4
```

`get` recusa sobrescrever um arquivo existente. Um novo build cria novo ID; não há cache implícito no Hypit. O `runtime up` instala dependências na área compartilhada `%LOCALAPPDATA%/Hypit/packages` e inicia o Worker.

## Limite

Esta prova confirma um vídeo local criado por Author Source `.svml`, Run `.svrun` e Runtime Hypit. Não confirma importação automática de composição HyperFrames existente nem a qualidade de um episódio de 23–28 segundos. O áudio AAC é silencioso: não há narração nem SFX. Nenhuma credencial ou mídia privada entrou no projeto.
