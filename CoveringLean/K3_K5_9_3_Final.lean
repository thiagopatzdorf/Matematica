import CoveringLean.K3_K5_9_3
import CoveringLean.K3_Bridge

/-!
# K_5(9,3) ≤ 1250, kernel tier (frente 1b)

The code is `CoveringCerts.Data.K5_9_3` (C1_Data_K5_9_3.lean; canonical sha256 in its header).
`K5_9_3_q : go 5 9 (wordItems 3 CoveringCerts.Data.K5_9_3) = true` is assembled in `K3_K5_9_3.lean` from
625 leaf theorems (`decide +kernel`) in the part files `K3_K5_9_3_P*.lean`.
-/

namespace CoveringKernel

theorem K5_9_3_le_1250_kernel :
    ∃ C : Finset (Fin 9 → ZMod 5), C.card = 1250 ∧ CoveringA2.Covers 3 C :=
  cert_of_go (L := CoveringCerts.Data.K5_9_3) (by decide +kernel) (by decide +kernel) K5_9_3_q

end CoveringKernel

#print axioms CoveringKernel.K5_9_3_le_1250_kernel
