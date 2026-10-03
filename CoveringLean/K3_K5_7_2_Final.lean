import CoveringLean.K3_K5_7_2
import CoveringLean.K3_Bridge

/-!
# K_5(7,2) ≤ 500, kernel tier (frente 1b)

The code is `CoveringCerts.Data.K5_7_2` (C1_Data_K5_7_2.lean; canonical sha256 in its header).
`K5_7_2_q : go 5 7 (wordItems 2 CoveringCerts.Data.K5_7_2) = true` is assembled in `K3_K5_7_2.lean` from
25 leaf theorems (`decide +kernel`) in the part files `K3_K5_7_2_P*.lean`.
-/

namespace CoveringKernel

theorem K5_7_2_le_500_kernel :
    ∃ C : Finset (Fin 7 → ZMod 5), C.card = 500 ∧ CoveringA2.Covers 2 C :=
  cert_of_go (L := CoveringCerts.Data.K5_7_2) (by decide +kernel) (by decide +kernel) K5_7_2_q

end CoveringKernel

#print axioms CoveringKernel.K5_7_2_le_500_kernel
