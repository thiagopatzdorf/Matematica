# Referências de design da página pública

Pesquisa feita em 2026-10-06 para a página `site/matematica/` (https://genesisinnovation.io/matematica).
Só texto e links: nenhuma imagem de terceiros entra no repositório. Para cada referência, o que foi visto de
verdade e o princípio que virou decisão na página. Onde a página não carregou no navegador headless
(rede da sessão), isso está dito: o princípio veio da leitura, não da captura.

## Premiados conferidos

A lista de Sites of the Year do Awwwards foi lida em https://www.awwwards.com/websites/sites_of_the_year/
(consulta de 2026-10-06). Os que interessam aqui:

| site | prêmio conferido | capturado? | o que se aprende |
|---|---|---|---|
| [Igloo Inc](https://www.igloo.inc/) (abeto) | Awwwards Site of the Year 2024 | sim, só a tela de carga (o WebGL não subiu no headless) | uma única cena 3D contínua conduzida pela rolagem; carga como ritual, não como espera |
| [Lusion v3](https://lusion.co/) | Awwwards Site of the Year 2023 | não (rede) | partículas e luz como protagonistas; tipografia mínima por cima; movimento lento e com inércia |
| [Persepolis Reimagined](https://persepolis.getty.edu/) (Monks, Getty) | Awwwards Site of the Year 2022 | não (rede) | patrimônio contado em capítulos de tela cheia; cada capítulo uma ideia, com respiro escuro entre eles |
| [Frans Hals Museum](https://www.franshalsmuseum.nl/en/) (Build in Amsterdam) | Awwwards Site of the Year 2018 | não (o servidor recusou) | museu: fotografia grande, texto curto, muito vazio; a obra fala, a interface some |
| [Active Theory](https://activetheory.net/) | Awwwards Site of the Year 2018 (v4) | parcial (o WebGL falhou na captura) | cena em tempo real com fallback; o conteúdo não espera a cena |

## Referências editoriais e científicas (sem prêmio conferido aqui)

| site | capturado? | o que se aprende |
|---|---|---|
| [Bartosz Ciechanowski, *Moon*](https://ciechanow.ski/moon/) | sim | começa claro e simples e, quando o assunto pede, a página **vira noite** para a cena; cada figura interativa explica uma coisa só, logo depois do parágrafo que a pede |
| [Distill, *Why Momentum Really Works*](https://distill.pub/2017/momentum/) | sim | título serifado centrado, muito branco em volta, figura interativa antes do texto denso; citação e autoria como parte do desenho |
| [Stripe Press](https://press.stripe.com/) | sim (fundo escuro com cena carregando) | livro como objeto: escuro aveludado, serifada clássica, quase nenhum elemento de interface |
| [The Pudding](https://pudding.cool/) | sim | explicação de dados passo a passo, uma pergunta por tela, rolagem que revela |

## Princípios extraídos e onde estão na página

1. **Uma cena contínua comandada pela rolagem** (Igloo, Lusion, Active Theory). O prólogo é uma rolagem
   longa com o palco preso: as 117 649 palavras de ℤ₇⁶ vão do caos à grade e à cobertura por 14 esferas.
   O progresso da rolagem é suavizado (a cena persegue a rolagem com inércia), para o movimento ser lento.
2. **Uma frase por vez, como verso** (The Pudding, Persepolis). Os versos do prólogo aparecem e somem um a
   um, centrados, com o resto da tela vazio.
3. **O conteúdo não espera a cena** (Active Theory, Ciechanowski). O texto é HTML puro e aparece antes de
   qualquer script; sem WebGL fica uma imagem estática do estado final; com `prefers-reduced-motion`, a
   rolagem longa some e tudo aparece de uma vez, com a cena parada no estado final.
4. **Virar noite quando o assunto pede** (Ciechanowski, Stripe Press). O prólogo, as cotas de Kéri e o
   horizonte dos Problemas do Milênio são sempre noturnos; o resto acompanha o tema do visitante.
5. **Fotografia grande, texto curto, ouro só em fios** (Frans Hals, Stripe Press). Cinco fotografias do
   Unsplash, tonalizadas em grafite e marfim; ouro apenas em filetes de 1 px, numerais e ênfases.
6. **Figura logo depois da frase que a pede** (Ciechanowski, Distill). O cubo Q₃/Q₄ interativo fica ao lado
   da explicação em quatro níveis; a fórmula da cota da esfera vem com o exemplo numérico do prólogo.
7. **Escala e vazio pela razão áurea.** Espaçamentos em potências de φ (0,618 · 1 · 1,618 · 2,618 · 4,236 ·
   6,854 · 11,09 rem), colunas 1 : 1,618, numerais de estilo antigo.
8. **Honestidade como desenho.** A legenda do prólogo diz o que é visualização e o que é dado; a frase do
   ledger aparece literal; "potencialmente novo" sempre com a ressalva; o navegador do visitante confere a
   cobertura e diz quanto tempo levou.

## O que não foi copiado

Nenhuma marca, fonte proprietária, imagem ou trecho de código das referências. O WebGL da página é escrito
do zero (WebGL 1, sem biblioteca), as fontes são Cormorant Garamond e Inter (Google Fonts) e as fotos têm
licença Unsplash, com crédito no rodapé da página.
