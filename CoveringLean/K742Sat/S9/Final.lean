import CoveringLean.K742Sat.S9.B0
import CoveringLean.K742Sat.S9.B1
import CoveringLean.K742Sat.S9.B2
import CoveringLean.K742Sat.S9.B3
import CoveringLean.K742Sat.S9.B4
import CoveringLean.K742Sat.S9.B5
import CoveringLean.K742Sat.S9.B6
import CoveringLean.K742Sat.S9.B7
import CoveringLean.K742Sat.S9.B8
import CoveringLean.K742Sat.S9.B9
import CoveringLean.LratKFinal
import CoveringLean.K742_Cnf

/-! K_7(4,2), M = 18, perfil 9 (`4332222 | 4332222 | 3333222 | 3333222`), CNF sem a quebra (d)–(f).
Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`
(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/

namespace K742Sat

lratk_final_seg s9 "../dados/s0009"
  for K742Cnf.cnfSemQuebra 7 18 [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]]

end K742Sat

#print axioms K742Sat.s9.unsatFor
