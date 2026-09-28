# Repo Radar 04/14 — QM

Piloto privado, vertical 1080 × 1920, 60 fps, 38 s. O Reel principal é uma composição HyperFrames editável em `index.html`; não foi publicado.

## Entrega local

- `delivery/04-qm-com-musica.mp4` — master com voz, SFX e música.
- `delivery/04-qm-limpo.mp4` — voz e SFX, sem música.
- `delivery/04-qm-capa.png` — capa extraída do gancho.
- `delivery/04-qm-contato.jpg` — contato de frames do master.
- `qa/QA.md` e `qa/metrics.json` — inspeção e medições.

Os arquivos em `delivery/`, `assets/` e `work/` são privados e ficam fora do Git por `.gitignore`. Um clone público contém manifesto, pesquisa, storyboard e código, mas precisa dos assets locais para abrir e renderizar a composição.

## Abrir e renderizar

Na pasta deste episódio, com Node e FFmpeg disponíveis:

```powershell
npx.cmd --yes hyperframes@0.8.82 check
npx.cmd --yes hyperframes@0.8.82 preview
```

`index.html` contém as sete cenas e as faixas de voz, música e SFX. `batch.json` define os dois masters. A composição usa capturas próprias de páginas públicas, fontes locais e sons gerados por código. Os desenhos de trabalho em equipe e WhatsApp são ilustrativos.

## Fontes e limites

Matriz de claims em `RESEARCH.md`: [QM oficial](https://github.com/yc-software/qm), [docs](https://qm.ycombinator.com/), [relato de usuário no Reddit](https://www.reddit.com/r/ycombinator/comments/1vc6plb/comment/p1b5k72/) e [skill Muretai](https://github.com/muretai/muretai-qm-skill), fonte separada. Não há vínculo verificado entre o usuário do Reddit e o mantenedor da skill. O relato não traz log anexado.

A voz Vlad é **candidata**, sem locale PT-BR comprovado no catálogo e sem escuta humana nesta produção. Antes de publicar, ouvir no celular e revisar direitos das capturas. O teste Hypit separado de 8 s está descrito em `HYPIT-INTEGRATION.md`; o Reel de 38 s foi produzido em HyperFrames.
