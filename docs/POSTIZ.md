# Postiz no Repo Reel Farm — 28/09/2026

**Estado verificado:** conector local de Reel preparado e testado sem upload. A CLI `postiz@2.0.16` existe em `%LOCALAPPDATA%/CiganoTools/postiz/`, mas `auth:status` respondeu `Not authenticated`; `integrations:list` falhou. A instância local preparada em TycoonClaws não iniciou: `wsl --status` informa que WSL não está instalado e `docker` não foi encontrado. Não há canal Instagram confirmado, rascunho remoto nem postagem.

## O que o Postiz resolve

Postiz é a etapa de distribuição: receber mídia, criar rascunho, agendar e observar a publicação. A [API oficial](https://docs.postiz.com/public-api/posts/create) separa `draft`, `schedule` e `now`; `draft` não publica. O [upload oficial](https://docs.postiz.com/cli/media-upload) devolve ID e URL de mídia. Para Instagram, um Reel de vídeo único usa `post_type: "post"` no [schema do provedor](https://docs.postiz.com/public-api/providers/instagram). O conector deste repo implementa somente **rascunho**, após gate de direitos e aceite. Não há comando de agendamento/publicação aqui.

Postiz não descobre pautas, verifica fatos, escreve roteiro, gera voz, monta cenas nem aprova vídeo. Essas etapas pertencem à farm. Hoje `farm.py` orquestra papéis por episódio já definido; o lote simulado e um worker factual real foram testados, mas não existe radar autônomo e a farm não produziu um episódio completo de ponta a ponta sem direção humana. Portanto **360 sem Fabrício ainda não está operacional**.

## Protocolo atual para criar outro vídeo

1. Criar pasta do episódio a partir de `episodes/example/` e preencher `episode.json` + `BRIEF.md` com fonte, uso concreto e CTA. A pauta ainda precisa ser escolhida/validada; não afirmar descoberta automática.
2. Rodar `python farm.py episodes/<slug> --provider codex`. Pesquisa/fatos e casting podem ocorrer em paralelo; gates bloqueiam claims sem prova. O editor detém a composição e QA/red team revisam o MP4 final. A farm exige dois masters, capa, contato e HTML para o papel produtor.
3. Conferir `work/run.json`, QA, escuta da voz e direitos. `pipelinePassed` indica que os papéis passaram; `publicationReady` exige direitos e aprovações específicas. Não mudar flags só para destravar o upload.
4. Escrever legenda em `episodes/<slug>/work/postiz/LEGENDA.txt`, com fonte e limite factual. Preparar manifesto: `python postiz_reel.py prepare episodes/<slug> --caption work/postiz/LEGENDA.txt`. O manifesto tem hashes de MP4, QA, legenda, episódio e resultado da farm; `inspect` aponta `remoteEligible`.
5. Com instância autenticada e canal correto, `python postiz_reel.py channels` confirma ID e perfil. Após aceite do episódio, `python postiz_reel.py draft <manifesto> --integration <ID>` faz upload e cria **um rascunho**, com recibo local. Falha parcial vira `needs_reconciliation`; conferir o calendário antes de tentar de novo.
6. Um pedido posterior com pauta, destino e calendário pode liberar agendamento. Depois, conferir post remoto e métricas reais. `scheduled` não significa `published`.

O QM foi preparado localmente com uma legenda que distingue descrição oficial, aplicação ilustrativa e autorrelato Reddit. `inspect` retornou `remoteEligible: false`: a voz Vlad ainda não teve aceite humano e capturas de páginas ainda têm direitos pendentes. Nada foi enviado ao Postiz.

## O que falta para o 360

| Frente | Entrega necessária | Estado em 28/09/2026 |
| --- | --- | --- |
| Radar autônomo | Coletar candidatos datados, deduplicar, validar novidade e artefato visual, registrar direitos | Planejado; não implementado |
| Produção sem brief manual | Gerar e revisar `episode.json`/brief por contrato; executar farm real até dois masters | Farm existente exige entrada preparada; só um papel real e lote mock foram testados |
| QA automático + revisão | Métricas técnicas, frames, pausas, claims e defeitos concretos; erro volta ao editor | Parcial nos pilotos; não comprovado para lote autônomo |
| Distribuição | Instância Postiz saudável, OAuth/API key, Instagram profissional correto, primeiro rascunho e teste controlado de formato | Conector local testado; autenticação/instância/canal ausentes |
| Aprendizado | IDs remotos, estado `published`, métricas por janela e comparação com baseline | Não implementado |

**Próxima intervenção indispensável para conexão real:** habilitar WSL e Docker Desktop no Windows, iniciar a stack local preparada, criar/autorizar a conta e conectar o Instagram profissional no Postiz. Isso inclui login/OAuth da Meta, que pode exigir ação do titular. O projeto anterior já tem instruções e Compose em `ventures-apps/tycoonclaws/conteudo/cigano/agencia/postiz/LOCAL.md`; não duplicar stack nem credenciais no repo público. A [documentação oficial de self-host e Instagram](https://docs.postiz.com/self-host/providers/instagram) exige app Meta e fluxo OAuth. Sem canal autenticado, o teste remoto não pode ser declarado concluído.

## Limites de segurança

- `postiz_reel.py draft` só opera quando `work/run.json` declara `publicationReady: true`, os direitos têm estados liberados e há aceite de áudio/editorial no episódio. Hashes impedem usar outro arquivo sem novo manifesto. Esses campos são registro operacional, não assinatura criptográfica de uma pessoa.
- O manifesto e os recibos ficam em `work/`, fora do Git; nenhum token entra no projeto. O comando remoto não faz retry de criação. Recibo/lock existentes exigem reconciliação no Postiz.
- A conta e o destino são conferidos antes do upload. O conector não envia caption nem mídia por shell construído a partir de texto do usuário.
- A checagem de direitos e a escuta do QM continuam pendentes. A V4 Hypit usa vídeo de terceiro e requer confirmação de uso público antes de qualquer postagem.
