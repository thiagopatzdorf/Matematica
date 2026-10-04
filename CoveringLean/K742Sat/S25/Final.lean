import CoveringLean.K742Sat.S25.B0
import CoveringLean.K742Sat.S25.B1
import CoveringLean.K742Sat.S25.B2
import CoveringLean.K742Sat.S25.B3
import CoveringLean.K742Sat.S25.B4
import CoveringLean.K742Sat.S25.B5
import CoveringLean.K742Sat.S25.B6
import CoveringLean.K742Sat.S25.B7
import CoveringLean.K742Sat.S25.B8
import CoveringLean.K742Sat.S25.B9
import CoveringLean.K742Sat.S25.B10
import CoveringLean.K742Sat.S25.B11
import CoveringLean.K742Sat.S25.B12
import CoveringLean.K742Sat.S25.B13
import CoveringLean.K742Sat.S25.B14
import CoveringLean.LratKFinal
import CoveringLean.K742_Cnf

/-! K_7(4,2), M = 18, perfil 25 (`4332222 | 3333222 | 3333222 | 3333222`), CNF sem a quebra (d)–(f).
Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`
(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/

namespace K742Sat

lratk_final_seg s25 "../dados/s0025"
  for K742Cnf.cnfSemQuebra 7 18 [[4,3,3,2,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]]

end K742Sat

#print axioms K742Sat.s25.unsatFor
