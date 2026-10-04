import CoveringLean.K742Sat.S0.Final
import CoveringLean.K742Sat.S1.Final
import CoveringLean.K742Sat.S2.Final
import CoveringLean.K742Sat.S3.Final
import CoveringLean.K742Sat.S4.Final
import CoveringLean.K742Sat.S5.Final
import CoveringLean.K742Sat.S6.Final
import CoveringLean.K742Sat.S7.Final
import CoveringLean.K742Sat.S8.Final
import CoveringLean.K742Sat.S9.Final
import CoveringLean.K742Sat.S10.Final
import CoveringLean.K742Sat.S11.Final
import CoveringLean.K742Sat.S12.Final
import CoveringLean.K742Sat.S13.Final
import CoveringLean.K742Sat.S14.Final
import CoveringLean.K742Sat.S15.Final
import CoveringLean.K742Sat.S16.Final
import CoveringLean.K742Sat.S17.Final
import CoveringLean.K742Sat.S18.Final
import CoveringLean.K742Sat.S19.Final
import CoveringLean.K742Sat.S20.Final
import CoveringLean.K742Sat.S21.Final
import CoveringLean.K742Sat.S22.Final
import CoveringLean.K742Sat.S23.Final
import CoveringLean.K742Sat.S24.Final
import CoveringLean.K742Sat.S25.Final
import CoveringLean.K742Sat.S26.Final
import CoveringLean.K742Sat.S27.Final
import CoveringLean.K742Sat.S28.Final
import CoveringLean.K742Sat.S29.Final
import CoveringLean.K742Sat.S30.Final
import CoveringLean.K742Sat.S31.Final
import CoveringLean.K742Sat.S32.Final
import CoveringLean.K742Sat.S33.Final
import CoveringLean.K742Sat.S34.Final
import CoveringLean.K742Sat.S35.Final
import CoveringLean.K742Sat.S36.Final
import CoveringLean.K742Sat.S37.Final
import CoveringLean.K742Sat.S38.Final
import CoveringLean.K742Sat.S39.Final
import CoveringLean.K742Sat.S40.Final
import CoveringLean.K742Sat.S41.Final
import CoveringLean.K742Sat.S42.Final
import CoveringLean.K742Sat.S43.Final
import CoveringLean.K742Sat.S44.Final
import CoveringLean.K742Sat.S45.Final
import CoveringLean.K742Sat.S46.Final
import CoveringLean.K742Sat.S47.Final
import CoveringLean.K742Sat.S48.Final
import CoveringLean.K742Sat.S49.Final
import CoveringLean.K742Sat.S50.Final
import CoveringLean.K742Sat.S51.Final
import CoveringLean.K742Sat.S52.Final
import CoveringLean.K742Sat.S53.Final
import CoveringLean.K742Sat.S54.Final
import CoveringLean.K742Sat.S55.Final
import CoveringLean.K742Sat.S56.Final
import CoveringLean.K742Sat.S57.Final
import CoveringLean.K742Sat.S58.Final
import CoveringLean.K742Sat.S59.Final
import CoveringLean.K742Sat.S60.Final
import CoveringLean.K742Sat.S61.Final
import CoveringLean.K742Sat.S62.Final
import CoveringLean.K742Sat.S63.Final
import CoveringLean.K742Sat.S64.Final
import CoveringLean.K742Sat.S65.Final
import CoveringLean.K742Sat.S66.Final
import CoveringLean.K742Sat.S67.Final
import CoveringLean.K742Sat.S68.Final
import CoveringLean.K742Sat.S69.Final
import CoveringLean.K742_Final

/-!
# `Refut18` para a CNF sem quebra: as 70 refutações, no kernel

Cada `K742Sat.s<p>.unsatFor : LratK.Unsat (K742Cnf.cnfSemQuebra 7 18 t_p)` vem de um verificador
LRAT provado correto (`LratK`), executado pelo kernel. Gerado por
`tools/exatos/k742/lean/gerar_modulos.py`.
-/

namespace K742Sat

set_option maxRecDepth 100000 in
/-- **As 70 CNFs sem quebra de `M = 18` são insatisfatíveis.** -/
theorem refut18 : K742.Refut18 (K742Cnf.cnfSemQuebra 7 18) := by
  intro t ht
  simp only [K742.perfis18, List.mem_cons, List.not_mem_nil, or_false] at ht
  rcases ht with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact K742Sat.s0.unsatFor
  · exact K742Sat.s1.unsatFor
  · exact K742Sat.s2.unsatFor
  · exact K742Sat.s3.unsatFor
  · exact K742Sat.s4.unsatFor
  · exact K742Sat.s5.unsatFor
  · exact K742Sat.s6.unsatFor
  · exact K742Sat.s7.unsatFor
  · exact K742Sat.s8.unsatFor
  · exact K742Sat.s9.unsatFor
  · exact K742Sat.s10.unsatFor
  · exact K742Sat.s11.unsatFor
  · exact K742Sat.s12.unsatFor
  · exact K742Sat.s13.unsatFor
  · exact K742Sat.s14.unsatFor
  · exact K742Sat.s15.unsatFor
  · exact K742Sat.s16.unsatFor
  · exact K742Sat.s17.unsatFor
  · exact K742Sat.s18.unsatFor
  · exact K742Sat.s19.unsatFor
  · exact K742Sat.s20.unsatFor
  · exact K742Sat.s21.unsatFor
  · exact K742Sat.s22.unsatFor
  · exact K742Sat.s23.unsatFor
  · exact K742Sat.s24.unsatFor
  · exact K742Sat.s25.unsatFor
  · exact K742Sat.s26.unsatFor
  · exact K742Sat.s27.unsatFor
  · exact K742Sat.s28.unsatFor
  · exact K742Sat.s29.unsatFor
  · exact K742Sat.s30.unsatFor
  · exact K742Sat.s31.unsatFor
  · exact K742Sat.s32.unsatFor
  · exact K742Sat.s33.unsatFor
  · exact K742Sat.s34.unsatFor
  · exact K742Sat.s35.unsatFor
  · exact K742Sat.s36.unsatFor
  · exact K742Sat.s37.unsatFor
  · exact K742Sat.s38.unsatFor
  · exact K742Sat.s39.unsatFor
  · exact K742Sat.s40.unsatFor
  · exact K742Sat.s41.unsatFor
  · exact K742Sat.s42.unsatFor
  · exact K742Sat.s43.unsatFor
  · exact K742Sat.s44.unsatFor
  · exact K742Sat.s45.unsatFor
  · exact K742Sat.s46.unsatFor
  · exact K742Sat.s47.unsatFor
  · exact K742Sat.s48.unsatFor
  · exact K742Sat.s49.unsatFor
  · exact K742Sat.s50.unsatFor
  · exact K742Sat.s51.unsatFor
  · exact K742Sat.s52.unsatFor
  · exact K742Sat.s53.unsatFor
  · exact K742Sat.s54.unsatFor
  · exact K742Sat.s55.unsatFor
  · exact K742Sat.s56.unsatFor
  · exact K742Sat.s57.unsatFor
  · exact K742Sat.s58.unsatFor
  · exact K742Sat.s59.unsatFor
  · exact K742Sat.s60.unsatFor
  · exact K742Sat.s61.unsatFor
  · exact K742Sat.s62.unsatFor
  · exact K742Sat.s63.unsatFor
  · exact K742Sat.s64.unsatFor
  · exact K742Sat.s65.unsatFor
  · exact K742Sat.s66.unsatFor
  · exact K742Sat.s67.unsatFor
  · exact K742Sat.s68.unsatFor
  · exact K742Sat.s69.unsatFor

end K742Sat

#print axioms K742Sat.refut18
