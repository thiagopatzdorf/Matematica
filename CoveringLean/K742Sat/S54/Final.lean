import CoveringLean.K742Sat.S54.B0
import CoveringLean.K742Sat.S54.B1
import CoveringLean.LratKFinal
import CoveringLean.K742_Cnf

/-! K_7(4,2), M = 18, perfil 54 (`5322222 | 6222222 | 6222222 | 6222222`), CNF sem a quebra (d)–(f).
Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`
(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/

namespace K742Sat

lratk_final_seg s54 "../dados/s0054"
  for K742Cnf.cnfSemQuebra 7 18 [[5,3,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2], [6,2,2,2,2,2,2]]

end K742Sat

#print axioms K742Sat.s54.unsatFor
