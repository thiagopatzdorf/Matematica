# Candidato K_7(9,4) ≤ 1134 (NÃO publicado)

- Código: as 1029 palavras das 3 classes laterais da base campeã (as mesmas do 1137) mais um remendo de
  105 palavras, achado pelo ILP com simetria imposta (`ilp_sym.py 18 line 10 600`): o remendo é invariante
  por translação pela reta 10 de C0 (15 órbitas de 7). `precompute.py` gera as entradas do ILP.
- Conferido: verificador A (força bruta), B (união de bolas), C (BFS) e redundância individual, todos PASS;
  distribuição N_0..N_4 = 1134 / 61040 / 1417073 / 15311828 / 23562532; 0 palavras redundantes.
- Lean: `Syn.K7_9_4_le_1134_syn : ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1134 ∧ CoveringA2.Covers 4 C`,
  `lake build CoveringLean.Syn_K1134` com exit 0 (2026-10-03), axiomas [propext, Classical.choice, Quot.sound],
  sem `sorry`/`native_decide`. Gerado por `scripts/syndrome/gen_syn.py data/structured/q7_n9_R4_M1134.json K1134`.
- Falta: red team do Lean, mutações e revisão bibliográfica atualizada (a de 2026-10-02 vale: menor anterior 1475).
