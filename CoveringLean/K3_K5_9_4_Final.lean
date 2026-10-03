import CoveringLean.K3_K5_9_4
import CoveringLean.K3_Bridge

/-!
# K_5(9,4) ≤ 250, kernel tier (frente 1b)

The code is `CoveringCerts.Data.K5_9_4` (C1_Data_K5_9_4.lean; canonical sha256 in its header).
`K5_9_4_q : go 5 9 (wordItems 4 CoveringCerts.Data.K5_9_4) = true` is assembled in `K3_K5_9_4.lean` from
125 leaf theorems (`decide +kernel`) in the part files `K3_K5_9_4_P*.lean`.
-/

namespace CoveringKernel

theorem K5_9_4_le_250_kernel :
    ∃ C : Finset (Fin 9 → ZMod 5), C.card = 250 ∧ CoveringA2.Covers 4 C :=
  cert_of_go (L := CoveringCerts.Data.K5_9_4) (by decide +kernel) (by decide +kernel) K5_9_4_q

end CoveringKernel

#print axioms CoveringKernel.K5_9_4_le_250_kernel
