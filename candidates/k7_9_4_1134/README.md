# Candidato K_7(9,4) ≤ 1134 (NÃO publicado, NÃO certificado em Lean ainda)

- Código: as 1029 palavras das 3 classes laterais da base campeã (as mesmas do 1137) mais um remendo de
  105 palavras, achado pelo ILP com simetria imposta (`ilp_sym.py 18 line 10 600`): o remendo é invariante
  por translação pela reta 10 de C0 (15 órbitas de 7). `precompute.py` gera as entradas do ILP.
- Conferido: verificador A (força bruta), B (união de bolas), C (BFS) e redundância individual, todos PASS;
  distribuição N_0..N_4 = 1134 / 61040 / 1417073 / 15311828 / 23562532; 0 palavras redundantes.
- Falta: certificado Lean, red team e revisão bibliográfica atualizada. Até lá, é candidato.
