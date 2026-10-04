import CoveringLean.K742Sat.S35.B0
import CoveringLean.LratKFinal
import CoveringLean.K742_Cnf

/-! K_7(4,2), M = 18, perfil 35 (`5322222 | 5322222 | 5322222 | 5322222`), CNF sem a quebra (d)–(f).
Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`
(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/

namespace K742Sat

lratk_final_seg s35 "../dados/s0035"
  for K742Cnf.cnfSemQuebra 7 18 [[5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2], [5,3,2,2,2,2,2]]

end K742Sat

#print axioms K742Sat.s35.unsatFor
