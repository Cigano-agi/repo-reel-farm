estado: bloqueado
pedido: "vamos conectar o Postiz para a automação ficar 360 sem precisar de mim pra pesquisar, criar, modelar e testar?"
resultado: C:/Users/Usuario/orca/projects/repo-reel-farm/postiz_reel.py e docs/POSTIZ.md; manifesto local QM em episodes/04-qm/work/postiz/
verificar: `python -m unittest discover -s tests -q`
proximo:
prova-bloqueio: `python postiz_reel.py channels` → exit 1, "Postiz não autenticado"; `wsl --status` → WSL não instalado; `Get-Command docker` → ausente. Sem instância/canal, não há rascunho remoto nem tela para conferir.
suposicoes:
- Conectar significa preparar o fluxo de rascunho de Reel; agendar/publicar requer destino e calendário específicos.
- O Postiz local preparado em TycoonClaws é o destino pretendido, conforme decisão registrada em 23/09/2026.

## Critérios
- [x] Protocolo de criação e papel do Postiz documentados — prova: `Test-Path docs/POSTIZ.md` → True
- [x] Adaptador prepara manifesto do QM sem upload e informa elegibilidade real — prova: `python postiz_reel.py inspect episodes/04-qm/work/postiz/reel-9a8a1969dda5.manifest.json` → localPrepared true, remoteEligible false
- [x] Borda: mídia ou QA alterados, direitos pendentes, aceite revogado durante upload e duplicata remota bloqueados — prova: `python -m unittest discover -s tests -q` → Ran 9 tests, OK
- [x] Teste que falha sem a mudança e passa com ela — prova: antes: dois testes novos falharam (revogação criou draft; encoding ausente); depois: `python -m unittest tests.test_postiz_reel -q` → Ran 4 tests, OK
- [ ] Postiz autenticado, canal Instagram conferido e rascunho remoto reconciliado — prova: `python postiz_reel.py channels`
- [x] Tela: bloqueio documentado — prova: `wsl --status` → não instalado; `python postiz_reel.py channels` → Postiz não autenticado
- [x] revisor: APROVADO para integração local; 9 testes OK, revogação bloqueada, manifesto QM inelegível; autenticação/canal/rascunho remoto não comprovados.
