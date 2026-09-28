# QM — matriz de prova (28/09/2026)

| Afirmação usada | Fonte específica | Limite editorial |
| --- | --- | --- |
| QM é um harness colaborativo para trabalho em Slack e web. | [README oficial](https://github.com/yc-software/qm/blob/main/README.md), [documentação](https://qm.ycombinator.com/) | Descrição do fornecedor; não é teste desta produção. |
| Cada pessoa e sala tem memória, arquivos, permissões e sandbox durável em escopo próprio. | [README oficial](https://github.com/yc-software/qm/blob/main/README.md), [documentação](https://qm.ycombinator.com/) | “Isolado” é postura padrão e depende da configuração e implantação. Não prometer segurança absoluta; consultar `SECURITY.md`. |
| A equipe usa Slack ou web e escolhe harness/modelo. | [README oficial](https://github.com/yc-software/qm/blob/main/README.md) | Não afirmar compatibilidade testada aqui. |
| Um usuário relata deploy real da 0.1.4 em Fly, sandbox persistente e agente que encontrou um bug no atualizador dele. | [Comentário de u/Smooth-One-9514](https://www.reddit.com/r/ycombinator/comments/1vc6plb/comment/p1b5k72/) | Autorrelato textual, sem screenshot ou log anexado. A issue #130 sustenta a menção separada ao problema de `SPRITES_TOKEN`, não comprova o bug do atualizador do autor. |
| Há uma skill pública que conecta QM à rede Muretai. | [Repositório muretai/muretai-qm-skill](https://github.com/muretai/muretai-qm-skill) | Fonte separada; não há vínculo verificado entre o pseudônimo do Reddit e a conta GitHub Muretai. O README descreve o fluxo de convite/cotação, sem auditoria independente nesta produção. |
| Uma sala poderia pesquisar documentos autorizados e preparar um PR para revisão. | [Documentação oficial, possibilidades de uso](https://qm.ycombinator.com/) | Exemplo editorial ilustrativo. Não é resultado observado nem automação implantada aqui. |

## Capturas e direitos

Capturas próprias de páginas públicas oficiais em 28/09/2026: `assets/browser/qm-repo.png`, `qm-readme.png`, `qm-docs.png`, `muretai-repo.png`. Usadas para identificar fonte e explicar funcionamento em piloto privado. O comentário do Reddit será transcrito em card com crédito e identificado como transcrição; nenhum vídeo de terceiro será incorporado. A publicação requer revisão de direitos e aceite humano.

## Red lines

- Rejeitar: “A Y Combinator deu um agente para cada funcionário”. O material oficial diz que QM dá espaços separados por pessoa e sala e que YC o desenvolveu/usou, não prova implantação universal.
- Rejeitar: autor do Reddit = mantenedor do repositório Muretai. Não há prova de identidade.
- Rejeitar: o caso do Reddit comprova desempenho, segurança ou ausência de custo. É autorrelato.
- A implantação exige infraestrutura, credenciais e política de acesso; o software não foi implantado nesta produção.
