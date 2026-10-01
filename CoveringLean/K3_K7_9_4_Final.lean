import CoveringLean.K3_K7_9_4
import CoveringLean.K3_Bridge

/-!
# K_7(9,4) ≤ 1351, kernel tier

The code is `CoveringCerts.Data.K7_9_4` (C1_Data_K7_9_4.lean; canonical sha256 in its header).
`K7_9_4_q : go 7 9 (wordItems 4 Data.K7_9_4) = true` is assembled in `K3_K7_9_4.lean` from
2401 leaf theorems (`decide +kernel`) in the part files `K3_K7_9_4_P*.lean`.
-/

namespace CoveringKernel

theorem K7_9_4_le_1351_kernel :
    ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1351 ∧ CoveringA2.Covers 4 C :=
  cert_of_go (L := CoveringCerts.Data.K7_9_4) (by decide +kernel) (by decide +kernel) K7_9_4_q

end CoveringKernel

#print axioms CoveringKernel.K7_9_4_le_1351_kernel
