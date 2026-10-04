import CoveringLean.K742Sat.S2.B0
import CoveringLean.K742Sat.S2.B1
import CoveringLean.K742Sat.S2.B2
import CoveringLean.K742Sat.S2.B3
import CoveringLean.K742Sat.S2.B4
import CoveringLean.K742Sat.S2.B5
import CoveringLean.K742Sat.S2.B6
import CoveringLean.K742Sat.S2.B7
import CoveringLean.LratKFinal
import CoveringLean.K742_Cnf

/-! K_7(4,2), M = 18, perfil 2 (`4332222 | 4332222 | 4332222 | 3333222`), CNF sem a quebra (d)–(f).
Gerado por `tools/exatos/k742/lean/gerar_modulos.py`; dados por `preparar_semquebra.py`
(sha256 em `tools/exatos/k742/lean/semquebra_M18.jsonl`). -/

namespace K742Sat

lratk_final_seg s2 "../dados/s0002"
  for K742Cnf.cnfSemQuebra 7 18 [[4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [4,3,3,2,2,2,2], [3,3,3,3,2,2,2]]

end K742Sat

#print axioms K742Sat.s2.unsatFor
