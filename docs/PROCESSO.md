# Processo Repo Reel

Data: 28/09/2026. Fonte do caso real: Hypit V4, projeto em `ventures-apps/tycoonclaws/conteudo/cigano/pesquisa/2026-09-26-terceiro-formato-motion/implementation/hypit-v4`; registro durável na Punk Records: `wiki/concepts/cigano-hypit-v4-processo-producao-2026-09-28.md`.

## 1. Escolher pauta com prova

Comece pelo repositório oficial e seu README. Confirme função, licença, instalação e limites. Procure demonstração real de terceiro; guarde URL, autor, data, trecho visual e o que a pessoa construiu. Não transforme autorrelato em medição ou case comprovado. Registre `claim → prova → limite` no episódio.

## 2. Definir história e oferta

Escreva mistério, mecanismo, prova humana, aplicação concreta e Guilda. O nome da ferramenta aparece na primeira menção. Gancho visual em até 3 s. A prova precisa de tempo para ser vista e narrada; na Hypit V4 isso ampliou o vídeo de 26 para 32 s. O CTA fixo é: “Esse e outros repos estão na nossa Guilda gratuita. Segue pra ter acesso.” Não prometa compatibilidade de IA sem fonte.

## 3. Dirigir imagens e voz

Use browser real com cursor, scroll e foco legível; preserve proporção. Se o post contém vídeo, mostre trechos do vídeo real e identifique a origem. Separe demonstração do usuário e exemplo ilustrativo da equipe. Teste três vozes PT-BR com nomes técnicos e a palavra Guilda. Anote grafia em tela e pronúncia falada. ASR ajuda a encontrar problemas; a escuta humana no celular decide o take.

## 4. Produzir e revisar

O editor único monta HyperFrames, captions com fundo sólido, SFX funcionais e duas versões (música/limpa). Guarde hash do take e das fontes. Renderize MP4 completo e confira com `ffprobe` e loudness com `ffmpeg`; inspecione capa e contato de frames reais. Meta técnica padrão: 1080×1920, 60 fps, −16 a −14 LUFS e pico verdadeiro até −1,5 dBFS. Duração é decisão editorial por episódio; não corte uma prova só para caber em 28 s.

QA técnico/visual e red team editorial operam em paralelo após o render. Checar sem áudio, com áudio e em escala de celular. Corrigir defeitos no render final e revisar de novo. Somente depois decidir sobre postagem, com direitos de mídia e voz aprovados.

## 5. Lote com subagentes

Uma equipe por função atende os episódios do lote. Pesquisa, fatos e casting podem avançar simultaneamente; editor detém composição; QA/red team não a alteram. Cache por hash evita repetir etapas que não mudaram. O Hypit não oferece cache implícito entre builds, por isso a farm usa cache externo e o arquivo `.svrun` precisa explicitar reuso com `build-record`/`satisfy` quando aplicável. Cada episódio tem manifesto, brief, fontes, status de direitos e entregas separados.

## Gates

| Gate | Aceite | Reprova se |
| --- | --- | --- |
| A | Claims e fonte específica; voz PT-BR compreensível | Promessa sem prova, sotaque inadequado ou nome mal falado |
| B | Hook, roteiro, storyboard e CTA | Aplicação vaga, prova passageira, CTA antes do valor |
| Final | MP4, capa, QA visual/copy/marketing/produto | Render parcial, mídia deformada, direito pendente marcado como liberado |

O gate final pode aprovar **avaliação local** sem aprovar publicação. Essa distinção é obrigatória.
