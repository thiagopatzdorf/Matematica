import CoveringLean.SearchSound
import CoveringLean.G610_Chunk_0
import CoveringLean.G610_Chunk_1
import CoveringLean.G610_Chunk_2
import CoveringLean.G610_Chunk_3
import CoveringLean.G610_Chunk_4
import CoveringLean.G610_Chunk_5
import CoveringLean.G610_Chunk_6
import CoveringLean.G610_Chunk_7
import CoveringLean.G610_Chunk_8
import CoveringLean.G610_Chunk_9
import CoveringLean.G610_Chunk_10
import CoveringLean.G610_Chunk_11
import CoveringLean.G610_Chunk_12
import CoveringLean.G610_Chunk_13
import CoveringLean.G610_Chunk_14
import CoveringLean.G610_Chunk_15
import CoveringLean.G610_Chunk_16
import CoveringLean.G610_Chunk_17
import CoveringLean.G610_Chunk_18
import CoveringLean.G610_Chunk_19
import CoveringLean.G610_Chunk_20
import CoveringLean.G610_Chunk_21
import CoveringLean.G610_Chunk_22
import CoveringLean.G610_Chunk_23
import CoveringLean.G610_Chunk_24
import CoveringLean.G610_Chunk_25
import CoveringLean.G610_Chunk_26
import CoveringLean.G610_Chunk_27
import CoveringLean.G610_Chunk_28
import CoveringLean.G610_Chunk_29
import CoveringLean.G610_Chunk_30
import CoveringLean.G610_Chunk_31
import CoveringLean.G610_Chunk_32
import CoveringLean.G610_Chunk_33
import CoveringLean.G610_Chunk_34
import CoveringLean.G610_Chunk_35
import CoveringLean.G610_Chunk_36
import CoveringLean.G610_Chunk_37
open SC

namespace G610

/-- fronteira na profundidade 2, em ordem DFS -/
def S : List St := [
  ⟨8, 16753531392109382047, 9223372036854775817⟩,
  ⟨8, 16753531374929249631, 9223372036854775821⟩,
  ⟨8, 16753531366339183423, 9223372036854775823⟩,
  ⟨8, 16753531907513352703, 9223372036854775951⟩,
  ⟨8, 16753540153976393503, 9223372036854777999⟩,
  ⟨8, 16755783157706326303, 9223372036855302287⟩,
  ⟨8, 16755792563541180703, 9223372071215040655⟩,
  ⟨8, 16753531379224282735, 9223372036854775815⟩,
  ⟨8, 16753531396404415151, 9223372036854775823⟩,
  ⟨8, 16753531636926268159, 9223372036854775887⟩,
  ⟨8, 16753535760157789999, 9223372036854776911⟩,
  ⟨8, 16754657262023148079, 9223372036855039055⟩,
  ⟨8, 16754661990709985839, 9223372054034908239⟩,
  ⟨8, 16753531404994481359, 9223372036854775823⟩,
  ⟨8, 16753531508075275519, 9223372036854775855⟩,
  ⟨8, 16753533569691037519, 9223372036854776367⟩,
  ⟨8, 16754094320624010319, 9223372036854907439⟩,
  ⟨8, 16754096704294487119, 9223372045444842031⟩,
  ⟨8, 16753531456534878463, 9223372036854775839⟩,
  ⟨8, 16753531559615672563, 9223372036854775871⟩,
  ⟨8, 16753533621231434611, 9223372036854776383⟩,
  ⟨8, 16754094372164407411, 9223372036854907455⟩,
  ⟨8, 16754096755834884211, 9223372045444842047⟩,
  ⟨8, 16753532487342759823, 9223372036854776095⟩,
  ⟨8, 16753532590423553971, 9223372036854776127⟩,
  ⟨8, 16753534652039315203, 9223372036854776639⟩,
  ⟨8, 16754095402972288771, 9223372036854907711⟩,
  ⟨8, 16754097786642765571, 9223372045444842303⟩,
  ⟨8, 16753812862809344143, 9223372036854841631⟩,
  ⟨8, 16753812965890138291, 9223372036854841663⟩,
  ⟨8, 16753815027505900291, 9223372036854842175⟩,
  ⟨8, 16754375778438676483, 9223372036854973247⟩,
  ⟨8, 16754378162109349891, 9223372045444907839⟩,
  ⟨8, 16753814061086935183, 9223372041149808927⟩,
  ⟨8, 16753814164167729331, 9223372041149808959⟩,
  ⟨8, 16753816225783491331, 9223372041149809471⟩,
  ⟨8, 16754376976716464131, 9223372041149940543⟩,
  ⟨8, 16754379347502039043, 9223372049739875135⟩]

theorem top : chkN 6 S 2 (root 6 10) = true := by decide +kernel

theorem ref : Ref 6 (root 6 10) := by
  refine chkN_sound 6 S 2 _ top ?_
  intro t ht
  simp only [S, List.mem_cons, List.not_mem_nil, or_false] at ht
  rcases ht with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact chkN_sound 6 [] _ _ c0 (by simp)
  · exact chkN_sound 6 [] _ _ c1 (by simp)
  · exact chkN_sound 6 [] _ _ c2 (by simp)
  · exact chkN_sound 6 [] _ _ c3 (by simp)
  · exact chkN_sound 6 [] _ _ c4 (by simp)
  · exact chkN_sound 6 [] _ _ c5 (by simp)
  · exact chkN_sound 6 [] _ _ c6 (by simp)
  · exact chkN_sound 6 [] _ _ c7 (by simp)
  · exact chkN_sound 6 [] _ _ c8 (by simp)
  · exact chkN_sound 6 [] _ _ c9 (by simp)
  · exact chkN_sound 6 [] _ _ c10 (by simp)
  · exact chkN_sound 6 [] _ _ c11 (by simp)
  · exact chkN_sound 6 [] _ _ c12 (by simp)
  · exact chkN_sound 6 [] _ _ c13 (by simp)
  · exact chkN_sound 6 [] _ _ c14 (by simp)
  · exact chkN_sound 6 [] _ _ c15 (by simp)
  · exact chkN_sound 6 [] _ _ c16 (by simp)
  · exact chkN_sound 6 [] _ _ c17 (by simp)
  · exact chkN_sound 6 [] _ _ c18 (by simp)
  · exact chkN_sound 6 [] _ _ c19 (by simp)
  · exact chkN_sound 6 [] _ _ c20 (by simp)
  · exact chkN_sound 6 [] _ _ c21 (by simp)
  · exact chkN_sound 6 [] _ _ c22 (by simp)
  · exact chkN_sound 6 [] _ _ c23 (by simp)
  · exact chkN_sound 6 [] _ _ c24 (by simp)
  · exact chkN_sound 6 [] _ _ c25 (by simp)
  · exact chkN_sound 6 [] _ _ c26 (by simp)
  · exact chkN_sound 6 [] _ _ c27 (by simp)
  · exact chkN_sound 6 [] _ _ c28 (by simp)
  · exact chkN_sound 6 [] _ _ c29 (by simp)
  · exact chkN_sound 6 [] _ _ c30 (by simp)
  · exact chkN_sound 6 [] _ _ c31 (by simp)
  · exact chkN_sound 6 [] _ _ c32 (by simp)
  · exact chkN_sound 6 [] _ _ c33 (by simp)
  · exact chkN_sound 6 [] _ _ c34 (by simp)
  · exact chkN_sound 6 [] _ _ c35 (by simp)
  · exact chkN_sound 6 [] _ _ c36 (by simp)
  · exact chkN_sound 6 [] _ _ c37 (by simp)

end G610

#print axioms G610.ref
