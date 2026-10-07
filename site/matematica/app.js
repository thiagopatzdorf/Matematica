/* Matemática — página única em PT · EN · FR. Sem framework, sem rede além de JSON do mesmo diretório.
   O HTML traz o texto embutido em português (fallback): se conteudo.<lang>.json, conteudo.json ou
   dados.json faltarem ou vierem quebrados, a página continua inteira. Os rótulos fixos da interface
   vêm do dicionário abaixo; o português deles é o próprio HTML (uma cópia só).
   ?lang=pt|en|fr escolhe o idioma; ?exemplo lê os *.exemplo.json (desenvolvimento). */
(function () {
  "use strict";

  var ESTADOS = ["CLAIMED", "WITNESS_CHECKED", "CERTIFICATE_VERIFIED", "FORMALIZED", "INDEPENDENTLY_REPRODUCED"];
  // Regra de honestidade do projeto: estas três células são "potencialmente novas" —
  // não encontradas na literatura que pesquisamos (docs/exatos/NOVIDADE_V09.md).
  var POTENCIALMENTE_NOVO = { "K3(6,2)": 1, "K7(6,4)": 1, "K7(5,3)": 1 };
  var REPO = "https://github.com/thiagopatzdorf/Matematica/blob/main/";
  var IDIOMAS = ["pt", "en", "fr"];
  var HTML_LANG = { pt: "pt-BR", en: "en", fr: "fr" };
  var reduzir = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Números embutidos (ledger/COBERTURA.md e ledger/cells.json, v0.10.0). Valem só quando dados.json falta;
  // a página diz isso no carimbo da seção de números.
  var DADOS_EMBUTIDOS = {
    versao: "0.10.0", doi: "10.5281/zenodo.23214556", doi_conceito: "10.5281/zenodo.23085769", celulas_total: 1145, exatas: 524, abertas: 621,
    superiores_por_estado: { CLAIMED: 444, WITNESS_CHECKED: 1, CERTIFICATE_VERIFIED: 0, FORMALIZED: 579, INDEPENDENTLY_REPRODUCED: 121 },
    inferiores_por_estado: { CLAIMED: 1138, WITNESS_CHECKED: 0, CERTIFICATE_VERIFIED: 5, FORMALIZED: 2, INDEPENDENTLY_REPRODUCED: 0 },
    destaques: [
      { celula: "K3(6,2)", antes: "15–17", agora: "= 17", estado_lb: "CERTIFICATE_VERIFIED", estado_ub: "INDEPENDENTLY_REPRODUCED", fonte: "docs/exatos/NOVIDADE_V09.md" },
      { celula: "K7(6,4)", antes: "13–15", agora: "= 14", estado_lb: "CERTIFICATE_VERIFIED", estado_ub: "INDEPENDENTLY_REPRODUCED", fonte: "docs/exatos/NOVIDADE_V09.md" },
      { celula: "K7(5,3)", antes: "15–17", agora: "= 17", estado_lb: "CERTIFICATE_VERIFIED", estado_ub: "INDEPENDENTLY_REPRODUCED", fonte: "docs/exatos/NOVIDADE_V09.md" },
      { celula: "K4(7,4)", antes: "9–10", agora: "= 10", estado_lb: "CERTIFICATE_VERIFIED", estado_ub: "WITNESS_CHECKED", fonte: "docs/exatos/FIBRAS_RAIO_GERAL.md" },
      { celula: "K7(4,2)", antes: "17–19", agora: "= 19", estado_lb: "FORMALIZED", estado_ub: "FORMALIZED", fonte: "docs/exatos/LEAN_K742.md" },
      { celula: "K7(9,4)", antes: "≤ 1475", agora: "≤ 1134", estado_lb: "CLAIMED", estado_ub: "INDEPENDENTLY_REPRODUCED", fonte: "ledger/COBERTURA.md" }
    ]
  };

  /* ——— Dicionário 1: textos do HTML (data-i / data-i-aria). O português é o HTML. ——— */
  var LEDGER = "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.";
  var CLAY = '<a href="https://www.claymath.org/millennium-problems/">claymath.org</a>';
  var UI = {
    en: {
      "v.0": "There is a space with <b class=\"n\">117,649</b> points.",
      "v.1": "Each point is a six-letter word over a seven-letter alphabet.",
      "v.2": "How many spheres of radius 4 are enough to touch them all?",
      "v.3": "The literature said: between thirteen and fifteen.",
      "v.4": "Fourteen are enough. With thirteen, there is no way.",
      "v.5": "Anyone can check all 117,649, one by one.",
      "prologo.rolar": "scroll slowly",
      "prologo.legenda": "Visualisation of a real code: the 14 words of <code>data/codes/q7_n6_R4_M14.txt</code> and the 117,649 words of ℤ<sub>7</sub><sup>6</sup>, each carried to the sphere of a centre within distance 4, layered by distance. K<sub>7</sub>(6,4) = 14 is potentially new: not found in the literature we searched. The upper bound was independently reproduced; the lower bound is a certificate checked by a verifier, outside Lean.",
      "formula.rotulo": "The sphere bound: no code covers with fewer words than",
      "formula.nota": "For K<sub>7</sub>(6,4): 117,649 ÷ 24,337 ≈ 4.8, so at least 5. The truth is 14: the distance between that floor and the real value is where the work lives.",
      "keri.nota": "“Potentially new”: not found in the literature we searched (docs/exatos/NOVIDADE_V09.md). For K<sub>7</sub>(5,3), the upper bound 17 now has our own 17-word code and a Lean theorem; its lower bound is a verified certificate outside Lean.",
      "rodape.fotos": "Photographs (Unsplash licence), toned for this page:",
      "pular": "Skip to content", "marca": "Mathematics, home", "secoes": "Index", "tema": "Toggle light and dark theme", "idioma": "Language",
      "hero.sobre": "State collapse · local entropy reversal",
      "hero.titulo": "Discovery is expensive. <em>Verification</em> is cheap.",
      "hero.subtitulo": "A ledger of covering-code bounds where every number moves up a state only when someone checks it — and at the top of the ladder, the checker is the Lean kernel.",
      "hero.rotuloLedger": "What this repository is", "hero.btnNumeros": "See the numbers", "hero.btnRepo": "Repository on GitHub",
      "hero.canvas": "Animation: points scattered at random settle onto a grid and are covered, with no gaps and no overlaps, by five-point crosses — the radius-1 spheres of the Lee metric.",
      "hero.legenda": "<i>From chance to covering.</i> Every point of the discrete plane lies within distance 1 (Lee metric) of exactly one centre: the radius-1 spheres, five-point crosses, tile the plane perfectly.",
      "n.entenda": "Explained", "n.manifesto": "Manifesto", "n.principios": "Principles", "n.metodo": "Method", "n.numeros": "Numbers",
      "n.keri": "Kéri", "n.james": "James", "n.horizonte": "Horizon", "n.citar": "Cite",
      "m.entenda": "§ The problem, explained", "m.manifesto": "I. Manifesto", "m.principios": "II. Principles", "m.metodo": "VII. The ladder",
      "m.keri": "III. Kéri bounds", "m.numeros": "IV. Live numbers", "m.james": "V. The James theorem", "m.horizonte": "VI. Horizon",
      "m.lacunas": "VIII. Honest gaps", "m.citar": "IX. Cite",
      "r.entenda": "The problem, explained", "r.manifesto": "Manifesto", "r.principios": "Principles", "r.metodo": "The ladder",
      "r.numeros": "Live numbers", "r.keri": "Kéri bounds", "r.james": "The James theorem", "r.horizonte": "Horizon",
      "r.lacunas": "Honest gaps", "r.citar": "Links and citation",
      "h.entenda": "Cover everything with the <em>fewest</em>.", "h.manifesto": "Every expensive discovery should become a <em>cheap verification</em>.",
      "h.principios": "The axioms of the <em>craft</em>.", "h.metodo": "Against the unproved, a ladder of <em>states</em>.", "h.numeros": "The ledger, <em>counted</em>.",
      "h.keri": "How many spheres cover the <em>space</em>?", "h.james": "The philosophy, <em>compiled</em>.",
      "h.horizonte": "The seven <em>Millennium</em> Problems.", "h.lacunas": "What is <em>not</em> proved yet.", "h.citar": "Check it <em>yourself</em>.",
      "entenda.lede": "The same question at four depths. Pick yours.", "entenda.niveis": "Level of explanation",
      "nivel.0": "In 30 seconds", "nivel.1": "High school", "nivel.2": "Undergraduate", "nivel.3": "Research",
      "cubo.modo": "Cube mode", "cubo.explorar": "Explore", "cubo.solucao": "Solution", "cubo.tente": "Try it",
      "cubo.semjs": "With JavaScript this cube is interactive: click a word to see its radius-1 sphere.", "glossario": "Glossary",
      "tr.0": '<b>chaos</b> <span class="seta" aria-hidden="true">→</span> structure',
      "tr.1": '<b>implicit</b> <span class="seta" aria-hidden="true">→</span> explicit',
      "tr.2": '<b>ambiguity</b> <span class="seta" aria-hidden="true">→</span> metric',
      "tr.3": '<b>discovery</b> <span class="seta" aria-hidden="true">→</span> verification',
      "metodo.lede": "Every bound starts as a claim and climbs one step only when a more demanding instrument checks it. States are cumulative.",
      "escada.titulo": "Upper bounds by state",
      "e.CLAIMED": "Stated in the literature; nothing checked here.", "e.WITNESS_CHECKED": "Explicit code checked by a program.",
      "e.CERTIFICATE_VERIFIED": "Certificate checked by a verifier (the typical state of a lower bound).",
      "e.FORMALIZED": "Theorem accepted by the Lean 4 kernel.", "e.INDEPENDENTLY_REPRODUCED": "In Lean and reproduced along a second, independent path.",
      "numeros.lede": LEDGER + " The table as a whole has not been formally verified: every bound carries its own state, and most lower bounds are still inherited from the literature.",
      "num.celulas": "K<sub>q</sub>(n,R) cells in the ledger", "num.exatas": "exact: lower bound equals upper bound", "num.abertas": "still open",
      "num.lean": "upper bounds in Lean (FORMALIZED or above)", "barra.rotulo": "Upper bounds, by state",
      "keri.formula": "K<sub>q</sub>(n,R) = the smallest code in ℤ<sub>q</sub><sup>n</sup> whose Hamming spheres of radius R cover everything.",
      "keri.resumo": "Gerzson Kéri’s tables collect, for each alphabet size q, length n and radius R, the best known lower and upper bounds. Every cell with an open interval is a question: is there a smaller code, or can one prove there is none?",
      "keri.porque": "It is the ideal ground for the method: finding a code is expensive, checking that it covers is cheap and exact. Closing a cell turns a band of uncertainty into a number — and leaves the proof where anyone can check it.",
      "james.resumo": "The three pillars of James’s philosophy — knowledge, safety and soul — proved in Lean 4, without Mathlib and without <code>sorry</code>. Writing the proofs was search; checking them is the kernel, in milliseconds.",
      "james.fronteira": "<strong>Boundary.</strong> The theorems hold for the models defined there, not for production code: <em>if</em> the system behaves like the model, <em>then</em> the properties hold.",
      "horizonte.lede": "In 2000 the Clay Mathematics Institute chose seven problems and offered US$1 million for each solution. One has been solved; six remain open.",
      "horizonte.aviso": "<strong>We have not solved, nor are we attacking, any of these problems.</strong> They appear here as a horizon and as inspiration for the method: questions where discovering and verifying seem to live on different scales. Source for the status: " + CLAY + ".",
      "copiar": "Copy", "bibtex": "BibTeX citation",
      "rodape.epigrafe": "“There is as yet insufficient data for a meaningful answer.”", "rodape.autor": "Isaac Asimov, The Last Question",
      "rodape.nota": "Thiago Patzdorf · Genesis Innovation · content under CC-BY-4.0. This page reads <code>conteudo.json</code> and <code>dados.json</code>; without them it shows the embedded text."
    },
    fr: {
      "v.0": "Il y a un espace de <b class=\"n\">117 649</b> points.",
      "v.1": "Chaque point est un mot de six lettres, sur un alphabet de sept.",
      "v.2": "Combien de sphères de rayon 4 suffisent pour les toucher tous ?",
      "v.3": "La littérature disait : entre treize et quinze.",
      "v.4": "Quatorze suffisent. Avec treize, impossible.",
      "v.5": "Chacun peut vérifier les 117 649, un par un.",
      "prologo.rolar": "faites défiler lentement",
      "prologo.legenda": "Visualisation d’un code réel : les 14 mots de <code>data/codes/q7_n6_R4_M14.txt</code> et les 117 649 mots de ℤ<sub>7</sub><sup>6</sup>, chacun porté vers la sphère d’un centre à distance au plus 4, en couches selon la distance. K<sub>7</sub>(6,4) = 14 est potentiellement nouveau : introuvable dans la littérature que nous avons consultée. La borne supérieure a été reproduite de façon indépendante ; la borne inférieure est un certificat vérifié par un vérificateur, hors de Lean.",
      "formula.rotulo": "La borne des sphères : aucun code ne recouvre avec moins de mots que",
      "formula.nota": "Pour K<sub>7</sub>(6,4) : 117 649 ÷ 24 337 ≈ 4,8, donc au moins 5. La vérité est 14 : l’écart entre ce plancher et la valeur réelle, c’est là que vit le travail.",
      "keri.nota": "« Potentiellement nouveau » : introuvable dans la littérature que nous avons consultée (docs/exatos/NOVIDADE_V09.md). Pour K<sub>7</sub>(5,3), la borne supérieure 17 a désormais notre propre code de 17 mots et un théorème Lean ; sa borne inférieure est un certificat vérifié hors de Lean.",
      "rodape.fotos": "Photographies (licence Unsplash), teintées pour cette page :",
      "pular": "Aller au contenu", "marca": "Mathématiques, accueil", "secoes": "Sommaire", "tema": "Basculer entre thème clair et sombre", "idioma": "Langue",
      "hero.sobre": "Effondrement d’état · inversion locale de l’entropie",
      "hero.titulo": "Découvrir coûte cher. <em>Vérifier</em> coûte peu.",
      "hero.subtitulo": "Un registre de bornes de codes de recouvrement où chaque nombre ne monte d’un état que lorsque quelqu’un le vérifie — et, en haut de l’échelle, le vérificateur est le noyau de Lean.",
      "hero.rotuloLedger": "Ce qu’est ce dépôt", "hero.btnNumeros": "Voir les chiffres", "hero.btnRepo": "Dépôt sur GitHub",
      "hero.canvas": "Animation : des points dispersés au hasard se placent sur une grille et sont recouverts, sans trou ni chevauchement, par des croix de cinq points — les sphères de rayon 1 de la métrique de Lee.",
      "hero.legenda": "<i>Du hasard au recouvrement.</i> Chaque point du plan discret est à distance au plus 1 (métrique de Lee) d’exactement un centre : les sphères de rayon 1, des croix de cinq points, pavent le plan sans reste.",
      "n.entenda": "Comprendre", "n.manifesto": "Manifeste", "n.principios": "Principes", "n.metodo": "Méthode", "n.numeros": "Chiffres",
      "n.keri": "Kéri", "n.james": "James", "n.horizonte": "Horizon", "n.citar": "Citer",
      "m.entenda": "§ Comprendre le problème", "m.manifesto": "I. Manifeste", "m.principios": "II. Principes", "m.metodo": "VII. L’échelle",
      "m.keri": "III. Bornes de Kéri", "m.numeros": "IV. Chiffres en direct", "m.james": "V. Le théorème de James", "m.horizonte": "VI. Horizon",
      "m.lacunas": "VIII. Lacunes assumées", "m.citar": "IX. Citer",
      "r.entenda": "Comprendre le problème", "r.manifesto": "Manifeste", "r.principios": "Principes", "r.metodo": "L’échelle",
      "r.numeros": "Chiffres en direct", "r.keri": "Bornes de Kéri", "r.james": "Le théorème de James", "r.horizonte": "Horizon",
      "r.lacunas": "Lacunes assumées", "r.citar": "Liens et citation",
      "h.entenda": "Tout recouvrir avec le <em>minimum</em>.", "h.manifesto": "Toute découverte coûteuse doit devenir une <em>vérification bon marché</em>.",
      "h.principios": "Les axiomes du <em>métier</em>.", "h.metodo": "Contre le non-prouvé, une échelle d’<em>états</em>.", "h.numeros": "Le registre, <em>compté</em>.",
      "h.keri": "Combien de sphères recouvrent l’<em>espace</em> ?", "h.james": "La philosophie, <em>compilée</em>.",
      "h.horizonte": "Les sept problèmes du <em>millénaire</em>.", "h.lacunas": "Ce qui n’est <em>pas</em> encore prouvé.", "h.citar": "Vérifiez <em>vous-même</em>.",
      "entenda.lede": "La même question, à quatre profondeurs. Choisissez la vôtre.", "entenda.niveis": "Niveau d’explication",
      "nivel.0": "En 30 secondes", "nivel.1": "Lycée", "nivel.2": "Licence", "nivel.3": "Recherche",
      "cubo.modo": "Mode du cube", "cubo.explorar": "Explorer", "cubo.solucao": "Solution", "cubo.tente": "À vous",
      "cubo.semjs": "Avec JavaScript, ce cube est interactif : cliquez sur un mot pour voir sa sphère de rayon 1.", "glossario": "Glossaire",
      "tr.0": '<b>chaos</b> <span class="seta" aria-hidden="true">→</span> structure',
      "tr.1": '<b>implicite</b> <span class="seta" aria-hidden="true">→</span> explicite',
      "tr.2": '<b>ambiguïté</b> <span class="seta" aria-hidden="true">→</span> mesure',
      "tr.3": '<b>découverte</b> <span class="seta" aria-hidden="true">→</span> vérification',
      "metodo.lede": "Chaque borne commence comme une affirmation et ne gravit une marche que lorsqu’un instrument plus exigeant la vérifie. Les états sont cumulatifs.",
      "escada.titulo": "Bornes supérieures par état",
      "e.CLAIMED": "Affirmée dans la littérature ; rien n’a été vérifié ici.", "e.WITNESS_CHECKED": "Code explicite vérifié par un programme.",
      "e.CERTIFICATE_VERIFIED": "Certificat vérifié par un vérificateur (état typique d’une borne inférieure).",
      "e.FORMALIZED": "Théorème accepté par le noyau de Lean 4.", "e.INDEPENDENTLY_REPRODUCED": "Dans Lean et reproduite par un second chemin indépendant.",
      "numeros.lede": LEDGER + " Le tableau dans son ensemble n’a pas été vérifié formellement : chaque borne a son propre état, et la plupart des bornes inférieures sont encore héritées de la littérature.",
      "num.celulas": "cellules K<sub>q</sub>(n,R) dans le registre", "num.exatas": "exactes : borne inférieure égale à la borne supérieure", "num.abertas": "encore ouvertes",
      "num.lean": "bornes supérieures dans Lean (FORMALIZED ou au-delà)", "barra.rotulo": "Bornes supérieures, par état",
      "keri.formula": "K<sub>q</sub>(n,R) = le plus petit code de ℤ<sub>q</sub><sup>n</sup> dont les sphères de Hamming de rayon R recouvrent tout.",
      "keri.resumo": "Les tables de Gerzson Kéri rassemblent, pour chaque alphabet q, longueur n et rayon R, les meilleures bornes inférieure et supérieure connues. Chaque cellule à intervalle ouvert est une question : existe-t-il un code plus petit, ou peut-on prouver qu’il n’y en a pas ?",
      "keri.porque": "C’est le terrain idéal pour la méthode : trouver un code coûte cher, vérifier qu’il recouvre est bon marché et exact. Fermer une cellule transforme une bande d’incertitude en un nombre — et laisse la preuve là où chacun peut la vérifier.",
      "james.resumo": "Les trois piliers de la philosophie de James — connaissance, sécurité et âme — prouvés en Lean 4, sans Mathlib et sans <code>sorry</code>. Écrire les preuves a été une recherche ; les vérifier, c’est le noyau, en millisecondes.",
      "james.fronteira": "<strong>Frontière.</strong> Les théorèmes valent pour les modèles qui y sont définis, pas pour le code de production : <em>si</em> le système se comporte comme le modèle, <em>alors</em> les propriétés valent.",
      "horizonte.lede": "En 2000, le Clay Mathematics Institute a choisi sept problèmes et offert 1 million de dollars pour chaque solution. Un a été résolu ; six restent ouverts.",
      "horizonte.aviso": "<strong>Nous n’avons résolu ni n’attaquons aucun de ces problèmes.</strong> Ils figurent ici comme horizon et inspiration de la méthode : des questions où découvrir et vérifier semblent vivre à des échelles différentes. Source du statut : " + CLAY + ".",
      "copiar": "Copier", "bibtex": "Citation BibTeX",
      "rodape.epigrafe": "« Il n’y a pas encore assez de données pour une réponse significative. »", "rodape.autor": "Isaac Asimov, La Dernière Question",
      "rodape.nota": "Thiago Patzdorf · Genesis Innovation · contenu sous CC-BY-4.0. Cette page lit <code>conteudo.json</code> et <code>dados.json</code> ; sans eux, elle affiche le texte intégré."
    }
  };

  /* ——— Dicionário 2: frases montadas pelo JS ({x} = valor). ——— */
  var S = {
    pt: {
      docTitulo: "Matemática · Colapso de estado",
      metaDesc: LEDGER + " Cotas de Kéri K_q(n,R), o teorema do James e os Problemas do Milênio como horizonte.",
      cotas: "cotas", sup: "Cotas superiores: {x}.", inf: "Cotas inferiores: {x}.",
      lido: "Lido de <code>dados.json</code>: {x}.", geradoEm: "gerado em {x}", commit: "commit {x}", versao: "versão {x}",
      embutido: "Números embutidos na página (ledger/COBERTURA.md, v{v}). Quando <code>dados.json</code> está publicado, esta seção é refeita a partir dele.",
      codigos: "códigos explícitos conferidos por programa",
      novo: "Potencialmente novo", naoAchado: "Não encontrado na literatura que pesquisamos.",
      ubClaimed: "A cota superior só foi anunciada na literatura (CLAIMED); ainda não foi conferida aqui.",
      lbClaimed: "A cota inferior ainda é a da literatura (CLAIMED).",
      mesmo: "Mesmo valor de antes; o que mudou foi o estado de certificação.",
      inferior: "inferior", superior: "superior", fonte: "Fonte: {x}", antes: "antes: ", agora: "agora: ",
      copiado: "Copiado", copieMao: "Selecione e copie",
      palavra: "Palavra {x}", cuboAria: "Hipercubo Q{n}: {N} palavras binárias de {n} bits; arestas ligam palavras que diferem em um bit.",
      paraQ4: "Trocar para o hipercubo Q4", paraQ3: "Voltar ao cubo Q3",
      expl0: "Clique (ou use Tab e Enter) numa palavra para ver a sua <b>esfera de raio 1</b>.",
      expl: "Esfera de raio 1 em torno de <b>{w}</b>: ela e os vizinhos {viz} — {V} de {N} palavras.",
      sol: "<b>{{lista}}</b> cobre as {N} palavras, então {K} ≤ {M}. Menos não dá: cada esfera cobre {V} palavras e ⌈{N}/{V}⌉ = {M}. Logo {K} = {M}.",
      tente0: "Escolha palavras para serem centros. Meta: cobrir as {N} com o menor número possível.",
      falta: "Você escolheu <b>{k}</b>; faltam <b>{f}</b> de {N} palavras (contorno tracejado).",
      minimo: "Cobriu tudo com <b>{k}</b> — o mínimo possível: {K} = {M}.",
      menos: "Cobriu tudo com <b>{k}</b> palavras. Dá para fazer com menos? (o mínimo é {M})",
      conferido: "Seu navegador acabou de conferir as <b class=\"n\">{n}</b>: nenhuma fica a mais de 4 de um centro.<small class=\"verificado\">{ms} ms · data/codes/q7_n6_R4_M14.txt</small>",
      naoConferido: "A conferência no navegador achou {f} palavras descobertas. Algo está errado: não confie nesta página até isso ser explicado."
    },
    en: {
      docTitulo: "Mathematics · State collapse",
      metaDesc: LEDGER + " Kéri bounds K_q(n,R), the James theorem, and the Millennium Problems as a horizon.",
      cotas: "bounds", sup: "Upper bounds: {x}.", inf: "Lower bounds: {x}.",
      lido: "Read from <code>dados.json</code>: {x}.", geradoEm: "generated on {x}", commit: "commit {x}", versao: "version {x}",
      embutido: "Numbers embedded in the page (ledger/COBERTURA.md, v{v}). When <code>dados.json</code> is published, this section is rebuilt from it.",
      codigos: "explicit codes checked by a program",
      novo: "Potentially new", naoAchado: "Not found in the literature we searched.",
      ubClaimed: "The upper bound has only been announced in the literature (CLAIMED); it has not been checked here yet.",
      lbClaimed: "The lower bound is still the one from the literature (CLAIMED).",
      mesmo: "Same value as before; what changed is the certification state.",
      inferior: "lower", superior: "upper", fonte: "Source: {x}", antes: "before: ", agora: "now: ",
      copiado: "Copied", copieMao: "Select and copy",
      palavra: "Word {x}", cuboAria: "Hypercube Q{n}: {N} binary words of {n} bits; edges join words that differ in one bit.",
      paraQ4: "Switch to the Q4 hypercube", paraQ3: "Back to the Q3 cube",
      expl0: "Click (or use Tab and Enter) on a word to see its <b>radius-1 sphere</b>.",
      expl: "Radius-1 sphere around <b>{w}</b>: the word itself and its neighbours {viz} — {V} of {N} words.",
      sol: "<b>{{lista}}</b> covers all {N} words, so {K} ≤ {M}. Fewer is impossible: each sphere covers {V} words and ⌈{N}/{V}⌉ = {M}. Hence {K} = {M}.",
      tente0: "Pick words to be centres. Goal: cover all {N} with as few as possible.",
      falta: "You picked <b>{k}</b>; <b>{f}</b> of {N} words are still uncovered (dashed outline).",
      minimo: "Everything covered with <b>{k}</b> — the minimum possible: {K} = {M}.",
      menos: "Everything covered with <b>{k}</b> words. Can you do it with fewer? (the minimum is {M})",
      conferido: "Your browser has just checked all <b class=\"n\">{n}</b>: none lies farther than 4 from a centre.<small class=\"verificado\">{ms} ms · data/codes/q7_n6_R4_M14.txt</small>",
      naoConferido: "The in-browser check found {f} uncovered words. Something is wrong: do not trust this page until it is explained."
    },
    fr: {
      docTitulo: "Mathématiques · Effondrement d’état",
      metaDesc: LEDGER + " Bornes de Kéri K_q(n,R), le théorème de James et les problèmes du millénaire comme horizon.",
      cotas: "bornes", sup: "Bornes supérieures : {x}.", inf: "Bornes inférieures : {x}.",
      lido: "Lu depuis <code>dados.json</code> : {x}.", geradoEm: "généré le {x}", commit: "commit {x}", versao: "version {x}",
      embutido: "Chiffres intégrés à la page (ledger/COBERTURA.md, v{v}). Quand <code>dados.json</code> est publié, cette section est reconstruite à partir de lui.",
      codigos: "codes explicites vérifiés par un programme",
      novo: "Potentiellement nouveau", naoAchado: "Introuvable dans la littérature que nous avons consultée.",
      ubClaimed: "La borne supérieure n’a été qu’annoncée dans la littérature (CLAIMED) ; elle n’a pas encore été vérifiée ici.",
      lbClaimed: "La borne inférieure est encore celle de la littérature (CLAIMED).",
      mesmo: "Même valeur qu’avant ; ce qui a changé, c’est l’état de certification.",
      inferior: "inférieure", superior: "supérieure", fonte: "Source : {x}", antes: "avant : ", agora: "maintenant : ",
      copiado: "Copié", copieMao: "Sélectionnez et copiez",
      palavra: "Mot {x}", cuboAria: "Hypercube Q{n} : {N} mots binaires de {n} bits ; les arêtes relient les mots qui diffèrent d’un bit.",
      paraQ4: "Passer à l’hypercube Q4", paraQ3: "Revenir au cube Q3",
      expl0: "Cliquez (ou utilisez Tab et Entrée) sur un mot pour voir sa <b>sphère de rayon 1</b>.",
      expl: "Sphère de rayon 1 autour de <b>{w}</b> : le mot lui-même et ses voisins {viz} — {V} mots sur {N}.",
      sol: "<b>{{lista}}</b> recouvre les {N} mots, donc {K} ≤ {M}. Impossible de faire moins : chaque sphère recouvre {V} mots et ⌈{N}/{V}⌉ = {M}. Donc {K} = {M}.",
      tente0: "Choisissez des mots comme centres. Objectif : recouvrir les {N} avec le moins possible.",
      falta: "Vous avez choisi <b>{k}</b> ; il reste <b>{f}</b> mots sur {N} à recouvrir (contour en pointillé).",
      minimo: "Tout est recouvert avec <b>{k}</b> — le minimum possible : {K} = {M}.",
      menos: "Tout est recouvert avec <b>{k}</b> mots. Peut-on faire avec moins ? (le minimum est {M})",
      conferido: "Votre navigateur vient de vérifier les <b class=\"n\">{n}</b> : aucun n’est à plus de 4 d’un centre.<small class=\"verificado\">{ms} ms · data/codes/q7_n6_R4_M14.txt</small>",
      naoConferido: "La vérification dans le navigateur a trouvé {f} mots non recouverts. Quelque chose ne va pas : ne vous fiez pas à cette page tant que ce n’est pas expliqué."
    }
  };

  var idioma = "pt";
  function t(chave, v) {
    var s = (S[idioma] && S[idioma][chave]) || S.pt[chave] || chave;
    return s.replace(/\{\{(\w+)\}\}|\{(\w+)\}/g, function (m, a, b) {
      var k = a || b, val = v && v[k] != null ? v[k] : m;
      return a ? "{" + val + "}" : val;
    });
  }

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  // Texto vindo do JSON: escapa e só então formata K_q(n,R) com subscrito.
  function fmt(s) {
    return esc(s).replace(/\bK_?\{?(\d+|q)\}?\((\d+|n),\s*(\d+|R)\)/g, "K<sub>$1</sub>($2,$3)");
  }
  function chaveCelula(s) { return String(s || "").replace(/[\s_{}]/g, ""); }
  function href(u) {
    u = String(u || "");
    if (/^https?:\/\//.test(u)) return u;
    if (/^[\w.-]+\/[\w./-]+$/.test(u) || /\.(md|json|lean)$/.test(u)) return REPO + u.replace(/^\.?\//, "");
    return "";
  }
  function link(u, rotulo, cls) {
    var h = href(u);
    if (!h) return '<span class="' + (cls || "") + '">' + fmt(rotulo || u) + "</span>";
    return '<a class="' + (cls || "") + '" href="' + esc(h) + '">' + fmt(rotulo || u) + "</a>";
  }
  function arr(x) { return Array.isArray(x) && x.length ? x : null; }
  function txt(x) { return typeof x === "string" && x.trim() ? x : null; }
  function num(x) { return typeof x === "number" && isFinite(x) ? x : null; }
  function milhar(n) { return Number(n).toLocaleString(HTML_LANG[idioma]); }
  function setHTML(sel, html) { var el = typeof sel === "string" ? $(sel) : sel; if (el && html != null) el.innerHTML = html; }

  /* ——— Tema, cabeçalho, entrada suave ——— */
  function iniciarTema() {
    var b = $("#tema");
    if (!b) return;
    b.addEventListener("click", function () {
      var raiz = document.documentElement;
      var escuroAgora = raiz.dataset.theme ? raiz.dataset.theme === "dark"
        : matchMedia("(prefers-color-scheme: dark)").matches;
      raiz.dataset.theme = escuroAgora ? "light" : "dark";
      try { localStorage.setItem("mat-tema", raiz.dataset.theme); } catch (e) { /* sem storage: só nesta visita */ }
      document.dispatchEvent(new Event("mat-tema"));
    });
  }
  function iniciarCabecalho() {
    var topo = $("#topo");
    var noturnas = $$("main .noturno");
    var marcar = function () {
      if (!topo) return;
      topo.classList.toggle("rolou", window.scrollY > 8);
      var y = topo.offsetHeight / 2, sobre = noturnas.some(function (s) { var r = s.getBoundingClientRect(); return r.top <= y && r.bottom >= y; });
      topo.classList.toggle("sobre-noite", sobre);
    };
    window.addEventListener("scroll", marcar, { passive: true });
    marcar();
    $$(".menu a").forEach(function (a) { a.addEventListener("click", function () { $(".menu").removeAttribute("open"); }); });
    if (!("IntersectionObserver" in window)) return;
    var links = $$(".topo nav a");
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.setAttribute("aria-current", a.getAttribute("href") === "#" + e.target.id ? "true" : "false"); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main section[id]").forEach(function (s) { io.observe(s); });
  }
  function iniciarSurge() {
    if (reduzir || !("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("visto"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    $$(".secao .miolo > *").forEach(function (el) {
      // Só esconde o que ainda está abaixo da dobra: nada some na frente do leitor.
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add("surge"); io.observe(el); }
    });
  }

  /* ——— Idioma: o português do HTML é guardado uma vez e restaurado a cada troca ——— */
  var originais = { i: [], a: [], c: [] };
  function guardarOriginais() {
    $$("[data-i]").forEach(function (el) { originais.i.push([el, el.innerHTML]); });
    $$("[data-i-aria]").forEach(function (el) { originais.a.push([el, el.getAttribute("aria-label")]); });
    $$("[data-c]").forEach(function (el) { originais.c.push([el, el.innerHTML]); });
  }
  function aplicarDicionario() {
    originais.c.forEach(function (p) { p[0].innerHTML = p[1]; });
    originais.i.forEach(function (p) {
      var tr = UI[idioma] && UI[idioma][p[0].dataset.i];
      p[0].innerHTML = tr != null ? tr : p[1];
    });
    originais.a.forEach(function (p) {
      var tr = UI[idioma] && UI[idioma][p[0].dataset.iAria];
      p[0].setAttribute("aria-label", tr != null ? tr : p[1]);
    });
    document.documentElement.lang = HTML_LANG[idioma];
    document.title = t("docTitulo");
    var md = $('meta[name="description"]');
    if (md) md.setAttribute("content", t("metaDesc"));
    $$("[data-lang]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.lang === idioma)); });
  }
  function idiomaInicial() {
    var m = /[?&]lang=(pt|en|fr)\b/i.exec(location.search);
    if (m) return m[1].toLowerCase();
    try { var s = localStorage.getItem("mat-idioma"); if (IDIOMAS.indexOf(s) >= 0) return s; } catch (e) { /* segue */ }
    var nav = String((navigator.languages && navigator.languages[0]) || navigator.language || "").toLowerCase();
    return /^fr/.test(nav) ? "fr" : /^pt/.test(nav) ? "pt" : "en";
  }

  /* ——— Conteúdo (conteudo.<lang>.json → conteudo.json) ——— */
  function renderConteudo(c) {
    if (!c || typeof c !== "object") return;
    if (txt(c.titulo)) { setHTML("[data-c=titulo]", fmt(c.titulo)); document.title = c.titulo + " · " + t("docTitulo").split(" · ")[0]; }
    if (txt(c.subtitulo)) setHTML("[data-c=subtitulo]", fmt(c.subtitulo));
    if (arr(c.manifesto)) setHTML("[data-c=manifesto]", c.manifesto.map(function (p) { return "<p>" + fmt(p) + "</p>"; }).join(""));
    if (arr(c.principios)) setHTML("[data-c=principios]", c.principios.map(function (p) {
      return "<li><h3>" + fmt(p.nome) + "</h3><p>" + fmt(p.enunciado) + "</p></li>";
    }).join(""));
    if (arr(c.metodo)) setHTML("[data-c=metodo]", c.metodo.map(function (p) {
      return "<li><b>" + fmt(p.passo) + "</b><span>" + fmt(p.descricao) + "</span></li>";
    }).join(""));
    if (c.keri) {
      if (txt(c.keri.resumo)) setHTML("[data-c='keri.resumo']", fmt(c.keri.resumo));
      if (txt(c.keri.porque_importa)) setHTML("[data-c='keri.porque_importa']", fmt(c.keri.porque_importa));
    }
    if (c.james) {
      if (txt(c.james.resumo)) setHTML("[data-c='james.resumo']", fmt(c.james.resumo));
      if (arr(c.james.teoremas)) setHTML("[data-c='james.teoremas']", c.james.teoremas.map(function (x) {
        return '<article class="teorema"><h3>' + fmt(x.nome) + "</h3><p>" + fmt(x.enunciado) + "</p>" +
          (x.fonte ? link(x.fonte, String(x.fonte).split("/").pop()) : "") + "</article>";
      }).join(""));
    }
    if (arr(c.milenio)) setHTML("[data-c=milenio]", c.milenio.map(function (m) {
      // "Resolvido/Resolvida", "Solved", "Résolu(e)": só a Conjectura de Poincaré, segundo o Clay.
      var resolvido = /^\s*(resolvid|solved|résolu|resolu)/i.test(m.status || "");
      return '<li class="problema"><h3>' + fmt(m.problema) + "</h3><p>" + fmt(m.enunciado_curto) + "</p>" +
        '<span class="status' + (resolvido ? " resolvido" : "") + '">' + fmt(m.status) + "</span></li>";
    }).join(""));
    if (arr(c.lacunas)) setHTML("[data-c=lacunas]", c.lacunas.map(function (l) { return "<li>" + fmt(l) + "</li>"; }).join(""));
    if (arr(c.links)) setHTML("[data-c=links]", c.links.map(function (l) {
      var h = href(l.url);
      return h ? '<li><a href="' + esc(h) + '">' + fmt(l.rotulo) + "</a></li>" : "";
    }).join(""));
    if (c.explicando && arr(c.explicando.camadas)) renderCamadas(c.explicando.camadas);
    if (arr(c.glossario)) setHTML("[data-c=glossario]", c.glossario.map(function (g) {
      return "<dt>" + fmt(g.termo) + "</dt><dd>" + fmt(g.definicao) + "</dd>";
    }).join(""));
  }

  function renderCamadas(camadas) {
    setHTML("#niveis", camadas.map(function (k, i) {
      return '<button role="tab" type="button" id="tab-' + i + '" aria-controls="painel-nivel" aria-selected="' + (i === 0) +
        '"' + (i ? ' tabindex="-1"' : "") + ">" + fmt(k.nivel || ("Nível " + (i + 1))) + "</button>";
    }).join(""));
    setHTML("#painel-nivel", camadas.map(function (k, i) {
      return '<div class="camada" data-nivel="' + i + '"' + (i ? " hidden" : "") + ">" +
        (k.titulo ? "<h3>" + fmt(k.titulo) + "</h3>" : "") +
        (k.texto ? "<p>" + fmt(k.texto) + "</p>" : "") +
        (k.analogia ? '<blockquote class="analogia"><span>' + esc(t("analogia")) + "</span>" + fmt(k.analogia) + "</blockquote>" : "") +
        (k.exemplo ? '<p class="exemplo"><span>' + esc(t("exemplo")) + "</span>" + fmt(k.exemplo) + "</p>" : "") + "</div>";
    }).join(""));
  }

  var nivelAtual = 0;
  function iniciarNiveis() {
    var lista = $("#niveis");
    if (!lista) return;
    var tabs = $$("[role=tab]", lista);
    if (!tabs.length) return;
    function escolher(i, focar, animar) {
      nivelAtual = i;
      tabs.forEach(function (b, j) { b.setAttribute("aria-selected", String(i === j)); b.tabIndex = i === j ? 0 : -1; });
      $$(".camada").forEach(function (k) {
        var on = Number(k.dataset.nivel) === i;
        k.hidden = !on;
        if (on && animar) { k.classList.remove("troca"); void k.offsetWidth; k.classList.add("troca"); }
      });
      $("#painel-nivel").setAttribute("aria-labelledby", tabs[i].id);
      if (focar) tabs[i].focus();
      try { localStorage.setItem("mat-nivel", String(i)); } catch (e) { /* conveniência apenas */ }
    }
    tabs.forEach(function (b, i) {
      b.onclick = function () { escolher(i, false, true); };
      b.onkeydown = function (ev) {
        var k = ev.key, n = tabs.length, alvo = null;
        if (k === "ArrowRight") alvo = (i + 1) % n;
        else if (k === "ArrowLeft") alvo = (i - 1 + n) % n;
        else if (k === "Home") alvo = 0;
        else if (k === "End") alvo = n - 1;
        if (alvo !== null) { ev.preventDefault(); escolher(alvo, true, true); }
      };
    });
    escolher(Math.min(nivelAtual, tabs.length - 1), false, false);
  }

  /* ——— Dados (dados.json, senão DADOS_EMBUTIDOS) ——— */
  function renderDados(d, embutido) {
    if (!d || typeof d !== "object") return;
    var sup = d.superiores_por_estado || {}, inf = d.inferiores_por_estado || {};
    var temLean = num(sup.FORMALIZED) !== null || num(sup.INDEPENDENTLY_REPRODUCED) !== null;
    var vals = { celulas_total: num(d.celulas_total), exatas: num(d.exatas), abertas: num(d.abertas),
      no_lean: temLean ? (num(sup.FORMALIZED) || 0) + (num(sup.INDEPENDENTLY_REPRODUCED) || 0) : null };
    if (vals.abertas === null && vals.celulas_total !== null && vals.exatas !== null) vals.abertas = vals.celulas_total - vals.exatas;
    Object.keys(vals).forEach(function (k) { if (vals[k] !== null) setHTML("[data-d=" + k + "]", milhar(vals[k])); });
    var cv = $("[data-d=codigos_verificados]");
    if (num(d.codigos_verificados) !== null) {
      if (!cv) {
        var div = document.createElement("div");
        div.className = "numero";
        div.innerHTML = '<dd data-d="codigos_verificados"></dd><dt data-t="codigos"></dt>';
        $(".numeros").appendChild(div);
        cv = $("[data-d=codigos_verificados]");
      }
      cv.textContent = milhar(d.codigos_verificados);
      $("[data-t=codigos]").textContent = t("codigos");
    }
    if (ESTADOS.some(function (e) { return num(sup[e]) !== null; })) {
      var total = ESTADOS.reduce(function (s, e) { return s + (num(sup[e]) || 0); }, 0);
      var vivos = ESTADOS.filter(function (e) { return (num(sup[e]) || 0) > 0; });
      setHTML("#barra", vivos.map(function (e) { return '<span class="e-' + e + '" style="flex:' + sup[e] + '"></span>'; }).join(""));
      $("#barra").setAttribute("aria-label", t("sup", { x: vivos.map(function (e) { return milhar(sup[e]) + " " + e; }).join(", ") }));
      setHTML("#legenda", vivos.map(function (e) { return '<li><i class="e-' + e + '"></i>' + e + " · " + milhar(sup[e]) + "</li>"; }).join(""));
      setHTML("#barra-total", milhar(total) + " " + t("cotas"));
      ESTADOS.forEach(function (e) {
        var q = $('[data-ub="' + e + '"]');
        if (q) q.innerHTML = milhar(num(sup[e]) || 0) + "<small>" + esc(t("cotas")) + "</small>";
      });
    }
    var infVivos = ESTADOS.filter(function (e) { return (num(inf[e]) || 0) > 0; });
    if (infVivos.length) setHTML("#inferiores", esc(t("inf", { x: infVivos.map(function (e) { return milhar(inf[e]) + " " + e; }).join(", ") })));
    if (arr(d.destaques)) setHTML("#destaques", d.destaques.map(cartaoDestaque).join(""));
    if (embutido) setHTML("#carimbo", t("embutido", { v: esc(d.versao || "") }));
    else {
      var partes = [];
      if (txt(d.gerado_em)) partes.push(t("geradoEm", { x: esc(d.gerado_em) }));
      if (txt(d.commit)) partes.push(t("commit", { x: '<a href="https://github.com/thiagopatzdorf/Matematica/commit/' + esc(d.commit) + '">' + esc(d.commit.slice(0, 7)) + "</a>" }));
      if (txt(d.versao)) partes.push(t("versao", { x: esc(d.versao) }));
      if (partes.length) setHTML("#carimbo", t("lido", { x: partes.join(" · ") }));
    }
    var pre = $("#bibtex");
    var doi = txt(d.doi) || txt(d.doi_conceito); // DOI da versão citada; o de conceito só se faltar
    if (pre && doi) pre.textContent = pre.textContent.replace(/doi\s*=\s*\{[^}]*\}/, "doi     = {" + doi + "}");
    if (pre && txt(d.versao)) pre.textContent = pre.textContent.replace(/version\s*=\s*\{[^}]*\}/, "version = {" + d.versao.replace(/^v/, "") + "}");
  }

  function selo(lado, estado) {
    var cls = estado === "CLAIMED" ? (lado === "superior" ? "selo fraco" : "selo") : "selo forte";
    return '<span class="' + cls + '">' + esc(t(lado)) + " · " + esc(estado || "?") + "</span>";
  }
  function cartaoDestaque(h) {
    var novo = POTENCIALMENTE_NOVO[chaveCelula(h.celula)];
    var antes = h.antes == null ? "" : String(h.antes), agora = h.agora == null ? "" : String(h.agora);
    var obs = [];
    if (novo) obs.push(t("naoAchado"));
    if (h.estado_ub === "CLAIMED") obs.push(t("ubClaimed"));
    if (h.estado_lb === "CLAIMED" && h.estado_ub !== "CLAIMED") obs.push(t("lbClaimed"));
    if (antes && antes === agora) obs.push(t("mesmo"));
    return '<li class="destaque' + (novo ? " novo" : "") + '">' +
      '<span class="celula">' + fmt(h.celula) + "</span>" +
      '<span class="antes-agora">' + (antes && antes !== agora ? '<span class="antes"><span class="sr">' + esc(t("antes")) + "</span>" + fmt(antes) +
        '</span><span class="seta" aria-hidden="true">→</span>' : "") +
      '<span class="agora"><span class="sr">' + esc(t("agora")) + "</span>" + fmt(agora) + "</span></span>" +
      '<span class="selos">' + (novo ? '<span class="tag-novo">' + esc(t("novo")) + "</span>" : "") +
      selo("inferior", h.estado_lb) + selo("superior", h.estado_ub) +
      (h.fonte ? link(h.fonte, h.fonte, "fonte") : "") + "</span>" +
      (obs.length ? '<span class="sr">' + esc(obs.join(" ")) + "</span>" : "") + "</li>";
  }

  function carregar(nome) {
    if (!window.fetch) return Promise.resolve(null);
    return fetch(nome, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(nome + ": HTTP " + r.status);
      return r.json();
    }).catch(function () { return null; }); // falta ou JSON quebrado: fica o texto embutido
  }
  function primeiro(nomes) {
    return nomes.reduce(function (p, nome) {
      return p.then(function (r) { return r || carregar(nome); });
    }, Promise.resolve(null));
  }

  /* ——— Cubo Q3 / Q4 interativo ——— */
  var cubo = { repintar: function () {} };
  function iniciarCubo() {
    var svg = $("#cubo-svg"), msg = $("#cubo-msg"), fig = $("#cubo");
    if (!svg || !msg) return;
    var NS = "http://www.w3.org/2000/svg";
    var estado = { n: 3, modo: "explorar", centros: [] };
    var SOLUCAO = { 3: [0, 7], 4: [0, 1, 14, 15] }; // 0000, 0001, 1110, 1111 cobrem Q4
    var MINIMO = { 3: 2, 4: 4 };                     // ⌈8/4⌉ = 2 e ⌈16/5⌉ = 4, atingidos acima
    var pos = [], nos = [], arestas = [];
    var dim = $("#dim");

    function bits(w) { var s = w.toString(2); while (s.length < estado.n) s = "0" + s; return s; }
    function vizinhos(w) { var v = []; for (var i = 0; i < estado.n; i++) v.push(w ^ (1 << i)); return v; }
    function esfera(w) { return [w].concat(vizinhos(w)); }
    function posicao(w) {
      var a = (w >> 2) & 1, b = (w >> 1) & 1, c = w & 1;
      if (estado.n === 3) return [70 + 190 * c + 90 * b, 300 - 200 * a - 70 * b];
      var d = (w >> 3) & 1, s = d ? 58 : 128;
      var A = 2 * a - 1, B = 2 * b - 1, C = 2 * c - 1;
      return [200 + s * (C + 0.42 * B), 180 - s * (A * 0.92 + 0.36 * B)];
    }
    function construir() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var N = 1 << estado.n, r = estado.n === 3 ? 23 : 19;
      pos = []; nos = []; arestas = [];
      for (var w = 0; w < N; w++) pos.push(posicao(w));
      var gA = document.createElementNS(NS, "g");
      gA.setAttribute("aria-hidden", "true");
      for (w = 0; w < N; w++) vizinhos(w).forEach(function (v) {
        if (v < w) return;
        var l = document.createElementNS(NS, "line");
        l.setAttribute("x1", pos[w][0]); l.setAttribute("y1", pos[w][1]);
        l.setAttribute("x2", pos[v][0]); l.setAttribute("y2", pos[v][1]);
        l.setAttribute("class", "aresta");
        l.dataset.a = w; l.dataset.b = v;
        gA.appendChild(l); arestas.push(l);
      });
      svg.appendChild(gA);
      for (w = 0; w < N; w++) (function (w) {
        var g = document.createElementNS(NS, "g");
        g.setAttribute("class", "no");
        g.setAttribute("tabindex", "0");
        g.setAttribute("role", "button");
        var c = document.createElementNS(NS, "circle");
        c.setAttribute("cx", pos[w][0]); c.setAttribute("cy", pos[w][1]); c.setAttribute("r", r);
        var tx = document.createElementNS(NS, "text");
        tx.setAttribute("x", pos[w][0]); tx.setAttribute("y", pos[w][1]);
        tx.textContent = bits(w);
        g.appendChild(c); g.appendChild(tx);
        g.addEventListener("click", function () { tocar(w); });
        g.addEventListener("keydown", function (ev) {
          if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); tocar(w); }
        });
        svg.appendChild(g); nos.push(g);
      })(w);
    }
    function pintar() {
      var N = 1 << estado.n, cob = {}, cent = {};
      estado.centros.forEach(function (w) { cent[w] = 1; esfera(w).forEach(function (v) { cob[v] = 1; }); });
      var tente = estado.modo === "tente";
      svg.setAttribute("aria-label", t("cuboAria", { n: estado.n, N: N }));
      if (dim) dim.setAttribute("aria-label", t(estado.n === 4 ? "paraQ3" : "paraQ4"));
      nos.forEach(function (g, w) {
        g.setAttribute("aria-label", t("palavra", { x: bits(w).split("").join(" ") }));
        g.classList.toggle("centro", !!cent[w]);
        g.classList.toggle("coberto", !!cob[w] && !cent[w]);
        g.classList.toggle("falta", tente && estado.centros.length > 0 && !cob[w]);
        if (tente) g.setAttribute("aria-pressed", String(!!cent[w])); else g.removeAttribute("aria-pressed");
      });
      arestas.forEach(function (l) { l.classList.toggle("on", !!(cent[l.dataset.a] || cent[l.dataset.b])); });
      var falta = N - Object.keys(cob).length, V = estado.n + 1, M = MINIMO[estado.n], k = estado.centros.length;
      var K = "K<sub>2</sub>(" + estado.n + ",1)";
      if (estado.modo === "explorar") {
        msg.innerHTML = !k ? t("expl0") : t("expl", { w: bits(estado.centros[0]), viz: vizinhos(estado.centros[0]).map(bits).join(", "), V: V, N: N });
      } else if (estado.modo === "solucao") {
        msg.innerHTML = t("sol", { lista: SOLUCAO[estado.n].map(bits).join(", "), N: N, K: K, M: M, V: V });
      } else if (!k) msg.innerHTML = t("tente0", { N: N });
      else if (falta > 0) msg.innerHTML = t("falta", { k: k, f: falta, N: N });
      else msg.innerHTML = t(k === M ? "minimo" : "menos", { k: k, K: K, M: M });
    }
    function marcarModo() {
      $$("[data-modo]", fig).forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.modo === estado.modo)); });
    }
    function tocar(w) {
      if (estado.modo === "solucao") { estado.modo = "explorar"; marcarModo(); }
      if (estado.modo === "explorar") estado.centros = [w];
      else {
        var i = estado.centros.indexOf(w);
        if (i >= 0) estado.centros.splice(i, 1); else estado.centros.push(w);
      }
      pintar();
    }
    $$("[data-modo]", fig).forEach(function (b) {
      b.addEventListener("click", function () {
        estado.modo = b.dataset.modo;
        estado.centros = estado.modo === "solucao" ? SOLUCAO[estado.n].slice() : [];
        marcarModo(); pintar();
      });
    });
    if (dim) dim.addEventListener("click", function () {
      estado.n = estado.n === 3 ? 4 : 3;
      dim.setAttribute("aria-pressed", String(estado.n === 4));
      estado.centros = estado.modo === "solucao" ? SOLUCAO[estado.n].slice() : [];
      construir(); pintar();
    });
    construir(); pintar();
    cubo.repintar = function () { marcarModo(); pintar(); };
  }

  /* ——— Prólogo: K7(6,4) inteiro, do caos à cobertura (WebGL puro, sem biblioteca) ———
     As 117 649 palavras de ℤ7^6 são pontos de verdade. Três estados, comandados pela rolagem:
       caos   → posições ao acaso, tremendo;
       espaço → a grade 49 × 49 × 49 (pares de coordenadas viram um eixo: c0 + 7·c1, …);
       cobertura → cada palavra vai para a esfera do centro mais próximo, numa camada pela distância (0 a 4).
     Os 14 centros são o código de data/codes/q7_n6_R4_M14.txt (o teste tests/test_pagina_matematica.py
     confere que a lista abaixo é a mesma do arquivo). A conferência roda no navegador do visitante. */
  var CODIGO_K764 = ["000000", "011111", "100011", "122200", "212222", "221122", "333333",
    "343444", "434455", "444366", "555534", "565643", "656665", "666556"];
  var conferencia = null; // {n, max, fora, ms}

  function conferirCobertura() {
    var t0 = performance.now(), C = CODIGO_K764.map(function (w) { return w.split("").map(Number); });
    var N = 117649, dist = new Uint8Array(N), dono = new Uint8Array(N), max = 0, fora = 0, d = [0, 0, 0, 0, 0, 0];
    for (var w = 0; w < N; w++) {
      var x = w;
      for (var k = 0; k < 6; k++) { d[k] = x % 7; x = (x / 7) | 0; }
      var melhor = 7, quem = 0;
      for (var c = 0; c < 14; c++) {
        var cc = C[c], h = 0;
        for (k = 0; k < 6; k++) if (cc[k] !== d[k]) h++;
        if (h < melhor) { melhor = h; quem = c; }
      }
      dist[w] = melhor; dono[w] = quem;
      if (melhor > max) max = melhor;
      if (melhor > 4) fora++;
    }
    conferencia = { n: N, max: max, fora: fora, ms: Math.max(1, Math.round(performance.now() - t0)) };
    return { dist: dist, dono: dono };
  }
  function renderConferencia() {
    var el = $("#verso-conferido");
    if (!el || !conferencia) return;
    el.innerHTML = conferencia.fora === 0
      ? t("conferido", { n: milhar(conferencia.n), ms: milhar(conferencia.ms) })
      : t("naoConferido", { f: milhar(conferencia.fora) });
  }

  var prologo = { progresso: function () {} };
  function iniciarPrologo() {
    var sec = $("#prologo"), palco = $(".palco", sec), cv = $("#colapso");
    if (!sec || !cv) return;
    var cobertura = conferirCobertura();
    renderConferencia();
    var versos = $$(".verso", sec);
    // Janela de cada verso na rolagem (0–1): centro e meia-largura. O último (a tese) fica até o fim.
    var JANELAS = [[0, 0.08], [0.15, 0.075], [0.29, 0.075], [0.43, 0.075], [0.57, 0.075], [0.72, 0.08], [0.93, 0.1]];
    var longo = !reduzir;
    if (longo) sec.classList.add("longo");

    var gl = null;
    try { gl = cv.getContext("webgl", { antialias: false, alpha: false, powerPreference: "high-performance" }); } catch (e) { gl = null; }
    var p = longo ? 0 : 1, alvoP = p, rodando = false, visivel = true, t0 = performance.now(), ultimo = 0;

    function lerProgresso() {
      if (!longo) return 1;
      var total = sec.offsetHeight - window.innerHeight;
      return Math.max(0, Math.min(1, (window.scrollY - sec.offsetTop) / Math.max(1, total)));
    }
    function suave(a, b, x) { x = Math.max(0, Math.min(1, (x - a) / (b - a))); return x * x * (3 - 2 * x); }
    function pintarVersos(pp) {
      if (!longo) return;
      versos.forEach(function (v, i) {
        var j = JANELAS[i], dd = Math.abs(pp - j[0]);
        var o = i === 0 ? 1 - suave(j[1] * 0.4, j[1], pp)
          : i === versos.length - 1 ? suave(j[0] - j[1], j[0] - j[1] * 0.35, pp)
          : 1 - suave(j[1] * 0.35, j[1], dd);
        v.style.opacity = o.toFixed(3);
        v.style.transform = "translate(-50%, calc(-50% + " + ((pp - j[0]) * -60).toFixed(1) + "px))";
      });
      sec.classList.toggle("andou", pp > 0.015);
      sec.classList.toggle("final", pp > 0.86);
    }

    if (!gl) { pintarVersos(p); if (longo) window.addEventListener("scroll", function () { pintarVersos(lerProgresso()); }, { passive: true }); return; }

    /* — Geometria — */
    var celular = Math.min(window.innerWidth, window.innerHeight) < 700 || (navigator.hardwareConcurrency || 8) <= 4;
    var passo = celular ? 4 : 1, N = 117649, M = Math.ceil(N / passo);
    var contagem = new Array(14).fill(0);
    for (var w = 0; w < N; w++) contagem[cobertura.dono[w]]++;
    // Esferas que se tocam: raio ∝ raiz cúbica do número de palavras; um relaxamento simples as encosta.
    var raio = contagem.map(function (n) { return 0.5 * Math.cbrt(n / 9000); });
    var cen = raio.map(function (r, i) {
      var a = i * 2.39996, z = 1 - 2 * (i + 0.5) / 14, s = Math.sqrt(1 - z * z);
      return [Math.cos(a) * s * 1.4, z * 1.4, Math.sin(a) * s * 1.4];
    });
    for (var it = 0; it < 400; it++) {
      for (var i = 0; i < 14; i++) {
        for (var j = i + 1; j < 14; j++) {
          var dx = cen[j][0] - cen[i][0], dy = cen[j][1] - cen[i][1], dz = cen[j][2] - cen[i][2];
          var dd = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-3, alvo = raio[i] + raio[j] + 0.015;
          if (dd < alvo) {
            var f = (alvo - dd) / dd * 0.5;
            cen[i][0] -= dx * f; cen[i][1] -= dy * f; cen[i][2] -= dz * f;
            cen[j][0] += dx * f; cen[j][1] += dy * f; cen[j][2] += dz * f;
          }
        }
        cen[i][0] *= 0.985; cen[i][1] *= 0.985; cen[i][2] *= 0.985; // gravidade: aproxima do centro
      }
    }
    var cm = [0, 0, 0];
    cen.forEach(function (c) { cm[0] += c[0] / 14; cm[1] += c[1] / 14; cm[2] += c[2] / 14; });
    cen.forEach(function (c) { c[0] -= cm[0]; c[1] -= cm[1]; c[2] -= cm[2]; }); // o aglomerado fica no centro da cena
    var CAMADA = [0, 0.38, 0.62, 0.83, 1.0];
    var dados = new Float32Array((M + 14) * 11), rnd = (function (n) { return function () { n = (n * 16807) % 2147483647; return (n - 1) / 2147483646; }; })(20261006);
    var o = 0;
    function escreve(c, g, b, info0, info1) {
      dados[o++] = c[0]; dados[o++] = c[1]; dados[o++] = c[2];
      dados[o++] = g[0]; dados[o++] = g[1]; dados[o++] = g[2];
      dados[o++] = b[0]; dados[o++] = b[1]; dados[o++] = b[2];
      dados[o++] = info0; dados[o++] = info1;
    }
    for (w = 0; w < N; w += passo) {
      var x = w, dg = [];
      for (var k = 0; k < 6; k++) { dg.push(x % 7); x = (x / 7) | 0; }
      var g = [(dg[0] + 7 * dg[1]) / 24 - 1, (dg[2] + 7 * dg[3]) / 24 - 1, (dg[4] + 7 * dg[5]) / 24 - 1];
      // Caos: uma nuvem grande e desigual; direção e raio ao acaso.
      var u = rnd() * 2 - 1, th = rnd() * 6.2832, rr = 1.1 + Math.pow(rnd(), 0.6) * 2.6, sq = Math.sqrt(1 - u * u);
      var c0 = [Math.cos(th) * sq * rr * 1.25, u * rr * 0.9, Math.sin(th) * sq * rr];
      var dono = cobertura.dono[w], dist = cobertura.dist[w];
      var u2 = rnd() * 2 - 1, th2 = rnd() * 6.2832, sq2 = Math.sqrt(1 - u2 * u2);
      var rb = raio[dono] * (CAMADA[dist] + (dist ? (rnd() - 0.5) * 0.06 : 0));
      var b = [cen[dono][0] + Math.cos(th2) * sq2 * rb, cen[dono][1] + u2 * rb, cen[dono][2] + Math.sin(th2) * sq2 * rb];
      escreve(c0, g, b, dist / 4, rnd());
    }
    for (i = 0; i < 14; i++) escreve(cen[i], [0, 0, 0], cen[i], -1, raio[i]); // halos dos centros

    /* — Shaders — */
    var VS = [
      "attribute vec3 aC, aG, aB; attribute vec2 aI;",
      "uniform mat4 uP, uV; uniform float uA, uBb, uT, uTr, uS, uH, uPx; uniform vec2 uOff;",
      "varying vec3 vCor; varying float vAlfa; varying float vHalo;",
      "void main(){",
      "  float halo = aI.x < 0. ? 1. : 0.;",
      "  vec3 tr = vec3(sin(uT*3.1+aI.y*91.), sin(uT*2.3+aI.y*57.), sin(uT*2.9+aI.y*23.)) * 0.035 * uTr;",
      "  vec3 lento = vec3(sin(uT*.21+aI.y*6.), cos(uT*.17+aI.y*9.), sin(uT*.13+aI.y*4.)) * 0.12 * (1.-uA);",
      "  vec3 p = mix(mix(aC + tr + lento, aG + tr*.25, uA), aB, uBb);",
      "  if (halo > .5) p = aB;",
      "  vec4 v = uV * vec4(p, 1.);",
      "  gl_Position = uP * v; gl_Position.xy += uOff * gl_Position.w;",
      "  float d = clamp(aI.x, 0., 1.);",
      "  float casca = mix(1., .55 + .45*d, uBb);",
      "  gl_PointSize = halo > .5 ? 1.7 * aI.y * uPx / -v.z : uS * (1.5 + (1.-uA)*.9 + uBb*(d < .01 ? 7. : 0.)) * 5.6 / -v.z;",
      "  vec3 marfim = vec3(.93,.89,.80), ouro = vec3(.95,.74,.38);",
      "  vCor = halo > .5 ? ouro : mix(marfim, mix(ouro, marfim, d*.7), uBb*.85);",
      "  float neblina = smoothstep(9., 2.5, -v.z);",
      "  vAlfa = halo > .5 ? uBb * uH * .22 : neblina * mix(mix(.62, .5, uA), .8 * casca, uBb);",
      "  vHalo = halo;",
      "}"].join("\n");
    var FS = [
      "precision mediump float; varying vec3 vCor; varying float vAlfa; varying float vHalo;",
      "void main(){",
      "  vec2 q = gl_PointCoord - .5; float r2 = dot(q,q) * 4.;",
      "  float a = vHalo > .5 ? exp(-r2 * 3.2) : exp(-r2 * 5.);",
      "  gl_FragColor = vec4(vCor * a * vAlfa, 1.);",
      "}"].join("\n");
    function sh(tipo, src) {
      var s = gl.createShader(tipo); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
      return s;
    }
    var prog;
    try {
      prog = gl.createProgram();
      gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
      gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    } catch (e) {
      if (window.console) console.warn("WebGL indisponível, fica a imagem estática:", e);
      pintarVersos(p); return;
    }
    gl.useProgram(prog);
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, dados, gl.STATIC_DRAW);
    [["aC", 3, 0], ["aG", 3, 3], ["aB", 3, 6], ["aI", 2, 9]].forEach(function (a) {
      var loc = gl.getAttribLocation(prog, a[0]);
      gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, a[1], gl.FLOAT, false, 44, a[2] * 4);
    });
    var U = {};
    ["uP", "uV", "uA", "uBb", "uT", "uTr", "uS", "uH", "uPx", "uOff"].forEach(function (n) { U[n] = gl.getUniformLocation(prog, n); });
    gl.disable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);

    var W = 0, H = 0, dpr = 1, mira = [0, 0], miraS = [0, 0];
    var posterLimpo = /[?&]poster\b/.test(location.search); // gera img/colapso.webp centrado (ver tests/)
    function medir() {
      dpr = Math.min(window.devicePixelRatio || 1, celular ? 1.5 : 1.75);
      W = cv.clientWidth; H = cv.clientHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      gl.viewport(0, 0, cv.width, cv.height);
    }
    function perspectiva(fov, asp, n, f) {
      var t2 = 1 / Math.tan(fov / 2), nf = 1 / (n - f);
      return [t2 / asp, 0, 0, 0, 0, t2, 0, 0, 0, 0, (f + n) * nf, -1, 0, 0, 2 * f * n * nf, 0];
    }
    function vista(ry, rx, dist) {
      var cy = Math.cos(ry), sy = Math.sin(ry), cx = Math.cos(rx), sx = Math.sin(rx);
      // R = Rx · Ry, depois translada −dist em z (colunas, como o WebGL espera)
      return [cy, sx * sy, -cx * sy, 0, 0, cx, sx, 0, sy, -sx * cy, cx * cy, 0, 0, 0, -dist, 1];
    }
    function quadro(agora) {
      var tt = (agora - t0) / 1000, dt = Math.min(0.05, (agora - (ultimo || agora)) / 1000);
      ultimo = agora;
      p += (alvoP - p) * Math.min(1, dt * 2.2); // a cena segue a rolagem devagar, sem pressa
      var a = suave(0.2, 0.42, p), b = suave(0.5, 0.72, p);
      var silencio = suave(0.78, 1, p);
      miraS[0] += (mira[0] - miraS[0]) * 0.03; miraS[1] += (mira[1] - miraS[1]) * 0.03;
      var asp = W / Math.max(1, H), dist = (asp < 0.8 ? 7.4 : 5.6) - b * 0.5 + silencio * (asp < 0.8 ? 1.6 : 1.1);
      gl.uniformMatrix4fv(U.uP, false, perspectiva(0.75, asp, 0.1, 40));
      gl.uniformMatrix4fv(U.uV, false, vista(tt * (0.05 - silencio * 0.035) + p * 1.4 + miraS[0] * 0.15, 0.32 + miraS[1] * 0.1, dist));
      gl.uniform1f(U.uA, a); gl.uniform1f(U.uBb, b); gl.uniform1f(U.uT, tt);
      gl.uniform1f(U.uTr, (1 - a) * 1.0 + (1 - silencio) * 0.08);
      gl.uniform1f(U.uS, dpr * (celular ? 1.25 : 1)); gl.uniform1f(U.uPx, cv.height / 2 / Math.tan(0.375)); gl.uniform1f(U.uH, 0.8 + 0.2 * Math.sin(tt * 0.6));
      // No silêncio final, a cobertura cede o lado esquerdo (no celular, o alto) para a tese.
      var desloca = posterLimpo ? 0 : silencio;
      gl.uniform2f(U.uOff, asp < 0.8 ? 0 : 0.52 * desloca, asp < 0.8 ? 0.36 * desloca : 0);
      gl.clearColor(0.051, 0.047, 0.039, 1); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.POINTS, 0, M + 14);
    }
    function laco(agora) {
      if (!rodando) return;
      alvoP = lerProgresso(); pintarVersos(alvoP);
      quadro(agora);
      requestAnimationFrame(laco);
    }
    function ligar() {
      var deve = visivel && !document.hidden && !reduzir;
      if (deve && !rodando) { rodando = true; ultimo = 0; requestAnimationFrame(laco); }
      if (!deve) rodando = false;
    }
    medir();
    palco.classList.add("webgl");
    if (reduzir) { p = alvoP = 1; quadro(performance.now()); }
    else ligar();
    pintarVersos(p);
    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(function () { medir(); if (!rodando) quadro(performance.now()); }, 120);
    });
    window.addEventListener("pointermove", function (e) {
      mira[0] = e.clientX / window.innerWidth - 0.5; mira[1] = e.clientY / window.innerHeight - 0.5;
    }, { passive: true });
    document.addEventListener("visibilitychange", ligar);
    if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { visivel = es[0].isIntersecting; ligar(); }).observe(sec);
    cv.addEventListener("webglcontextlost", function (e) { e.preventDefault(); rodando = false; palco.classList.remove("webgl"); });
    prologo.irPara = function (pp) { alvoP = p = pp; pintarVersos(pp); quadro(performance.now()); };
  }

  /* ——— Copiar citação ——— */
  function iniciarCopiar() {
    var b = $("#copiar"), pre = $("#bibtex");
    if (!b || !pre) return;
    if (!navigator.clipboard) { b.hidden = true; return; }
    b.addEventListener("click", function () {
      navigator.clipboard.writeText(pre.textContent).then(function () {
        b.textContent = t("copiado"); setTimeout(function () { b.textContent = UI[idioma] ? UI[idioma].copiar : "Copiar"; }, 1800);
      }, function () { b.textContent = t("copieMao"); });
    });
  }

  /* ——— Montagem ——— */
  S.pt.analogia = "Analogia"; S.en.analogia = "Analogy"; S.fr.analogia = "Analogie";
  S.pt.exemplo = "Exemplo"; S.en.exemplo = "Example"; S.fr.exemplo = "Exemple";
  var exemplo = /[?&]exemplo\b/.test(location.search);
  var cacheConteudo = {}, dadosP = null, vez = 0;
  function conteudoDe(l) {
    if (!cacheConteudo[l]) {
      var pre = exemplo ? "conteudo.exemplo" : "conteudo";
      // conteudo.json é o português; qualquer idioma sem arquivo próprio cai nele.
      cacheConteudo[l] = primeiro([pre + "." + l + ".json", pre + ".json"]);
    }
    return cacheConteudo[l];
  }
  function definirIdioma(l, doUsuario) {
    idioma = IDIOMAS.indexOf(l) >= 0 ? l : "pt";
    var minha = ++vez;
    if (doUsuario) {
      try { localStorage.setItem("mat-idioma", idioma); } catch (e) { /* segue sem lembrar */ }
      try {
        var u = new URL(location.href);
        u.searchParams.set("lang", idioma);
        history.replaceState(null, "", u.pathname + u.search + u.hash);
      } catch (e) { /* URL antiga: tudo bem */ }
    }
    aplicarDicionario(); renderConferencia(); iniciarNiveis(); cubo.repintar();
    return Promise.all([conteudoDe(idioma), dadosP]).then(function (r) {
      if (minha !== vez) return; // o visitante já trocou de novo
      aplicarDicionario(); renderConferencia();
      try { renderConteudo(r[0]); } catch (e) { if (window.console) console.warn("conteudo ignorado:", e); }
      iniciarNiveis();
      try { renderDados(r[1] || DADOS_EMBUTIDOS, !r[1]); } catch (e) { renderDados(DADOS_EMBUTIDOS, true); }
      cubo.repintar();
      document.documentElement.dataset.fontes = (r[0] ? "c" : "") + (r[1] ? "d" : "");
    });
  }
  function iniciar() {
    try { nivelAtual = Number(localStorage.getItem("mat-nivel")) || 0; } catch (e) { nivelAtual = 0; }
    guardarOriginais();
    iniciarTema(); iniciarCabecalho(); iniciarCubo(); iniciarCopiar();
    try { iniciarPrologo(); } catch (e) { if (window.console) console.warn("prólogo:", e); }
    dadosP = carregar(exemplo ? "dados.exemplo.json" : "dados.json");
    $$("[data-lang]").forEach(function (b) { b.addEventListener("click", function () { definirIdioma(b.dataset.lang, true); }); });
    definirIdioma(idiomaInicial(), false).then(iniciarSurge);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar); else iniciar();
})();
