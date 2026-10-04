import CoveringLean.LratKData
import CoveringLean.K742_Cnf

/-!
# Teste de ponta a ponta de `LratK`: as 5 CNFs de K_4(4,2), M = 6

Os 5 perfis de `encode.py --q 4 --M 6` (validação da fase 0: K_4(4,2) = 7). Cada CNF é a do
gerador `K742Cnf.cnf` (conferida, no kernel, contra o DIMACS do Python) e cada refutação LRAT
aparada é conferida pelo kernel com `LratK`. Os dados ficam em `LratK_K4/`, gerados por
`tools/exatos/k742/lean/gerar_dados.py --q 4 --M 6 --perfil i` (sha256 em
`tools/exatos/k742/lean/manifesto.json`). Leve o bastante para o alvo padrão (~2 min).
-/

namespace LratK_K4

lratk_refute p0 "LratK_K4/K4_4_2_M6_p0000.cnf" "LratK_K4/K4_4_2_M6_p0000.lrat" 200
  for K742Cnf.cnf 4 6 [[2,2,1,1], [2,2,1,1], [2,2,1,1], [2,2,1,1]]
lratk_refute p1 "LratK_K4/K4_4_2_M6_p0001.cnf" "LratK_K4/K4_4_2_M6_p0001.lrat" 200
  for K742Cnf.cnf 4 6 [[2,2,1,1], [2,2,1,1], [2,2,1,1], [3,1,1,1]]
lratk_refute p2 "LratK_K4/K4_4_2_M6_p0002.cnf" "LratK_K4/K4_4_2_M6_p0002.lrat" 200
  for K742Cnf.cnf 4 6 [[2,2,1,1], [2,2,1,1], [3,1,1,1], [3,1,1,1]]
lratk_refute p3 "LratK_K4/K4_4_2_M6_p0003.cnf" "LratK_K4/K4_4_2_M6_p0003.lrat" 200
  for K742Cnf.cnf 4 6 [[2,2,1,1], [3,1,1,1], [3,1,1,1], [3,1,1,1]]
lratk_refute p4 "LratK_K4/K4_4_2_M6_p0004.cnf" "LratK_K4/K4_4_2_M6_p0004.lrat" 200
  for K742Cnf.cnf 4 6 [[3,1,1,1], [3,1,1,1], [3,1,1,1], [3,1,1,1]]

/-- Os 5 perfis de `M = 6` para `q = 4`, na ordem de `encode.py --q 4 --M 6 --listar`. -/
def perfis6 : List (List (List Nat)) :=
  [[[2,2,1,1], [2,2,1,1], [2,2,1,1], [2,2,1,1]],
   [[2,2,1,1], [2,2,1,1], [2,2,1,1], [3,1,1,1]],
   [[2,2,1,1], [2,2,1,1], [3,1,1,1], [3,1,1,1]],
   [[2,2,1,1], [3,1,1,1], [3,1,1,1], [3,1,1,1]],
   [[3,1,1,1], [3,1,1,1], [3,1,1,1], [3,1,1,1]]]

/-- As 5 CNFs de `K_4(4,2)`, `M = 6`, são insatisfatíveis (conferido pelo kernel). -/
theorem refut6 : ∀ t ∈ perfis6, LratK.Unsat (K742Cnf.cnf 4 6 t) := by
  intro t ht
  simp only [perfis6, List.mem_cons, List.not_mem_nil, or_false] at ht
  rcases ht with rfl | rfl | rfl | rfl | rfl
  · exact p0.unsatFor
  · exact p1.unsatFor
  · exact p2.unsatFor
  · exact p3.unsatFor
  · exact p4.unsatFor

end LratK_K4

#print axioms LratK_K4.refut6
