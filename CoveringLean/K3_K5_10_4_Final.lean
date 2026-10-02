import CoveringLean.K3_K5_10_4
import CoveringLean.K3_Bridge

/-!
# K_5(10,4) ≤ 625, kernel tier (frente 1b)

The code is `CoveringCerts.Data.K5_10_4` (C1_Data_K5_10_4.lean; canonical sha256 in its header).
`K5_10_4_q : go 5 10 (wordItems 4 CoveringCerts.Data.K5_10_4) = true` is assembled in `K3_K5_10_4.lean` from
625 leaf theorems (`decide +kernel`) in the part files `K3_K5_10_4_P*.lean`.
-/

namespace CoveringKernel

theorem K5_10_4_le_625_kernel :
    ∃ C : Finset (Fin 10 → ZMod 5), C.card = 625 ∧ CoveringA2.Covers 4 C :=
  cert_of_go (L := CoveringCerts.Data.K5_10_4) (by decide +kernel) (by decide +kernel) K5_10_4_q

end CoveringKernel

#print axioms CoveringKernel.K5_10_4_le_625_kernel
