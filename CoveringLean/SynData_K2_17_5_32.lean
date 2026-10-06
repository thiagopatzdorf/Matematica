-- gerado por scripts/syndrome/gen_syn.py; não editar à mão
import CoveringLean.SynCheck

/-! Dados do certificado `K2_17_5_32`: q=2, n=17, R=5, M=32.
sha256 canônico do código (palavras como strings w_0..w_(n-1), ordenadas, uma por linha): 3846acf19c6f319254936c157743657d4d83e828cbc1e5ee0c278a29f58ad4c3
C0 = [17,2]_2, bloco de informação [7,9), 8 cosets completos, 0 síndromes órfãs (0 pontos). -/

namespace Syn

def PK2_17_5_32 : Spec where
  q := 2
  n := 17
  k := 2
  o := 7
  R := 5
  Gs := [98559, 32512]
  reps := [0, 11356, 20082, 5678, 128105, 113205, 123419, 120903]
  orphs := []
  PN := 57586086628118126593050620592270677639826381800319372880920230935545427585645956963275716888089756642836402900817714826814892921297337214532247908562644649162571776
  b := 17
  cnt := 32

def LK2_17_5_32 : List Nat := [0, 2966, 5678, 7652, 10168, 11356, 12658, 15050, 17866, 20082, 21340, 22712, 25316, 26926, 29846, 32512, 98559, 101225, 104145, 105755, 108359, 109731, 110989, 113205, 116021, 118413, 119715, 120903, 123419, 125393, 128105, 131071]

end Syn
