import CoveringLean.K742Sat.S55.B0
import CoveringLean.K742Sat.S55.B1
import CoveringLean.K742Sat.S55.B2
import CoveringLean.K742Sat.S55.B3
import CoveringLean.K742Sat.S55.B4
import CoveringLean.K742Sat.S55.B5
import CoveringLean.K742Sat.S55.B6
import CoveringLean.K742Sat.S55.B7
import CoveringLean.K742Sat.S55.B8
import CoveringLean.K742Sat.S55.B9
import CoveringLean.K742Sat.S55.B10
import CoveringLean.K742Sat.S55.B11
import CoveringLean.K742Sat.S55.B12
import CoveringLean.K742Sat.S55.B13
import CoveringLean.K742Sat.S55.B14
import CoveringLean.K742Sat.S55.B15
import CoveringLean.K742Sat.S55.B16
import CoveringLean.K742Sat.S55.B17
import CoveringLean.K742Sat.S55.B18
import CoveringLean.K742Sat.S55.B19
import CoveringLean.LratKFinal
import CoveringLean.K742_Cnf

/-! K_7(4,2), M = 18, perfil 55 (`3333222 | 3333222 | 3333222 | 3333222`), CNF sem a quebra (d)–(f).
Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`
(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/

namespace K742Sat

lratk_final_seg s55 "../dados/s0055"
  for K742Cnf.cnfSemQuebra 7 18 [[3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2], [3,3,3,3,2,2,2]]

end K742Sat

#print axioms K742Sat.s55.unsatFor
