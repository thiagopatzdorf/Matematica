import CoveringLean.K3_K7_8_3
import CoveringLean.K3_Bridge

/-!
# K_7(8,3) ≤ 1893, kernel tier

The code is `CoveringCerts.Data.K7_8_3` (C1_Data_K7_8_3.lean; canonical sha256 in its header:
7c276cf1fffe7e43da8d21fa24ebf2ec91d413fb5c8c5d08bc3ee9b8aeeb93b1).
`K7_8_3_q : go 7 8 (wordItems 3 Data.K7_8_3) = true` is assembled in `K3_K7_8_3.lean` from
343 leaf theorems (`decide +kernel`) in the part files `K3_K7_8_3_P*.lean`.
-/

namespace CoveringKernel

theorem K7_8_3_le_1893_kernel :
    ∃ C : Finset (Fin 8 → ZMod 7), C.card = 1893 ∧ CoveringA2.Covers 3 C :=
  cert_of_go (L := CoveringCerts.Data.K7_8_3) (by decide +kernel) (by decide +kernel) K7_8_3_q

end CoveringKernel

#print axioms CoveringKernel.K7_8_3_le_1893_kernel
