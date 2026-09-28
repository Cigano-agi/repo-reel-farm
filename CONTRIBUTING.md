# Editar com sua LLM

1. Faça fork ou crie branch. Copie `episodes/example/` para uma pasta com slug próprio e preencha `episode.json`/`BRIEF.md`.
2. Configure seu CLI em `providers.json` a partir de `providers.example.json`. O adapter precisa aceitar `{prompt}`, `{workspace}` e `{output}`; deve devolver JSON com `status`, `summary`, `evidence[]`, `outputs[]`, `issues[]`. Restrinja escrita ao workspace indicado. O exemplo Codex usa `--sandbox workspace-write`.
3. Execute `python farm.py episodes/seu-slug --mock` para conferir a DAG e depois sem `--mock` para acionar o provider. Para várias pautas, edite `episodes/batch.example.json` e use `--batch-file` com um limite global de workers.
4. Revise claims contra links específicos. Rotule transcrições e exemplos. Só o produtor altera a composição; QA e red team escrevem pareceres em seus workspaces. Antes de declarar entregue, confira os dois MP4s, capa, contato, voz, SFX, safe zone e direitos.
5. Faça PR com manifesto, fontes, composição e QA. Não inclua vozes, MP4, capturas de terceiros, `.env`, chaves nem dados privados; esses arquivos são ignorados por padrão. Indique como reproduzir os ativos quando isso for permitido.

`pipelinePassed` significa que os papéis concluíram os gates automáticos. `publicationReady` só fica verdadeiro com direitos registrados e aprovação humana de voz/editorial. A ferramenta nunca posta automaticamente.

O exemplo Hypit tem [licença própria](experiments/hypit-qm/LICENSE-HYPIT.txt); ela difere da MIT que cobre a farm e a documentação geral.
