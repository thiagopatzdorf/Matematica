import CoveringLean.LratKData
import CoveringLean.K742_Cnf

/-!
# K_7(4,2), M = 18: o perfil 64 refutado no kernel

O perfil 64 (`3333222 | 6222222 | 6222222 | 6222222`) é o de menor prova LRAT entre os 70
(10,3 MB; 4,76 MB depois de `lrat-trim` e sem deleções; 17 797 passos; 595 825 dicas).
Medidas em `docs/exatos/LEAN_K742.md`.

Dados fora do git (determinísticos; sha256 em `tools/exatos/k742/lean/manifesto.json`):

    python3 tools/exatos/k742/lean/gerar_dados.py --q 7 --M 18 --perfil 64 \
        --saida CoveringLean/K742Sat/dados
    lake build CoveringK742Sat
-/

namespace K742Sat

lratk_refute m18p64 "dados/K7_4_2_M18_p0064.cnf" "dados/K7_4_2_M18_p0064.lrat" 400
  for K742Cnf.cnf 7 18 [[3,3,3,3,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]]

theorem perfis18_64 :
    K742.perfis18[64]? = some [[3,3,3,3,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]] := by
  decide

/-- O perfil 64 de `perfis18` é insatisfatível: 1 dos 70 casos de `K742.Refut18`. -/
theorem refut18_p64 : LratK.Unsat (K742Cnf.cnf 7 18 ((K742.perfis18[64]?).getD [])) := by
  rw [perfis18_64]
  exact m18p64.unsatFor

end K742Sat

#print axioms K742Sat.refut18_p64
