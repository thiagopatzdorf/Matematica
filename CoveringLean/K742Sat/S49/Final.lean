import CoveringLean.K742Sat.S49.B0
import CoveringLean.LratKFinal
import CoveringLean.K742_Cnf

/-! K_7(4,2), M = 18, perfil 49 (`5322222 | 3333222 | 4422222 | 6222222`), CNF sem a quebra (d)–(f).
Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`
(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/

namespace K742Sat

lratk_final_seg s49 "../dados/s0049"
  for K742Cnf.cnfSemQuebra 7 18 [[5,3,2,2,2,2,2], [3,3,3,3,2,2,2], [4,4,2,2,2,2,2], [6,2,2,2,2,2,2]]

end K742Sat

#print axioms K742Sat.s49.unsatFor
