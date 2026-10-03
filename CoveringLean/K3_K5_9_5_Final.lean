import CoveringLean.K3_K5_9_5
import CoveringLean.K3_Bridge

/-!
# K_5(9,5) ≤ 50, kernel tier (frente 1b)

The code is `CoveringCerts.Data.K5_9_5` (C1_Data_K5_9_5.lean; canonical sha256 in its header).
`K5_9_5_q : go 5 9 (wordItems 5 CoveringCerts.Data.K5_9_5) = true` is assembled in `K3_K5_9_5.lean` from
25 leaf theorems (`decide +kernel`) in the part files `K3_K5_9_5_P*.lean`.
-/

namespace CoveringKernel

theorem K5_9_5_le_50_kernel :
    ∃ C : Finset (Fin 9 → ZMod 5), C.card = 50 ∧ CoveringA2.Covers 5 C :=
  cert_of_go (L := CoveringCerts.Data.K5_9_5) (by decide +kernel) (by decide +kernel) K5_9_5_q

end CoveringKernel

#print axioms CoveringKernel.K5_9_5_le_50_kernel
