import CoveringLean.G610_Top
import CoveringLean.SearchBridgeA2

/-!
# K_2(6,1) = 12, incondicional

`G610_Top` refuta `root 6 10` (centro 63 + 10 centros) com a fronteira de profundidade 2
(38 estados, DFS); cada estado é refutado num `G610_Chunk_k`.  Com `code12` (A6c_Search) dá o
valor exato.  Gerado por `gen_demo.py 6 10 2 … G610`.
-/

open CoveringA6

theorem SC.K_2_6_1_ge12 : ∀ C : Finset (W 2 6), C.card < 12 → ¬ Covers 1 C :=
  SC.K_2_6_1_ge12_of G610.ref

theorem SC.K_2_6_1_eq12 : IsK 2 6 1 12 := SC.K_2_6_1_eq12_of G610.ref

theorem SC.K_2_6_1_ge12_A2 :
    ∀ C : Finset (Fin 6 → ZMod 2), C.card < 12 → ¬ CoveringA2.Covers 1 C :=
  SC.K_2_6_1_ge12_A2_of G610.ref

#print axioms SC.K_2_6_1_ge12
#print axioms SC.K_2_6_1_eq12
#print axioms SC.K_2_6_1_ge12_A2
