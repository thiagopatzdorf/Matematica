import CoveringLean.K3_K4_10_4
import CoveringLean.K3_Bridge

/-!
# K_4(10,4) ≤ 192, kernel tier (frente 1b)

The code is `CoveringCerts.Data.K4_10_4` (C1_Data_K4_10_4.lean; canonical sha256 in its header).
`K4_10_4_q : go 4 10 (wordItems 4 CoveringCerts.Data.K4_10_4) = true` is assembled in `K3_K4_10_4.lean` from
64 leaf theorems (`decide +kernel`) in the part files `K3_K4_10_4_P*.lean`.
-/

namespace CoveringKernel

theorem K4_10_4_le_192_kernel :
    ∃ C : Finset (Fin 10 → ZMod 4), C.card = 192 ∧ CoveringA2.Covers 4 C :=
  cert_of_go (L := CoveringCerts.Data.K4_10_4) (by decide +kernel) (by decide +kernel) K4_10_4_q

end CoveringKernel

#print axioms CoveringKernel.K4_10_4_le_192_kernel
