import CoveringLean.Regras
import CoveringLean.K742_Upper
import CoveringLean.Ledger.W0
import CoveringLean.Ledger.W1
import CoveringLean.Ledger.W2
import CoveringLean.Ledger.W3

/-!
# Cotas superiores do ledger, célula base + regra (GERADO)

Gerado por `tools/certificar/gerar.py` a partir de `ledger/cells.json`; não edite à mão.
Cada `K<q>_<n>_<R>_le_<M>` é a melhor cota superior conhecida da célula.
-/

namespace CoveringLedger
open CoveringUB

-- raio ≥ n: uma palavra
theorem u2 : UB 2 1 1 1 :=
  UB.large_radius (q := 2) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u5 : UB 2 2 1 2 :=
  UB.constant_symbol (q := 2) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u7 : UB 2 2 2 1 :=
  UB.large_radius (q := 2) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u10 : UB 2 3 1 2 :=
  UB.constant_symbol (q := 2) (n := 3) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u12 : UB 2 3 2 2 :=
  UB.constant_symbol (q := 2) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u14 : UB 2 3 3 1 :=
  UB.large_radius (q := 2) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u18 : UB 2 4 2 2 :=
  UB.constant_symbol (q := 2) (n := 4) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u20 : UB 2 4 3 2 :=
  UB.constant_symbol (q := 2) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u22 : UB 2 4 4 1 :=
  UB.large_radius (q := 2) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u26 : UB 2 5 2 2 :=
  UB.constant_symbol (q := 2) (n := 5) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u28 : UB 2 5 3 2 :=
  UB.constant_symbol (q := 2) (n := 5) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u30 : UB 2 5 4 2 :=
  UB.constant_symbol (q := 2) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u32 : UB 2 5 5 1 :=
  UB.large_radius (q := 2) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u37 : UB 2 6 3 2 :=
  UB.constant_symbol (q := 2) (n := 6) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u39 : UB 2 6 4 2 :=
  UB.constant_symbol (q := 2) (n := 6) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u41 : UB 2 6 5 2 :=
  UB.constant_symbol (q := 2) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u43 : UB 2 6 6 1 :=
  UB.large_radius (q := 2) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u48 : UB 2 7 3 2 :=
  UB.constant_symbol (q := 2) (n := 7) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u50 : UB 2 7 4 2 :=
  UB.constant_symbol (q := 2) (n := 7) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u52 : UB 2 7 5 2 :=
  UB.constant_symbol (q := 2) (n := 7) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u54 : UB 2 7 6 2 :=
  UB.constant_symbol (q := 2) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u56 : UB 2 7 7 1 :=
  UB.large_radius (q := 2) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u62 : UB 2 8 4 2 :=
  UB.constant_symbol (q := 2) (n := 8) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u64 : UB 2 8 5 2 :=
  UB.constant_symbol (q := 2) (n := 8) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u66 : UB 2 8 6 2 :=
  UB.constant_symbol (q := 2) (n := 8) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u68 : UB 2 8 7 2 :=
  UB.constant_symbol (q := 2) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u70 : UB 2 8 8 1 :=
  UB.large_radius (q := 2) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u76 : UB 2 9 4 2 :=
  UB.constant_symbol (q := 2) (n := 9) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u78 : UB 2 9 5 2 :=
  UB.constant_symbol (q := 2) (n := 9) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u80 : UB 2 9 6 2 :=
  UB.constant_symbol (q := 2) (n := 9) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u82 : UB 2 9 7 2 :=
  UB.constant_symbol (q := 2) (n := 9) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u84 : UB 2 9 8 2 :=
  UB.constant_symbol (q := 2) (n := 9) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u86 : UB 2 9 9 1 :=
  UB.large_radius (q := 2) (n := 9) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u93 : UB 2 10 5 2 :=
  UB.constant_symbol (q := 2) (n := 10) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u95 : UB 2 10 6 2 :=
  UB.constant_symbol (q := 2) (n := 10) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u97 : UB 2 10 7 2 :=
  UB.constant_symbol (q := 2) (n := 10) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u99 : UB 2 10 8 2 :=
  UB.constant_symbol (q := 2) (n := 10) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u101 : UB 2 10 9 2 :=
  UB.constant_symbol (q := 2) (n := 10) (R := 9) (by decide)
-- raio ≥ n: uma palavra
theorem u103 : UB 2 10 10 1 :=
  UB.large_radius (q := 2) (n := 10) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u110 : UB 2 11 5 2 :=
  UB.constant_symbol (q := 2) (n := 11) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u112 : UB 2 11 6 2 :=
  UB.constant_symbol (q := 2) (n := 11) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u114 : UB 2 11 7 2 :=
  UB.constant_symbol (q := 2) (n := 11) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u116 : UB 2 11 8 2 :=
  UB.constant_symbol (q := 2) (n := 11) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u118 : UB 2 11 9 2 :=
  UB.constant_symbol (q := 2) (n := 11) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u120 : UB 2 11 10 2 :=
  UB.constant_symbol (q := 2) (n := 11) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u130 : UB 2 12 6 2 :=
  UB.constant_symbol (q := 2) (n := 12) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u132 : UB 2 12 7 2 :=
  UB.constant_symbol (q := 2) (n := 12) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u134 : UB 2 12 8 2 :=
  UB.constant_symbol (q := 2) (n := 12) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u136 : UB 2 12 9 2 :=
  UB.constant_symbol (q := 2) (n := 12) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u138 : UB 2 12 10 2 :=
  UB.constant_symbol (q := 2) (n := 12) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u150 : UB 2 13 6 2 :=
  UB.constant_symbol (q := 2) (n := 13) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u152 : UB 2 13 7 2 :=
  UB.constant_symbol (q := 2) (n := 13) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u154 : UB 2 13 8 2 :=
  UB.constant_symbol (q := 2) (n := 13) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u156 : UB 2 13 9 2 :=
  UB.constant_symbol (q := 2) (n := 13) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u158 : UB 2 13 10 2 :=
  UB.constant_symbol (q := 2) (n := 13) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u173 : UB 2 14 7 2 :=
  UB.constant_symbol (q := 2) (n := 14) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u175 : UB 2 14 8 2 :=
  UB.constant_symbol (q := 2) (n := 14) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u177 : UB 2 14 9 2 :=
  UB.constant_symbol (q := 2) (n := 14) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u179 : UB 2 14 10 2 :=
  UB.constant_symbol (q := 2) (n := 14) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u196 : UB 2 15 7 2 :=
  UB.constant_symbol (q := 2) (n := 15) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u198 : UB 2 15 8 2 :=
  UB.constant_symbol (q := 2) (n := 15) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u200 : UB 2 15 9 2 :=
  UB.constant_symbol (q := 2) (n := 15) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u202 : UB 2 15 10 2 :=
  UB.constant_symbol (q := 2) (n := 15) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u222 : UB 2 16 8 2 :=
  UB.constant_symbol (q := 2) (n := 16) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u224 : UB 2 16 9 2 :=
  UB.constant_symbol (q := 2) (n := 16) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u226 : UB 2 16 10 2 :=
  UB.constant_symbol (q := 2) (n := 16) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u248 : UB 2 17 8 2 :=
  UB.constant_symbol (q := 2) (n := 17) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u250 : UB 2 17 9 2 :=
  UB.constant_symbol (q := 2) (n := 17) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u252 : UB 2 17 10 2 :=
  UB.constant_symbol (q := 2) (n := 17) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u277 : UB 2 18 9 2 :=
  UB.constant_symbol (q := 2) (n := 18) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u279 : UB 2 18 10 2 :=
  UB.constant_symbol (q := 2) (n := 18) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u306 : UB 2 19 9 2 :=
  UB.constant_symbol (q := 2) (n := 19) (R := 9) (by decide)
-- palavras constantes (pombal)
theorem u308 : UB 2 19 10 2 :=
  UB.constant_symbol (q := 2) (n := 19) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u338 : UB 2 20 10 2 :=
  UB.constant_symbol (q := 2) (n := 20) (R := 10) (by decide)
-- palavras constantes (pombal)
theorem u370 : UB 2 21 10 2 :=
  UB.constant_symbol (q := 2) (n := 21) (R := 10) (by decide)
-- raio ≥ n: uma palavra
theorem u917 : UB 3 1 1 1 :=
  UB.large_radius (q := 3) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u920 : UB 3 2 1 3 :=
  UB.constant_symbol (q := 3) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u922 : UB 3 2 2 1 :=
  UB.large_radius (q := 3) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u926 : UB 3 3 2 3 :=
  UB.constant_symbol (q := 3) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u928 : UB 3 3 3 1 :=
  UB.large_radius (q := 3) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u932 : UB 3 4 2 3 :=
  UB.constant_symbol (q := 3) (n := 4) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u934 : UB 3 4 3 3 :=
  UB.constant_symbol (q := 3) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u936 : UB 3 4 4 1 :=
  UB.large_radius (q := 3) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u941 : UB 3 5 3 3 :=
  UB.constant_symbol (q := 3) (n := 5) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u943 : UB 3 5 4 3 :=
  UB.constant_symbol (q := 3) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u945 : UB 3 5 5 1 :=
  UB.large_radius (q := 3) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u951 : UB 3 6 4 3 :=
  UB.constant_symbol (q := 3) (n := 6) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u953 : UB 3 6 5 3 :=
  UB.constant_symbol (q := 3) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u955 : UB 3 6 6 1 :=
  UB.large_radius (q := 3) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u961 : UB 3 7 4 3 :=
  UB.constant_symbol (q := 3) (n := 7) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u963 : UB 3 7 5 3 :=
  UB.constant_symbol (q := 3) (n := 7) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u965 : UB 3 7 6 3 :=
  UB.constant_symbol (q := 3) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u967 : UB 3 7 7 1 :=
  UB.large_radius (q := 3) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u974 : UB 3 8 5 3 :=
  UB.constant_symbol (q := 3) (n := 8) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u976 : UB 3 8 6 3 :=
  UB.constant_symbol (q := 3) (n := 8) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u978 : UB 3 8 7 3 :=
  UB.constant_symbol (q := 3) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u980 : UB 3 8 8 1 :=
  UB.large_radius (q := 3) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u988 : UB 3 9 6 3 :=
  UB.constant_symbol (q := 3) (n := 9) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u990 : UB 3 9 7 3 :=
  UB.constant_symbol (q := 3) (n := 9) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u992 : UB 3 9 8 3 :=
  UB.constant_symbol (q := 3) (n := 9) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1002 : UB 3 10 6 3 :=
  UB.constant_symbol (q := 3) (n := 10) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1004 : UB 3 10 7 3 :=
  UB.constant_symbol (q := 3) (n := 10) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1006 : UB 3 10 8 3 :=
  UB.constant_symbol (q := 3) (n := 10) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1019 : UB 3 11 7 3 :=
  UB.constant_symbol (q := 3) (n := 11) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1021 : UB 3 11 8 3 :=
  UB.constant_symbol (q := 3) (n := 11) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1037 : UB 3 12 8 3 :=
  UB.constant_symbol (q := 3) (n := 12) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1055 : UB 3 13 8 3 :=
  UB.constant_symbol (q := 3) (n := 13) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1089 : UB 4 1 1 1 :=
  UB.large_radius (q := 4) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1092 : UB 4 2 1 4 :=
  UB.constant_symbol (q := 4) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1094 : UB 4 2 2 1 :=
  UB.large_radius (q := 4) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1098 : UB 4 3 2 4 :=
  UB.constant_symbol (q := 4) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1100 : UB 4 3 3 1 :=
  UB.large_radius (q := 4) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1105 : UB 4 4 3 4 :=
  UB.constant_symbol (q := 4) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1107 : UB 4 4 4 1 :=
  UB.large_radius (q := 4) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1112 : UB 4 5 3 4 :=
  UB.constant_symbol (q := 4) (n := 5) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1114 : UB 4 5 4 4 :=
  UB.constant_symbol (q := 4) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1116 : UB 4 5 5 1 :=
  UB.large_radius (q := 4) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1122 : UB 4 6 4 4 :=
  UB.constant_symbol (q := 4) (n := 6) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1124 : UB 4 6 5 4 :=
  UB.constant_symbol (q := 4) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1126 : UB 4 6 6 1 :=
  UB.large_radius (q := 4) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1133 : UB 4 7 5 4 :=
  UB.constant_symbol (q := 4) (n := 7) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1135 : UB 4 7 6 4 :=
  UB.constant_symbol (q := 4) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1137 : UB 4 7 7 1 :=
  UB.large_radius (q := 4) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1145 : UB 4 8 6 4 :=
  UB.constant_symbol (q := 4) (n := 8) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1147 : UB 4 8 7 4 :=
  UB.constant_symbol (q := 4) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1149 : UB 4 8 8 1 :=
  UB.large_radius (q := 4) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1157 : UB 4 9 6 4 :=
  UB.constant_symbol (q := 4) (n := 9) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1159 : UB 4 9 7 4 :=
  UB.constant_symbol (q := 4) (n := 9) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1161 : UB 4 9 8 4 :=
  UB.constant_symbol (q := 4) (n := 9) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1172 : UB 4 10 7 4 :=
  UB.constant_symbol (q := 4) (n := 10) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1174 : UB 4 10 8 4 :=
  UB.constant_symbol (q := 4) (n := 10) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1188 : UB 4 11 8 4 :=
  UB.constant_symbol (q := 4) (n := 11) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1197 : UB 5 1 1 1 :=
  UB.large_radius (q := 5) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1200 : UB 5 2 1 5 :=
  UB.constant_symbol (q := 5) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1202 : UB 5 2 2 1 :=
  UB.large_radius (q := 5) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1206 : UB 5 3 2 5 :=
  UB.constant_symbol (q := 5) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1208 : UB 5 3 3 1 :=
  UB.large_radius (q := 5) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1213 : UB 5 4 3 5 :=
  UB.constant_symbol (q := 5) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1215 : UB 5 4 4 1 :=
  UB.large_radius (q := 5) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1221 : UB 5 5 4 5 :=
  UB.constant_symbol (q := 5) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1223 : UB 5 5 5 1 :=
  UB.large_radius (q := 5) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1229 : UB 5 6 4 5 :=
  UB.constant_symbol (q := 5) (n := 6) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1231 : UB 5 6 5 5 :=
  UB.constant_symbol (q := 5) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1233 : UB 5 6 6 1 :=
  UB.large_radius (q := 5) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1240 : UB 5 7 5 5 :=
  UB.constant_symbol (q := 5) (n := 7) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1242 : UB 5 7 6 5 :=
  UB.constant_symbol (q := 5) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1244 : UB 5 7 7 1 :=
  UB.large_radius (q := 5) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1252 : UB 5 8 6 5 :=
  UB.constant_symbol (q := 5) (n := 8) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1254 : UB 5 8 7 5 :=
  UB.constant_symbol (q := 5) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1256 : UB 5 8 8 1 :=
  UB.large_radius (q := 5) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1265 : UB 5 9 7 5 :=
  UB.constant_symbol (q := 5) (n := 9) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1267 : UB 5 9 8 5 :=
  UB.constant_symbol (q := 5) (n := 9) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1279 : UB 5 10 8 5 :=
  UB.constant_symbol (q := 5) (n := 10) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1293 : UB 5 11 8 5 :=
  UB.constant_symbol (q := 5) (n := 11) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1302 : UB 6 1 1 1 :=
  UB.large_radius (q := 6) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1305 : UB 6 2 1 6 :=
  UB.constant_symbol (q := 6) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1307 : UB 6 2 2 1 :=
  UB.large_radius (q := 6) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1311 : UB 6 3 2 6 :=
  UB.constant_symbol (q := 6) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1313 : UB 6 3 3 1 :=
  UB.large_radius (q := 6) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1318 : UB 6 4 3 6 :=
  UB.constant_symbol (q := 6) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1320 : UB 6 4 4 1 :=
  UB.large_radius (q := 6) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1326 : UB 6 5 4 6 :=
  UB.constant_symbol (q := 6) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1328 : UB 6 5 5 1 :=
  UB.large_radius (q := 6) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1335 : UB 6 6 5 6 :=
  UB.constant_symbol (q := 6) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1337 : UB 6 6 6 1 :=
  UB.large_radius (q := 6) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1344 : UB 6 7 5 6 :=
  UB.constant_symbol (q := 6) (n := 7) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1346 : UB 6 7 6 6 :=
  UB.constant_symbol (q := 6) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1348 : UB 6 7 7 1 :=
  UB.large_radius (q := 6) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1356 : UB 6 8 6 6 :=
  UB.constant_symbol (q := 6) (n := 8) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1358 : UB 6 8 7 6 :=
  UB.constant_symbol (q := 6) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1360 : UB 6 8 8 1 :=
  UB.large_radius (q := 6) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1369 : UB 6 9 7 6 :=
  UB.constant_symbol (q := 6) (n := 9) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1371 : UB 6 9 8 6 :=
  UB.constant_symbol (q := 6) (n := 9) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1383 : UB 6 10 8 6 :=
  UB.constant_symbol (q := 6) (n := 10) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1390 : UB 7 1 1 1 :=
  UB.large_radius (q := 7) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1393 : UB 7 2 1 7 :=
  UB.constant_symbol (q := 7) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1395 : UB 7 2 2 1 :=
  UB.large_radius (q := 7) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1399 : UB 7 3 2 7 :=
  UB.constant_symbol (q := 7) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1401 : UB 7 3 3 1 :=
  UB.large_radius (q := 7) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1406 : UB 7 4 3 7 :=
  UB.constant_symbol (q := 7) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1408 : UB 7 4 4 1 :=
  UB.large_radius (q := 7) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1414 : UB 7 5 4 7 :=
  UB.constant_symbol (q := 7) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1416 : UB 7 5 5 1 :=
  UB.large_radius (q := 7) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1423 : UB 7 6 5 7 :=
  UB.constant_symbol (q := 7) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1425 : UB 7 6 6 1 :=
  UB.large_radius (q := 7) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1433 : UB 7 7 6 7 :=
  UB.constant_symbol (q := 7) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1435 : UB 7 7 7 1 :=
  UB.large_radius (q := 7) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1443 : UB 7 8 6 7 :=
  UB.constant_symbol (q := 7) (n := 8) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1445 : UB 7 8 7 7 :=
  UB.constant_symbol (q := 7) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1447 : UB 7 8 8 1 :=
  UB.large_radius (q := 7) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1456 : UB 7 9 7 7 :=
  UB.constant_symbol (q := 7) (n := 9) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1458 : UB 7 9 8 7 :=
  UB.constant_symbol (q := 7) (n := 9) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1470 : UB 7 10 8 7 :=
  UB.constant_symbol (q := 7) (n := 10) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1477 : UB 8 1 1 1 :=
  UB.large_radius (q := 8) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1480 : UB 8 2 1 8 :=
  UB.constant_symbol (q := 8) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1482 : UB 8 2 2 1 :=
  UB.large_radius (q := 8) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1486 : UB 8 3 2 8 :=
  UB.constant_symbol (q := 8) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1488 : UB 8 3 3 1 :=
  UB.large_radius (q := 8) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1493 : UB 8 4 3 8 :=
  UB.constant_symbol (q := 8) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1495 : UB 8 4 4 1 :=
  UB.large_radius (q := 8) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1501 : UB 8 5 4 8 :=
  UB.constant_symbol (q := 8) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1503 : UB 8 5 5 1 :=
  UB.large_radius (q := 8) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1510 : UB 8 6 5 8 :=
  UB.constant_symbol (q := 8) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1512 : UB 8 6 6 1 :=
  UB.large_radius (q := 8) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1520 : UB 8 7 6 8 :=
  UB.constant_symbol (q := 8) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1522 : UB 8 7 7 1 :=
  UB.large_radius (q := 8) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1531 : UB 8 8 7 8 :=
  UB.constant_symbol (q := 8) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1533 : UB 8 8 8 1 :=
  UB.large_radius (q := 8) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1542 : UB 8 9 7 8 :=
  UB.constant_symbol (q := 8) (n := 9) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1544 : UB 8 9 8 8 :=
  UB.constant_symbol (q := 8) (n := 9) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1556 : UB 8 10 8 8 :=
  UB.constant_symbol (q := 8) (n := 10) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1563 : UB 9 1 1 1 :=
  UB.large_radius (q := 9) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1566 : UB 9 2 1 9 :=
  UB.constant_symbol (q := 9) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1568 : UB 9 2 2 1 :=
  UB.large_radius (q := 9) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1572 : UB 9 3 2 9 :=
  UB.constant_symbol (q := 9) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1574 : UB 9 3 3 1 :=
  UB.large_radius (q := 9) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1579 : UB 9 4 3 9 :=
  UB.constant_symbol (q := 9) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1581 : UB 9 4 4 1 :=
  UB.large_radius (q := 9) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1587 : UB 9 5 4 9 :=
  UB.constant_symbol (q := 9) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1589 : UB 9 5 5 1 :=
  UB.large_radius (q := 9) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1596 : UB 9 6 5 9 :=
  UB.constant_symbol (q := 9) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1598 : UB 9 6 6 1 :=
  UB.large_radius (q := 9) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1606 : UB 9 7 6 9 :=
  UB.constant_symbol (q := 9) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1608 : UB 9 7 7 1 :=
  UB.large_radius (q := 9) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1617 : UB 9 8 7 9 :=
  UB.constant_symbol (q := 9) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1619 : UB 9 8 8 1 :=
  UB.large_radius (q := 9) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1629 : UB 9 9 8 9 :=
  UB.constant_symbol (q := 9) (n := 9) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1641 : UB 9 10 8 9 :=
  UB.constant_symbol (q := 9) (n := 10) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1648 : UB 10 1 1 1 :=
  UB.large_radius (q := 10) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1651 : UB 10 2 1 10 :=
  UB.constant_symbol (q := 10) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1653 : UB 10 2 2 1 :=
  UB.large_radius (q := 10) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1657 : UB 10 3 2 10 :=
  UB.constant_symbol (q := 10) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1659 : UB 10 3 3 1 :=
  UB.large_radius (q := 10) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1664 : UB 10 4 3 10 :=
  UB.constant_symbol (q := 10) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1666 : UB 10 4 4 1 :=
  UB.large_radius (q := 10) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1672 : UB 10 5 4 10 :=
  UB.constant_symbol (q := 10) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1674 : UB 10 5 5 1 :=
  UB.large_radius (q := 10) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1681 : UB 10 6 5 10 :=
  UB.constant_symbol (q := 10) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1683 : UB 10 6 6 1 :=
  UB.large_radius (q := 10) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1691 : UB 10 7 6 10 :=
  UB.constant_symbol (q := 10) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1693 : UB 10 7 7 1 :=
  UB.large_radius (q := 10) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1702 : UB 10 8 7 10 :=
  UB.constant_symbol (q := 10) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1704 : UB 10 8 8 1 :=
  UB.large_radius (q := 10) (n := 8) (R := 8) (by decide)
-- palavras constantes (pombal)
theorem u1714 : UB 10 9 8 10 :=
  UB.constant_symbol (q := 10) (n := 9) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1732 : UB 11 1 1 1 :=
  UB.large_radius (q := 11) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1735 : UB 11 2 1 11 :=
  UB.constant_symbol (q := 11) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1737 : UB 11 2 2 1 :=
  UB.large_radius (q := 11) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1741 : UB 11 3 2 11 :=
  UB.constant_symbol (q := 11) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1743 : UB 11 3 3 1 :=
  UB.large_radius (q := 11) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1748 : UB 11 4 3 11 :=
  UB.constant_symbol (q := 11) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1750 : UB 11 4 4 1 :=
  UB.large_radius (q := 11) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1756 : UB 11 5 4 11 :=
  UB.constant_symbol (q := 11) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1758 : UB 11 5 5 1 :=
  UB.large_radius (q := 11) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1765 : UB 11 6 5 11 :=
  UB.constant_symbol (q := 11) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1767 : UB 11 6 6 1 :=
  UB.large_radius (q := 11) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1775 : UB 11 7 6 11 :=
  UB.constant_symbol (q := 11) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1777 : UB 11 7 7 1 :=
  UB.large_radius (q := 11) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1786 : UB 11 8 7 11 :=
  UB.constant_symbol (q := 11) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1788 : UB 11 8 8 1 :=
  UB.large_radius (q := 11) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1791 : UB 12 1 1 1 :=
  UB.large_radius (q := 12) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1794 : UB 12 2 1 12 :=
  UB.constant_symbol (q := 12) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1796 : UB 12 2 2 1 :=
  UB.large_radius (q := 12) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1800 : UB 12 3 2 12 :=
  UB.constant_symbol (q := 12) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1802 : UB 12 3 3 1 :=
  UB.large_radius (q := 12) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1807 : UB 12 4 3 12 :=
  UB.constant_symbol (q := 12) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1809 : UB 12 4 4 1 :=
  UB.large_radius (q := 12) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1815 : UB 12 5 4 12 :=
  UB.constant_symbol (q := 12) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1817 : UB 12 5 5 1 :=
  UB.large_radius (q := 12) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1824 : UB 12 6 5 12 :=
  UB.constant_symbol (q := 12) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1826 : UB 12 6 6 1 :=
  UB.large_radius (q := 12) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1834 : UB 12 7 6 12 :=
  UB.constant_symbol (q := 12) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1836 : UB 12 7 7 1 :=
  UB.large_radius (q := 12) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1845 : UB 12 8 7 12 :=
  UB.constant_symbol (q := 12) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1847 : UB 12 8 8 1 :=
  UB.large_radius (q := 12) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1850 : UB 13 1 1 1 :=
  UB.large_radius (q := 13) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1853 : UB 13 2 1 13 :=
  UB.constant_symbol (q := 13) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1855 : UB 13 2 2 1 :=
  UB.large_radius (q := 13) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1859 : UB 13 3 2 13 :=
  UB.constant_symbol (q := 13) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1861 : UB 13 3 3 1 :=
  UB.large_radius (q := 13) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1866 : UB 13 4 3 13 :=
  UB.constant_symbol (q := 13) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1868 : UB 13 4 4 1 :=
  UB.large_radius (q := 13) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1874 : UB 13 5 4 13 :=
  UB.constant_symbol (q := 13) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1876 : UB 13 5 5 1 :=
  UB.large_radius (q := 13) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1883 : UB 13 6 5 13 :=
  UB.constant_symbol (q := 13) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1885 : UB 13 6 6 1 :=
  UB.large_radius (q := 13) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1893 : UB 13 7 6 13 :=
  UB.constant_symbol (q := 13) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1895 : UB 13 7 7 1 :=
  UB.large_radius (q := 13) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1904 : UB 13 8 7 13 :=
  UB.constant_symbol (q := 13) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1906 : UB 13 8 8 1 :=
  UB.large_radius (q := 13) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1909 : UB 14 1 1 1 :=
  UB.large_radius (q := 14) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1912 : UB 14 2 1 14 :=
  UB.constant_symbol (q := 14) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1914 : UB 14 2 2 1 :=
  UB.large_radius (q := 14) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1918 : UB 14 3 2 14 :=
  UB.constant_symbol (q := 14) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1920 : UB 14 3 3 1 :=
  UB.large_radius (q := 14) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1925 : UB 14 4 3 14 :=
  UB.constant_symbol (q := 14) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1927 : UB 14 4 4 1 :=
  UB.large_radius (q := 14) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1933 : UB 14 5 4 14 :=
  UB.constant_symbol (q := 14) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1935 : UB 14 5 5 1 :=
  UB.large_radius (q := 14) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u1942 : UB 14 6 5 14 :=
  UB.constant_symbol (q := 14) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u1944 : UB 14 6 6 1 :=
  UB.large_radius (q := 14) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u1952 : UB 14 7 6 14 :=
  UB.constant_symbol (q := 14) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u1954 : UB 14 7 7 1 :=
  UB.large_radius (q := 14) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u1963 : UB 14 8 7 14 :=
  UB.constant_symbol (q := 14) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u1965 : UB 14 8 8 1 :=
  UB.large_radius (q := 14) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u1968 : UB 15 1 1 1 :=
  UB.large_radius (q := 15) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u1971 : UB 15 2 1 15 :=
  UB.constant_symbol (q := 15) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u1973 : UB 15 2 2 1 :=
  UB.large_radius (q := 15) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u1977 : UB 15 3 2 15 :=
  UB.constant_symbol (q := 15) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u1979 : UB 15 3 3 1 :=
  UB.large_radius (q := 15) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u1984 : UB 15 4 3 15 :=
  UB.constant_symbol (q := 15) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u1986 : UB 15 4 4 1 :=
  UB.large_radius (q := 15) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u1992 : UB 15 5 4 15 :=
  UB.constant_symbol (q := 15) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u1994 : UB 15 5 5 1 :=
  UB.large_radius (q := 15) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u2001 : UB 15 6 5 15 :=
  UB.constant_symbol (q := 15) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u2003 : UB 15 6 6 1 :=
  UB.large_radius (q := 15) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u2011 : UB 15 7 6 15 :=
  UB.constant_symbol (q := 15) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u2013 : UB 15 7 7 1 :=
  UB.large_radius (q := 15) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u2022 : UB 15 8 7 15 :=
  UB.constant_symbol (q := 15) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u2024 : UB 15 8 8 1 :=
  UB.large_radius (q := 15) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u2027 : UB 16 1 1 1 :=
  UB.large_radius (q := 16) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u2030 : UB 16 2 1 16 :=
  UB.constant_symbol (q := 16) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u2032 : UB 16 2 2 1 :=
  UB.large_radius (q := 16) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u2036 : UB 16 3 2 16 :=
  UB.constant_symbol (q := 16) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u2038 : UB 16 3 3 1 :=
  UB.large_radius (q := 16) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u2043 : UB 16 4 3 16 :=
  UB.constant_symbol (q := 16) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u2045 : UB 16 4 4 1 :=
  UB.large_radius (q := 16) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u2051 : UB 16 5 4 16 :=
  UB.constant_symbol (q := 16) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u2053 : UB 16 5 5 1 :=
  UB.large_radius (q := 16) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u2060 : UB 16 6 5 16 :=
  UB.constant_symbol (q := 16) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u2062 : UB 16 6 6 1 :=
  UB.large_radius (q := 16) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u2070 : UB 16 7 6 16 :=
  UB.constant_symbol (q := 16) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u2072 : UB 16 7 7 1 :=
  UB.large_radius (q := 16) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u2081 : UB 16 8 7 16 :=
  UB.constant_symbol (q := 16) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u2083 : UB 16 8 8 1 :=
  UB.large_radius (q := 16) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u2086 : UB 17 1 1 1 :=
  UB.large_radius (q := 17) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u2089 : UB 17 2 1 17 :=
  UB.constant_symbol (q := 17) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u2091 : UB 17 2 2 1 :=
  UB.large_radius (q := 17) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u2095 : UB 17 3 2 17 :=
  UB.constant_symbol (q := 17) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u2097 : UB 17 3 3 1 :=
  UB.large_radius (q := 17) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u2102 : UB 17 4 3 17 :=
  UB.constant_symbol (q := 17) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u2104 : UB 17 4 4 1 :=
  UB.large_radius (q := 17) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u2110 : UB 17 5 4 17 :=
  UB.constant_symbol (q := 17) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u2112 : UB 17 5 5 1 :=
  UB.large_radius (q := 17) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u2119 : UB 17 6 5 17 :=
  UB.constant_symbol (q := 17) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u2121 : UB 17 6 6 1 :=
  UB.large_radius (q := 17) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u2129 : UB 17 7 6 17 :=
  UB.constant_symbol (q := 17) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u2131 : UB 17 7 7 1 :=
  UB.large_radius (q := 17) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u2140 : UB 17 8 7 17 :=
  UB.constant_symbol (q := 17) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u2142 : UB 17 8 8 1 :=
  UB.large_radius (q := 17) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u2145 : UB 18 1 1 1 :=
  UB.large_radius (q := 18) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u2148 : UB 18 2 1 18 :=
  UB.constant_symbol (q := 18) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u2150 : UB 18 2 2 1 :=
  UB.large_radius (q := 18) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u2154 : UB 18 3 2 18 :=
  UB.constant_symbol (q := 18) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u2156 : UB 18 3 3 1 :=
  UB.large_radius (q := 18) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u2161 : UB 18 4 3 18 :=
  UB.constant_symbol (q := 18) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u2163 : UB 18 4 4 1 :=
  UB.large_radius (q := 18) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u2169 : UB 18 5 4 18 :=
  UB.constant_symbol (q := 18) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u2171 : UB 18 5 5 1 :=
  UB.large_radius (q := 18) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u2178 : UB 18 6 5 18 :=
  UB.constant_symbol (q := 18) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u2180 : UB 18 6 6 1 :=
  UB.large_radius (q := 18) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u2188 : UB 18 7 6 18 :=
  UB.constant_symbol (q := 18) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u2190 : UB 18 7 7 1 :=
  UB.large_radius (q := 18) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u2199 : UB 18 8 7 18 :=
  UB.constant_symbol (q := 18) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u2201 : UB 18 8 8 1 :=
  UB.large_radius (q := 18) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u2204 : UB 19 1 1 1 :=
  UB.large_radius (q := 19) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u2207 : UB 19 2 1 19 :=
  UB.constant_symbol (q := 19) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u2209 : UB 19 2 2 1 :=
  UB.large_radius (q := 19) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u2213 : UB 19 3 2 19 :=
  UB.constant_symbol (q := 19) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u2215 : UB 19 3 3 1 :=
  UB.large_radius (q := 19) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u2220 : UB 19 4 3 19 :=
  UB.constant_symbol (q := 19) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u2222 : UB 19 4 4 1 :=
  UB.large_radius (q := 19) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u2228 : UB 19 5 4 19 :=
  UB.constant_symbol (q := 19) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u2230 : UB 19 5 5 1 :=
  UB.large_radius (q := 19) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u2237 : UB 19 6 5 19 :=
  UB.constant_symbol (q := 19) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u2239 : UB 19 6 6 1 :=
  UB.large_radius (q := 19) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u2247 : UB 19 7 6 19 :=
  UB.constant_symbol (q := 19) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u2249 : UB 19 7 7 1 :=
  UB.large_radius (q := 19) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u2258 : UB 19 8 7 19 :=
  UB.constant_symbol (q := 19) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u2260 : UB 19 8 8 1 :=
  UB.large_radius (q := 19) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u2263 : UB 20 1 1 1 :=
  UB.large_radius (q := 20) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u2266 : UB 20 2 1 20 :=
  UB.constant_symbol (q := 20) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u2268 : UB 20 2 2 1 :=
  UB.large_radius (q := 20) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u2272 : UB 20 3 2 20 :=
  UB.constant_symbol (q := 20) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u2274 : UB 20 3 3 1 :=
  UB.large_radius (q := 20) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u2279 : UB 20 4 3 20 :=
  UB.constant_symbol (q := 20) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u2281 : UB 20 4 4 1 :=
  UB.large_radius (q := 20) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u2287 : UB 20 5 4 20 :=
  UB.constant_symbol (q := 20) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u2289 : UB 20 5 5 1 :=
  UB.large_radius (q := 20) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u2296 : UB 20 6 5 20 :=
  UB.constant_symbol (q := 20) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u2298 : UB 20 6 6 1 :=
  UB.large_radius (q := 20) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u2306 : UB 20 7 6 20 :=
  UB.constant_symbol (q := 20) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u2308 : UB 20 7 7 1 :=
  UB.large_radius (q := 20) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u2317 : UB 20 8 7 20 :=
  UB.constant_symbol (q := 20) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u2319 : UB 20 8 8 1 :=
  UB.large_radius (q := 20) (n := 8) (R := 8) (by decide)
-- raio ≥ n: uma palavra
theorem u2322 : UB 21 1 1 1 :=
  UB.large_radius (q := 21) (n := 1) (R := 1) (by decide)
-- palavras constantes (pombal)
theorem u2325 : UB 21 2 1 21 :=
  UB.constant_symbol (q := 21) (n := 2) (R := 1) (by decide)
-- raio ≥ n: uma palavra
theorem u2327 : UB 21 2 2 1 :=
  UB.large_radius (q := 21) (n := 2) (R := 2) (by decide)
-- palavras constantes (pombal)
theorem u2331 : UB 21 3 2 21 :=
  UB.constant_symbol (q := 21) (n := 3) (R := 2) (by decide)
-- raio ≥ n: uma palavra
theorem u2333 : UB 21 3 3 1 :=
  UB.large_radius (q := 21) (n := 3) (R := 3) (by decide)
-- palavras constantes (pombal)
theorem u2338 : UB 21 4 3 21 :=
  UB.constant_symbol (q := 21) (n := 4) (R := 3) (by decide)
-- raio ≥ n: uma palavra
theorem u2340 : UB 21 4 4 1 :=
  UB.large_radius (q := 21) (n := 4) (R := 4) (by decide)
-- palavras constantes (pombal)
theorem u2346 : UB 21 5 4 21 :=
  UB.constant_symbol (q := 21) (n := 5) (R := 4) (by decide)
-- raio ≥ n: uma palavra
theorem u2348 : UB 21 5 5 1 :=
  UB.large_radius (q := 21) (n := 5) (R := 5) (by decide)
-- palavras constantes (pombal)
theorem u2355 : UB 21 6 5 21 :=
  UB.constant_symbol (q := 21) (n := 6) (R := 5) (by decide)
-- raio ≥ n: uma palavra
theorem u2357 : UB 21 6 6 1 :=
  UB.large_radius (q := 21) (n := 6) (R := 6) (by decide)
-- palavras constantes (pombal)
theorem u2365 : UB 21 7 6 21 :=
  UB.constant_symbol (q := 21) (n := 7) (R := 6) (by decide)
-- raio ≥ n: uma palavra
theorem u2367 : UB 21 7 7 1 :=
  UB.large_radius (q := 21) (n := 7) (R := 7) (by decide)
-- palavras constantes (pombal)
theorem u2376 : UB 21 8 7 21 :=
  UB.constant_symbol (q := 21) (n := 8) (R := 7) (by decide)
-- raio ≥ n: uma palavra
theorem u2378 : UB 21 8 8 1 :=
  UB.large_radius (q := 21) (n := 8) (R := 8) (by decide)
-- witness explícito
theorem u2379 : UB 10 3 1 50 :=
  Data.w_K10_3_1
-- witness explícito
theorem u2380 : UB 10 4 2 34 :=
  Data.w_K10_4_2
-- witness explícito
theorem u2381 : UB 11 3 1 61 :=
  Data.w_K11_3_1
-- witness explícito
theorem u2382 : UB 11 4 2 41 :=
  Data.w_K11_4_2
-- witness explícito
theorem u2383 : UB 12 3 1 72 :=
  Data.w_K12_3_1
-- witness explícito
theorem u2384 : UB 12 4 2 48 :=
  Data.w_K12_4_2
-- witness explícito
theorem u2385 : UB 13 3 1 85 :=
  Data.w_K13_3_1
-- witness explícito
theorem u2386 : UB 14 3 1 98 :=
  Data.w_K14_3_1
-- witness explícito
theorem u2387 : UB 15 3 1 113 :=
  Data.w_K15_3_1
-- witness explícito
theorem u2388 : UB 16 3 1 128 :=
  Data.w_K16_3_1
-- witness explícito
theorem u2389 : UB 17 3 1 145 :=
  Data.w_K17_3_1
-- witness explícito
theorem u2390 : UB 18 3 1 162 :=
  Data.w_K18_3_1
-- witness explícito
theorem u2391 : UB 2 10 3 12 :=
  Data.w_K2_10_3
-- witness explícito
theorem u2392 : UB 2 11 1 192 :=
  Data.w_K2_11_1
-- witness explícito
theorem u2393 : UB 2 11 3 16 :=
  Data.w_K2_11_3
-- witness explícito
theorem u2394 : UB 2 5 1 7 :=
  Data.w_K2_5_1
-- witness explícito
theorem u2395 : UB 2 6 1 12 :=
  Data.w_K2_6_1
-- witness explícito
theorem u2396 : UB 2 6 2 4 :=
  Data.w_K2_6_2
-- witness explícito
theorem u2397 : UB 2 7 1 16 :=
  Data.w_K2_7_1
-- witness explícito
theorem u2398 : UB 2 7 2 7 :=
  Data.w_K2_7_2
-- witness explícito
theorem u2399 : UB 2 8 1 32 :=
  Data.w_K2_8_1
-- witness explícito
theorem u2400 : UB 2 8 2 12 :=
  Data.w_K2_8_2
-- witness explícito
theorem u2401 : UB 2 9 2 16 :=
  Data.w_K2_9_2
-- witness explícito
theorem u2402 : UB 2 9 3 7 :=
  Data.w_K2_9_3
-- witness explícito
theorem u2403 : UB 3 3 1 5 :=
  Data.w_K3_3_1
-- witness explícito
theorem u2404 : UB 3 4 1 9 :=
  Data.w_K3_4_1
-- witness explícito
theorem u2405 : UB 3 5 2 8 :=
  Data.w_K3_5_2
-- witness explícito
theorem u2406 : UB 3 6 2 17 :=
  Data.w_K3_6_2
-- witness explícito
theorem u2407 : UB 3 6 3 6 :=
  Data.w_K3_6_3
-- witness explícito
theorem u2408 : UB 4 3 1 8 :=
  Data.w_K4_3_1
-- witness explícito
theorem u2409 : UB 4 4 1 24 :=
  Data.w_K4_4_1
-- witness explícito
theorem u2410 : UB 4 4 2 7 :=
  Data.w_K4_4_2
-- witness explícito
theorem u2411 : UB 5 3 1 13 :=
  Data.w_K5_3_1
-- witness explícito
theorem u2412 : UB 5 4 2 11 :=
  Data.w_K5_4_2
-- witness explícito
theorem u2413 : UB 6 3 1 18 :=
  Data.w_K6_3_1
-- witness explícito
theorem u2414 : UB 6 4 2 15 :=
  Data.w_K6_4_2
-- witness explícito
theorem u2415 : UB 7 3 1 25 :=
  Data.w_K7_3_1
-- witness explícito
theorem u2416 : UB 7 4 2 19 :=
  Data.w_K7_4_2
-- witness explícito
theorem u2417 : UB 8 3 1 32 :=
  Data.w_K8_3_1
-- witness explícito
theorem u2418 : UB 8 4 2 23 :=
  Data.w_K8_4_2
-- witness explícito
theorem u2419 : UB 9 3 1 41 :=
  Data.w_K9_3_1
-- witness explícito
theorem u2420 : UB 9 4 2 27 :=
  Data.w_K9_4_2
-- coordenada muda (t = 1) de K2(3,1) ≤ 2
theorem u2421 : UB 2 4 1 4 :=
  (UB.lengthen_dummy 1 u10).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(7,3) ≤ 2
theorem u2422 : UB 2 8 3 4 :=
  (UB.lengthen_dummy 1 u48).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(9,4) ≤ 2
theorem u2426 : UB 2 10 4 4 :=
  (UB.lengthen_dummy 1 u76).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(11,5) ≤ 2
theorem u2433 : UB 2 12 5 4 :=
  (UB.lengthen_dummy 1 u110).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(13,6) ≤ 2
theorem u2444 : UB 2 14 6 4 :=
  (UB.lengthen_dummy 1 u150).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(15,7) ≤ 2
theorem u2457 : UB 2 16 7 4 :=
  (UB.lengthen_dummy 1 u196).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(17,8) ≤ 2
theorem u2472 : UB 2 18 8 4 :=
  (UB.lengthen_dummy 1 u248).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(19,9) ≤ 2
theorem u2489 : UB 2 20 9 4 :=
  (UB.lengthen_dummy 1 u306).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K2(21,10) ≤ 2
theorem u2508 : UB 2 22 10 4 :=
  (UB.lengthen_dummy 1 u370).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K3(4,1) ≤ 9
theorem u2649 : UB 3 5 1 27 :=
  (UB.lengthen_dummy 1 u2404).weaken (by decide) (by decide) (by decide)
-- soma direta de K3(4,1) ≤ 9 e K3(4,1) ≤ 9
theorem u2655 : UB 3 8 2 81 :=
  (UB.direct_sum u2404 u2404).weaken (by decide) (by decide) (by decide)
-- soma direta de K3(4,1) ≤ 9 e K3(4,2) ≤ 3
theorem u2656 : UB 3 8 3 27 :=
  (UB.direct_sum u2404 u932).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K3(7,4) ≤ 3
theorem u2657 : UB 3 8 4 9 :=
  (UB.lengthen_dummy 1 u961).weaken (by decide) (by decide) (by decide)
-- soma direta de K3(4,1) ≤ 9 e K3(7,4) ≤ 3
theorem u2672 : UB 3 11 5 27 :=
  (UB.direct_sum u2404 u961).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K3(10,6) ≤ 3
theorem u2673 : UB 3 11 6 9 :=
  (UB.lengthen_dummy 1 u1002).weaken (by decide) (by decide) (by decide)
-- soma direta de K3(4,1) ≤ 9 e K3(10,6) ≤ 3
theorem u2694 : UB 3 14 7 27 :=
  (UB.direct_sum u2404 u1002).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K3(13,8) ≤ 3
theorem u2695 : UB 3 14 8 9 :=
  (UB.lengthen_dummy 1 u1055).weaken (by decide) (by decide) (by decide)
-- coordenada muda (t = 1) de K4(9,6) ≤ 4
theorem u2720 : UB 4 10 6 16 :=
  (UB.lengthen_dummy 1 u1157).weaken (by decide) (by decide) (by decide)
-- alongamento livre (t = 1) de K9(4,2) ≤ 27
theorem u2860 : UB 9 5 3 27 :=
  (UB.lengthen_free 1 u2420).weaken (by decide) (by decide) (by decide)
-- soma direta de K9(4,2) ≤ 27 e K9(4,2) ≤ 27
theorem u2873 : UB 9 8 4 729 :=
  (UB.direct_sum u2420 u2420).weaken (by decide) (by decide) (by decide)
-- soma direta de K10(4,2) ≤ 34 e K10(4,2) ≤ 34
theorem u2906 : UB 10 8 4 1156 :=
  (UB.direct_sum u2380 u2380).weaken (by decide) (by decide) (by decide)
-- soma direta de K11(4,2) ≤ 41 e K11(4,2) ≤ 41
theorem u2940 : UB 11 8 4 1681 :=
  (UB.direct_sum u2382 u2382).weaken (by decide) (by decide) (by decide)
-- soma direta de K12(3,1) ≤ 72 e K12(4,2) ≤ 48
theorem u2953 : UB 12 7 3 3456 :=
  (UB.direct_sum u2383 u2384).weaken (by decide) (by decide) (by decide)
-- soma direta de K12(4,2) ≤ 48 e K12(4,2) ≤ 48
theorem u2959 : UB 12 8 4 2304 :=
  (UB.direct_sum u2384 u2384).weaken (by decide) (by decide) (by decide)

theorem K2_1_1_le_1 : K 2 1 1 ≤ 1 := K_le u2
theorem K2_2_1_le_2 : K 2 2 1 ≤ 2 := K_le u5
theorem K2_2_2_le_1 : K 2 2 2 ≤ 1 := K_le u7
theorem K2_3_1_le_2 : K 2 3 1 ≤ 2 := K_le u10
theorem K2_3_2_le_2 : K 2 3 2 ≤ 2 := K_le u12
theorem K2_3_3_le_1 : K 2 3 3 ≤ 1 := K_le u14
theorem K2_4_1_le_4 : K 2 4 1 ≤ 4 := K_le u2421
theorem K2_4_2_le_2 : K 2 4 2 ≤ 2 := K_le u18
theorem K2_4_3_le_2 : K 2 4 3 ≤ 2 := K_le u20
theorem K2_4_4_le_1 : K 2 4 4 ≤ 1 := K_le u22
theorem K2_5_1_le_7 : K 2 5 1 ≤ 7 := K_le u2394
theorem K2_5_2_le_2 : K 2 5 2 ≤ 2 := K_le u26
theorem K2_5_3_le_2 : K 2 5 3 ≤ 2 := K_le u28
theorem K2_5_4_le_2 : K 2 5 4 ≤ 2 := K_le u30
theorem K2_5_5_le_1 : K 2 5 5 ≤ 1 := K_le u32
theorem K2_6_1_le_12 : K 2 6 1 ≤ 12 := K_le u2395
theorem K2_6_2_le_4 : K 2 6 2 ≤ 4 := K_le u2396
theorem K2_6_3_le_2 : K 2 6 3 ≤ 2 := K_le u37
theorem K2_6_4_le_2 : K 2 6 4 ≤ 2 := K_le u39
theorem K2_6_5_le_2 : K 2 6 5 ≤ 2 := K_le u41
theorem K2_6_6_le_1 : K 2 6 6 ≤ 1 := K_le u43
theorem K2_7_1_le_16 : K 2 7 1 ≤ 16 := K_le u2397
theorem K2_7_2_le_7 : K 2 7 2 ≤ 7 := K_le u2398
theorem K2_7_3_le_2 : K 2 7 3 ≤ 2 := K_le u48
theorem K2_7_4_le_2 : K 2 7 4 ≤ 2 := K_le u50
theorem K2_7_5_le_2 : K 2 7 5 ≤ 2 := K_le u52
theorem K2_7_6_le_2 : K 2 7 6 ≤ 2 := K_le u54
theorem K2_7_7_le_1 : K 2 7 7 ≤ 1 := K_le u56
theorem K2_8_1_le_32 : K 2 8 1 ≤ 32 := K_le u2399
theorem K2_8_2_le_12 : K 2 8 2 ≤ 12 := K_le u2400
theorem K2_8_3_le_4 : K 2 8 3 ≤ 4 := K_le u2422
theorem K2_8_4_le_2 : K 2 8 4 ≤ 2 := K_le u62
theorem K2_8_5_le_2 : K 2 8 5 ≤ 2 := K_le u64
theorem K2_8_6_le_2 : K 2 8 6 ≤ 2 := K_le u66
theorem K2_8_7_le_2 : K 2 8 7 ≤ 2 := K_le u68
theorem K2_8_8_le_1 : K 2 8 8 ≤ 1 := K_le u70
theorem K2_9_2_le_16 : K 2 9 2 ≤ 16 := K_le u2401
theorem K2_9_3_le_7 : K 2 9 3 ≤ 7 := K_le u2402
theorem K2_9_4_le_2 : K 2 9 4 ≤ 2 := K_le u76
theorem K2_9_5_le_2 : K 2 9 5 ≤ 2 := K_le u78
theorem K2_9_6_le_2 : K 2 9 6 ≤ 2 := K_le u80
theorem K2_9_7_le_2 : K 2 9 7 ≤ 2 := K_le u82
theorem K2_9_8_le_2 : K 2 9 8 ≤ 2 := K_le u84
theorem K2_9_9_le_1 : K 2 9 9 ≤ 1 := K_le u86
theorem K2_10_3_le_12 : K 2 10 3 ≤ 12 := K_le u2391
theorem K2_10_4_le_4 : K 2 10 4 ≤ 4 := K_le u2426
theorem K2_10_5_le_2 : K 2 10 5 ≤ 2 := K_le u93
theorem K2_10_6_le_2 : K 2 10 6 ≤ 2 := K_le u95
theorem K2_10_7_le_2 : K 2 10 7 ≤ 2 := K_le u97
theorem K2_10_8_le_2 : K 2 10 8 ≤ 2 := K_le u99
theorem K2_10_9_le_2 : K 2 10 9 ≤ 2 := K_le u101
theorem K2_10_10_le_1 : K 2 10 10 ≤ 1 := K_le u103
theorem K2_11_1_le_192 : K 2 11 1 ≤ 192 := K_le u2392
theorem K2_11_3_le_16 : K 2 11 3 ≤ 16 := K_le u2393
theorem K2_11_5_le_2 : K 2 11 5 ≤ 2 := K_le u110
theorem K2_11_6_le_2 : K 2 11 6 ≤ 2 := K_le u112
theorem K2_11_7_le_2 : K 2 11 7 ≤ 2 := K_le u114
theorem K2_11_8_le_2 : K 2 11 8 ≤ 2 := K_le u116
theorem K2_11_9_le_2 : K 2 11 9 ≤ 2 := K_le u118
theorem K2_11_10_le_2 : K 2 11 10 ≤ 2 := K_le u120
theorem K2_12_5_le_4 : K 2 12 5 ≤ 4 := K_le u2433
theorem K2_12_6_le_2 : K 2 12 6 ≤ 2 := K_le u130
theorem K2_12_7_le_2 : K 2 12 7 ≤ 2 := K_le u132
theorem K2_12_8_le_2 : K 2 12 8 ≤ 2 := K_le u134
theorem K2_12_9_le_2 : K 2 12 9 ≤ 2 := K_le u136
theorem K2_12_10_le_2 : K 2 12 10 ≤ 2 := K_le u138
theorem K2_13_6_le_2 : K 2 13 6 ≤ 2 := K_le u150
theorem K2_13_7_le_2 : K 2 13 7 ≤ 2 := K_le u152
theorem K2_13_8_le_2 : K 2 13 8 ≤ 2 := K_le u154
theorem K2_13_9_le_2 : K 2 13 9 ≤ 2 := K_le u156
theorem K2_13_10_le_2 : K 2 13 10 ≤ 2 := K_le u158
theorem K2_14_6_le_4 : K 2 14 6 ≤ 4 := K_le u2444
theorem K2_14_7_le_2 : K 2 14 7 ≤ 2 := K_le u173
theorem K2_14_8_le_2 : K 2 14 8 ≤ 2 := K_le u175
theorem K2_14_9_le_2 : K 2 14 9 ≤ 2 := K_le u177
theorem K2_14_10_le_2 : K 2 14 10 ≤ 2 := K_le u179
theorem K2_15_7_le_2 : K 2 15 7 ≤ 2 := K_le u196
theorem K2_15_8_le_2 : K 2 15 8 ≤ 2 := K_le u198
theorem K2_15_9_le_2 : K 2 15 9 ≤ 2 := K_le u200
theorem K2_15_10_le_2 : K 2 15 10 ≤ 2 := K_le u202
theorem K2_16_7_le_4 : K 2 16 7 ≤ 4 := K_le u2457
theorem K2_16_8_le_2 : K 2 16 8 ≤ 2 := K_le u222
theorem K2_16_9_le_2 : K 2 16 9 ≤ 2 := K_le u224
theorem K2_16_10_le_2 : K 2 16 10 ≤ 2 := K_le u226
theorem K2_17_8_le_2 : K 2 17 8 ≤ 2 := K_le u248
theorem K2_17_9_le_2 : K 2 17 9 ≤ 2 := K_le u250
theorem K2_17_10_le_2 : K 2 17 10 ≤ 2 := K_le u252
theorem K2_18_8_le_4 : K 2 18 8 ≤ 4 := K_le u2472
theorem K2_18_9_le_2 : K 2 18 9 ≤ 2 := K_le u277
theorem K2_18_10_le_2 : K 2 18 10 ≤ 2 := K_le u279
theorem K2_19_9_le_2 : K 2 19 9 ≤ 2 := K_le u306
theorem K2_19_10_le_2 : K 2 19 10 ≤ 2 := K_le u308
theorem K2_20_9_le_4 : K 2 20 9 ≤ 4 := K_le u2489
theorem K2_20_10_le_2 : K 2 20 10 ≤ 2 := K_le u338
theorem K2_21_10_le_2 : K 2 21 10 ≤ 2 := K_le u370
theorem K2_22_10_le_4 : K 2 22 10 ≤ 4 := K_le u2508
theorem K3_1_1_le_1 : K 3 1 1 ≤ 1 := K_le u917
theorem K3_2_1_le_3 : K 3 2 1 ≤ 3 := K_le u920
theorem K3_2_2_le_1 : K 3 2 2 ≤ 1 := K_le u922
theorem K3_3_1_le_5 : K 3 3 1 ≤ 5 := K_le u2403
theorem K3_3_2_le_3 : K 3 3 2 ≤ 3 := K_le u926
theorem K3_3_3_le_1 : K 3 3 3 ≤ 1 := K_le u928
theorem K3_4_1_le_9 : K 3 4 1 ≤ 9 := K_le u2404
theorem K3_4_2_le_3 : K 3 4 2 ≤ 3 := K_le u932
theorem K3_4_3_le_3 : K 3 4 3 ≤ 3 := K_le u934
theorem K3_4_4_le_1 : K 3 4 4 ≤ 1 := K_le u936
theorem K3_5_1_le_27 : K 3 5 1 ≤ 27 := K_le u2649
theorem K3_5_2_le_8 : K 3 5 2 ≤ 8 := K_le u2405
theorem K3_5_3_le_3 : K 3 5 3 ≤ 3 := K_le u941
theorem K3_5_4_le_3 : K 3 5 4 ≤ 3 := K_le u943
theorem K3_5_5_le_1 : K 3 5 5 ≤ 1 := K_le u945
theorem K3_6_2_le_17 : K 3 6 2 ≤ 17 := K_le u2406
theorem K3_6_3_le_6 : K 3 6 3 ≤ 6 := K_le u2407
theorem K3_6_4_le_3 : K 3 6 4 ≤ 3 := K_le u951
theorem K3_6_5_le_3 : K 3 6 5 ≤ 3 := K_le u953
theorem K3_6_6_le_1 : K 3 6 6 ≤ 1 := K_le u955
theorem K3_7_4_le_3 : K 3 7 4 ≤ 3 := K_le u961
theorem K3_7_5_le_3 : K 3 7 5 ≤ 3 := K_le u963
theorem K3_7_6_le_3 : K 3 7 6 ≤ 3 := K_le u965
theorem K3_7_7_le_1 : K 3 7 7 ≤ 1 := K_le u967
theorem K3_8_2_le_81 : K 3 8 2 ≤ 81 := K_le u2655
theorem K3_8_3_le_27 : K 3 8 3 ≤ 27 := K_le u2656
theorem K3_8_4_le_9 : K 3 8 4 ≤ 9 := K_le u2657
theorem K3_8_5_le_3 : K 3 8 5 ≤ 3 := K_le u974
theorem K3_8_6_le_3 : K 3 8 6 ≤ 3 := K_le u976
theorem K3_8_7_le_3 : K 3 8 7 ≤ 3 := K_le u978
theorem K3_8_8_le_1 : K 3 8 8 ≤ 1 := K_le u980
theorem K3_9_6_le_3 : K 3 9 6 ≤ 3 := K_le u988
theorem K3_9_7_le_3 : K 3 9 7 ≤ 3 := K_le u990
theorem K3_9_8_le_3 : K 3 9 8 ≤ 3 := K_le u992
theorem K3_10_6_le_3 : K 3 10 6 ≤ 3 := K_le u1002
theorem K3_10_7_le_3 : K 3 10 7 ≤ 3 := K_le u1004
theorem K3_10_8_le_3 : K 3 10 8 ≤ 3 := K_le u1006
theorem K3_11_5_le_27 : K 3 11 5 ≤ 27 := K_le u2672
theorem K3_11_6_le_9 : K 3 11 6 ≤ 9 := K_le u2673
theorem K3_11_7_le_3 : K 3 11 7 ≤ 3 := K_le u1019
theorem K3_11_8_le_3 : K 3 11 8 ≤ 3 := K_le u1021
theorem K3_12_8_le_3 : K 3 12 8 ≤ 3 := K_le u1037
theorem K3_13_8_le_3 : K 3 13 8 ≤ 3 := K_le u1055
theorem K3_14_7_le_27 : K 3 14 7 ≤ 27 := K_le u2694
theorem K3_14_8_le_9 : K 3 14 8 ≤ 9 := K_le u2695
theorem K4_1_1_le_1 : K 4 1 1 ≤ 1 := K_le u1089
theorem K4_2_1_le_4 : K 4 2 1 ≤ 4 := K_le u1092
theorem K4_2_2_le_1 : K 4 2 2 ≤ 1 := K_le u1094
theorem K4_3_1_le_8 : K 4 3 1 ≤ 8 := K_le u2408
theorem K4_3_2_le_4 : K 4 3 2 ≤ 4 := K_le u1098
theorem K4_3_3_le_1 : K 4 3 3 ≤ 1 := K_le u1100
theorem K4_4_1_le_24 : K 4 4 1 ≤ 24 := K_le u2409
theorem K4_4_2_le_7 : K 4 4 2 ≤ 7 := K_le u2410
theorem K4_4_3_le_4 : K 4 4 3 ≤ 4 := K_le u1105
theorem K4_4_4_le_1 : K 4 4 4 ≤ 1 := K_le u1107
theorem K4_5_3_le_4 : K 4 5 3 ≤ 4 := K_le u1112
theorem K4_5_4_le_4 : K 4 5 4 ≤ 4 := K_le u1114
theorem K4_5_5_le_1 : K 4 5 5 ≤ 1 := K_le u1116
theorem K4_6_4_le_4 : K 4 6 4 ≤ 4 := K_le u1122
theorem K4_6_5_le_4 : K 4 6 5 ≤ 4 := K_le u1124
theorem K4_6_6_le_1 : K 4 6 6 ≤ 1 := K_le u1126
theorem K4_7_5_le_4 : K 4 7 5 ≤ 4 := K_le u1133
theorem K4_7_6_le_4 : K 4 7 6 ≤ 4 := K_le u1135
theorem K4_7_7_le_1 : K 4 7 7 ≤ 1 := K_le u1137
theorem K4_8_6_le_4 : K 4 8 6 ≤ 4 := K_le u1145
theorem K4_8_7_le_4 : K 4 8 7 ≤ 4 := K_le u1147
theorem K4_8_8_le_1 : K 4 8 8 ≤ 1 := K_le u1149
theorem K4_9_6_le_4 : K 4 9 6 ≤ 4 := K_le u1157
theorem K4_9_7_le_4 : K 4 9 7 ≤ 4 := K_le u1159
theorem K4_9_8_le_4 : K 4 9 8 ≤ 4 := K_le u1161
theorem K4_10_6_le_16 : K 4 10 6 ≤ 16 := K_le u2720
theorem K4_10_7_le_4 : K 4 10 7 ≤ 4 := K_le u1172
theorem K4_10_8_le_4 : K 4 10 8 ≤ 4 := K_le u1174
theorem K4_11_8_le_4 : K 4 11 8 ≤ 4 := K_le u1188
theorem K5_1_1_le_1 : K 5 1 1 ≤ 1 := K_le u1197
theorem K5_2_1_le_5 : K 5 2 1 ≤ 5 := K_le u1200
theorem K5_2_2_le_1 : K 5 2 2 ≤ 1 := K_le u1202
theorem K5_3_1_le_13 : K 5 3 1 ≤ 13 := K_le u2411
theorem K5_3_2_le_5 : K 5 3 2 ≤ 5 := K_le u1206
theorem K5_3_3_le_1 : K 5 3 3 ≤ 1 := K_le u1208
theorem K5_4_2_le_11 : K 5 4 2 ≤ 11 := K_le u2412
theorem K5_4_3_le_5 : K 5 4 3 ≤ 5 := K_le u1213
theorem K5_4_4_le_1 : K 5 4 4 ≤ 1 := K_le u1215
theorem K5_5_4_le_5 : K 5 5 4 ≤ 5 := K_le u1221
theorem K5_5_5_le_1 : K 5 5 5 ≤ 1 := K_le u1223
theorem K5_6_4_le_5 : K 5 6 4 ≤ 5 := K_le u1229
theorem K5_6_5_le_5 : K 5 6 5 ≤ 5 := K_le u1231
theorem K5_6_6_le_1 : K 5 6 6 ≤ 1 := K_le u1233
theorem K5_7_5_le_5 : K 5 7 5 ≤ 5 := K_le u1240
theorem K5_7_6_le_5 : K 5 7 6 ≤ 5 := K_le u1242
theorem K5_7_7_le_1 : K 5 7 7 ≤ 1 := K_le u1244
theorem K5_8_6_le_5 : K 5 8 6 ≤ 5 := K_le u1252
theorem K5_8_7_le_5 : K 5 8 7 ≤ 5 := K_le u1254
theorem K5_8_8_le_1 : K 5 8 8 ≤ 1 := K_le u1256
theorem K5_9_7_le_5 : K 5 9 7 ≤ 5 := K_le u1265
theorem K5_9_8_le_5 : K 5 9 8 ≤ 5 := K_le u1267
theorem K5_10_8_le_5 : K 5 10 8 ≤ 5 := K_le u1279
theorem K5_11_8_le_5 : K 5 11 8 ≤ 5 := K_le u1293
theorem K6_1_1_le_1 : K 6 1 1 ≤ 1 := K_le u1302
theorem K6_2_1_le_6 : K 6 2 1 ≤ 6 := K_le u1305
theorem K6_2_2_le_1 : K 6 2 2 ≤ 1 := K_le u1307
theorem K6_3_1_le_18 : K 6 3 1 ≤ 18 := K_le u2413
theorem K6_3_2_le_6 : K 6 3 2 ≤ 6 := K_le u1311
theorem K6_3_3_le_1 : K 6 3 3 ≤ 1 := K_le u1313
theorem K6_4_2_le_15 : K 6 4 2 ≤ 15 := K_le u2414
theorem K6_4_3_le_6 : K 6 4 3 ≤ 6 := K_le u1318
theorem K6_4_4_le_1 : K 6 4 4 ≤ 1 := K_le u1320
theorem K6_5_4_le_6 : K 6 5 4 ≤ 6 := K_le u1326
theorem K6_5_5_le_1 : K 6 5 5 ≤ 1 := K_le u1328
theorem K6_6_5_le_6 : K 6 6 5 ≤ 6 := K_le u1335
theorem K6_6_6_le_1 : K 6 6 6 ≤ 1 := K_le u1337
theorem K6_7_5_le_6 : K 6 7 5 ≤ 6 := K_le u1344
theorem K6_7_6_le_6 : K 6 7 6 ≤ 6 := K_le u1346
theorem K6_7_7_le_1 : K 6 7 7 ≤ 1 := K_le u1348
theorem K6_8_6_le_6 : K 6 8 6 ≤ 6 := K_le u1356
theorem K6_8_7_le_6 : K 6 8 7 ≤ 6 := K_le u1358
theorem K6_8_8_le_1 : K 6 8 8 ≤ 1 := K_le u1360
theorem K6_9_7_le_6 : K 6 9 7 ≤ 6 := K_le u1369
theorem K6_9_8_le_6 : K 6 9 8 ≤ 6 := K_le u1371
theorem K6_10_8_le_6 : K 6 10 8 ≤ 6 := K_le u1383
theorem K7_1_1_le_1 : K 7 1 1 ≤ 1 := K_le u1390
theorem K7_2_1_le_7 : K 7 2 1 ≤ 7 := K_le u1393
theorem K7_2_2_le_1 : K 7 2 2 ≤ 1 := K_le u1395
theorem K7_3_1_le_25 : K 7 3 1 ≤ 25 := K_le u2415
theorem K7_3_2_le_7 : K 7 3 2 ≤ 7 := K_le u1399
theorem K7_3_3_le_1 : K 7 3 3 ≤ 1 := K_le u1401
theorem K7_4_2_le_19 : K 7 4 2 ≤ 19 := K_le u2416
theorem K7_4_3_le_7 : K 7 4 3 ≤ 7 := K_le u1406
theorem K7_4_4_le_1 : K 7 4 4 ≤ 1 := K_le u1408
theorem K7_5_4_le_7 : K 7 5 4 ≤ 7 := K_le u1414
theorem K7_5_5_le_1 : K 7 5 5 ≤ 1 := K_le u1416
theorem K7_6_5_le_7 : K 7 6 5 ≤ 7 := K_le u1423
theorem K7_6_6_le_1 : K 7 6 6 ≤ 1 := K_le u1425
theorem K7_7_6_le_7 : K 7 7 6 ≤ 7 := K_le u1433
theorem K7_7_7_le_1 : K 7 7 7 ≤ 1 := K_le u1435
theorem K7_8_6_le_7 : K 7 8 6 ≤ 7 := K_le u1443
theorem K7_8_7_le_7 : K 7 8 7 ≤ 7 := K_le u1445
theorem K7_8_8_le_1 : K 7 8 8 ≤ 1 := K_le u1447
theorem K7_9_7_le_7 : K 7 9 7 ≤ 7 := K_le u1456
theorem K7_9_8_le_7 : K 7 9 8 ≤ 7 := K_le u1458
theorem K7_10_8_le_7 : K 7 10 8 ≤ 7 := K_le u1470
theorem K8_1_1_le_1 : K 8 1 1 ≤ 1 := K_le u1477
theorem K8_2_1_le_8 : K 8 2 1 ≤ 8 := K_le u1480
theorem K8_2_2_le_1 : K 8 2 2 ≤ 1 := K_le u1482
theorem K8_3_1_le_32 : K 8 3 1 ≤ 32 := K_le u2417
theorem K8_3_2_le_8 : K 8 3 2 ≤ 8 := K_le u1486
theorem K8_3_3_le_1 : K 8 3 3 ≤ 1 := K_le u1488
theorem K8_4_2_le_23 : K 8 4 2 ≤ 23 := K_le u2418
theorem K8_4_3_le_8 : K 8 4 3 ≤ 8 := K_le u1493
theorem K8_4_4_le_1 : K 8 4 4 ≤ 1 := K_le u1495
theorem K8_5_4_le_8 : K 8 5 4 ≤ 8 := K_le u1501
theorem K8_5_5_le_1 : K 8 5 5 ≤ 1 := K_le u1503
theorem K8_6_5_le_8 : K 8 6 5 ≤ 8 := K_le u1510
theorem K8_6_6_le_1 : K 8 6 6 ≤ 1 := K_le u1512
theorem K8_7_6_le_8 : K 8 7 6 ≤ 8 := K_le u1520
theorem K8_7_7_le_1 : K 8 7 7 ≤ 1 := K_le u1522
theorem K8_8_7_le_8 : K 8 8 7 ≤ 8 := K_le u1531
theorem K8_8_8_le_1 : K 8 8 8 ≤ 1 := K_le u1533
theorem K8_9_7_le_8 : K 8 9 7 ≤ 8 := K_le u1542
theorem K8_9_8_le_8 : K 8 9 8 ≤ 8 := K_le u1544
theorem K8_10_8_le_8 : K 8 10 8 ≤ 8 := K_le u1556
theorem K9_1_1_le_1 : K 9 1 1 ≤ 1 := K_le u1563
theorem K9_2_1_le_9 : K 9 2 1 ≤ 9 := K_le u1566
theorem K9_2_2_le_1 : K 9 2 2 ≤ 1 := K_le u1568
theorem K9_3_1_le_41 : K 9 3 1 ≤ 41 := K_le u2419
theorem K9_3_2_le_9 : K 9 3 2 ≤ 9 := K_le u1572
theorem K9_3_3_le_1 : K 9 3 3 ≤ 1 := K_le u1574
theorem K9_4_2_le_27 : K 9 4 2 ≤ 27 := K_le u2420
theorem K9_4_3_le_9 : K 9 4 3 ≤ 9 := K_le u1579
theorem K9_4_4_le_1 : K 9 4 4 ≤ 1 := K_le u1581
theorem K9_5_3_le_27 : K 9 5 3 ≤ 27 := K_le u2860
theorem K9_5_4_le_9 : K 9 5 4 ≤ 9 := K_le u1587
theorem K9_5_5_le_1 : K 9 5 5 ≤ 1 := K_le u1589
theorem K9_6_5_le_9 : K 9 6 5 ≤ 9 := K_le u1596
theorem K9_6_6_le_1 : K 9 6 6 ≤ 1 := K_le u1598
theorem K9_7_6_le_9 : K 9 7 6 ≤ 9 := K_le u1606
theorem K9_7_7_le_1 : K 9 7 7 ≤ 1 := K_le u1608
theorem K9_8_4_le_729 : K 9 8 4 ≤ 729 := K_le u2873
theorem K9_8_7_le_9 : K 9 8 7 ≤ 9 := K_le u1617
theorem K9_8_8_le_1 : K 9 8 8 ≤ 1 := K_le u1619
theorem K9_9_8_le_9 : K 9 9 8 ≤ 9 := K_le u1629
theorem K9_10_8_le_9 : K 9 10 8 ≤ 9 := K_le u1641
theorem K10_1_1_le_1 : K 10 1 1 ≤ 1 := K_le u1648
theorem K10_2_1_le_10 : K 10 2 1 ≤ 10 := K_le u1651
theorem K10_2_2_le_1 : K 10 2 2 ≤ 1 := K_le u1653
theorem K10_3_1_le_50 : K 10 3 1 ≤ 50 := K_le u2379
theorem K10_3_2_le_10 : K 10 3 2 ≤ 10 := K_le u1657
theorem K10_3_3_le_1 : K 10 3 3 ≤ 1 := K_le u1659
theorem K10_4_2_le_34 : K 10 4 2 ≤ 34 := K_le u2380
theorem K10_4_3_le_10 : K 10 4 3 ≤ 10 := K_le u1664
theorem K10_4_4_le_1 : K 10 4 4 ≤ 1 := K_le u1666
theorem K10_5_4_le_10 : K 10 5 4 ≤ 10 := K_le u1672
theorem K10_5_5_le_1 : K 10 5 5 ≤ 1 := K_le u1674
theorem K10_6_5_le_10 : K 10 6 5 ≤ 10 := K_le u1681
theorem K10_6_6_le_1 : K 10 6 6 ≤ 1 := K_le u1683
theorem K10_7_6_le_10 : K 10 7 6 ≤ 10 := K_le u1691
theorem K10_7_7_le_1 : K 10 7 7 ≤ 1 := K_le u1693
theorem K10_8_4_le_1156 : K 10 8 4 ≤ 1156 := K_le u2906
theorem K10_8_7_le_10 : K 10 8 7 ≤ 10 := K_le u1702
theorem K10_8_8_le_1 : K 10 8 8 ≤ 1 := K_le u1704
theorem K10_9_8_le_10 : K 10 9 8 ≤ 10 := K_le u1714
theorem K11_1_1_le_1 : K 11 1 1 ≤ 1 := K_le u1732
theorem K11_2_1_le_11 : K 11 2 1 ≤ 11 := K_le u1735
theorem K11_2_2_le_1 : K 11 2 2 ≤ 1 := K_le u1737
theorem K11_3_1_le_61 : K 11 3 1 ≤ 61 := K_le u2381
theorem K11_3_2_le_11 : K 11 3 2 ≤ 11 := K_le u1741
theorem K11_3_3_le_1 : K 11 3 3 ≤ 1 := K_le u1743
theorem K11_4_2_le_41 : K 11 4 2 ≤ 41 := K_le u2382
theorem K11_4_3_le_11 : K 11 4 3 ≤ 11 := K_le u1748
theorem K11_4_4_le_1 : K 11 4 4 ≤ 1 := K_le u1750
theorem K11_5_4_le_11 : K 11 5 4 ≤ 11 := K_le u1756
theorem K11_5_5_le_1 : K 11 5 5 ≤ 1 := K_le u1758
theorem K11_6_5_le_11 : K 11 6 5 ≤ 11 := K_le u1765
theorem K11_6_6_le_1 : K 11 6 6 ≤ 1 := K_le u1767
theorem K11_7_6_le_11 : K 11 7 6 ≤ 11 := K_le u1775
theorem K11_7_7_le_1 : K 11 7 7 ≤ 1 := K_le u1777
theorem K11_8_4_le_1681 : K 11 8 4 ≤ 1681 := K_le u2940
theorem K11_8_7_le_11 : K 11 8 7 ≤ 11 := K_le u1786
theorem K11_8_8_le_1 : K 11 8 8 ≤ 1 := K_le u1788
theorem K12_1_1_le_1 : K 12 1 1 ≤ 1 := K_le u1791
theorem K12_2_1_le_12 : K 12 2 1 ≤ 12 := K_le u1794
theorem K12_2_2_le_1 : K 12 2 2 ≤ 1 := K_le u1796
theorem K12_3_1_le_72 : K 12 3 1 ≤ 72 := K_le u2383
theorem K12_3_2_le_12 : K 12 3 2 ≤ 12 := K_le u1800
theorem K12_3_3_le_1 : K 12 3 3 ≤ 1 := K_le u1802
theorem K12_4_2_le_48 : K 12 4 2 ≤ 48 := K_le u2384
theorem K12_4_3_le_12 : K 12 4 3 ≤ 12 := K_le u1807
theorem K12_4_4_le_1 : K 12 4 4 ≤ 1 := K_le u1809
theorem K12_5_4_le_12 : K 12 5 4 ≤ 12 := K_le u1815
theorem K12_5_5_le_1 : K 12 5 5 ≤ 1 := K_le u1817
theorem K12_6_5_le_12 : K 12 6 5 ≤ 12 := K_le u1824
theorem K12_6_6_le_1 : K 12 6 6 ≤ 1 := K_le u1826
theorem K12_7_3_le_3456 : K 12 7 3 ≤ 3456 := K_le u2953
theorem K12_7_6_le_12 : K 12 7 6 ≤ 12 := K_le u1834
theorem K12_7_7_le_1 : K 12 7 7 ≤ 1 := K_le u1836
theorem K12_8_4_le_2304 : K 12 8 4 ≤ 2304 := K_le u2959
theorem K12_8_7_le_12 : K 12 8 7 ≤ 12 := K_le u1845
theorem K12_8_8_le_1 : K 12 8 8 ≤ 1 := K_le u1847
theorem K13_1_1_le_1 : K 13 1 1 ≤ 1 := K_le u1850
theorem K13_2_1_le_13 : K 13 2 1 ≤ 13 := K_le u1853
theorem K13_2_2_le_1 : K 13 2 2 ≤ 1 := K_le u1855
theorem K13_3_1_le_85 : K 13 3 1 ≤ 85 := K_le u2385
theorem K13_3_2_le_13 : K 13 3 2 ≤ 13 := K_le u1859
theorem K13_3_3_le_1 : K 13 3 3 ≤ 1 := K_le u1861
theorem K13_4_3_le_13 : K 13 4 3 ≤ 13 := K_le u1866
theorem K13_4_4_le_1 : K 13 4 4 ≤ 1 := K_le u1868
theorem K13_5_4_le_13 : K 13 5 4 ≤ 13 := K_le u1874
theorem K13_5_5_le_1 : K 13 5 5 ≤ 1 := K_le u1876
theorem K13_6_5_le_13 : K 13 6 5 ≤ 13 := K_le u1883
theorem K13_6_6_le_1 : K 13 6 6 ≤ 1 := K_le u1885
theorem K13_7_6_le_13 : K 13 7 6 ≤ 13 := K_le u1893
theorem K13_7_7_le_1 : K 13 7 7 ≤ 1 := K_le u1895
theorem K13_8_7_le_13 : K 13 8 7 ≤ 13 := K_le u1904
theorem K13_8_8_le_1 : K 13 8 8 ≤ 1 := K_le u1906
theorem K14_1_1_le_1 : K 14 1 1 ≤ 1 := K_le u1909
theorem K14_2_1_le_14 : K 14 2 1 ≤ 14 := K_le u1912
theorem K14_2_2_le_1 : K 14 2 2 ≤ 1 := K_le u1914
theorem K14_3_1_le_98 : K 14 3 1 ≤ 98 := K_le u2386
theorem K14_3_2_le_14 : K 14 3 2 ≤ 14 := K_le u1918
theorem K14_3_3_le_1 : K 14 3 3 ≤ 1 := K_le u1920
theorem K14_4_3_le_14 : K 14 4 3 ≤ 14 := K_le u1925
theorem K14_4_4_le_1 : K 14 4 4 ≤ 1 := K_le u1927
theorem K14_5_4_le_14 : K 14 5 4 ≤ 14 := K_le u1933
theorem K14_5_5_le_1 : K 14 5 5 ≤ 1 := K_le u1935
theorem K14_6_5_le_14 : K 14 6 5 ≤ 14 := K_le u1942
theorem K14_6_6_le_1 : K 14 6 6 ≤ 1 := K_le u1944
theorem K14_7_6_le_14 : K 14 7 6 ≤ 14 := K_le u1952
theorem K14_7_7_le_1 : K 14 7 7 ≤ 1 := K_le u1954
theorem K14_8_7_le_14 : K 14 8 7 ≤ 14 := K_le u1963
theorem K14_8_8_le_1 : K 14 8 8 ≤ 1 := K_le u1965
theorem K15_1_1_le_1 : K 15 1 1 ≤ 1 := K_le u1968
theorem K15_2_1_le_15 : K 15 2 1 ≤ 15 := K_le u1971
theorem K15_2_2_le_1 : K 15 2 2 ≤ 1 := K_le u1973
theorem K15_3_1_le_113 : K 15 3 1 ≤ 113 := K_le u2387
theorem K15_3_2_le_15 : K 15 3 2 ≤ 15 := K_le u1977
theorem K15_3_3_le_1 : K 15 3 3 ≤ 1 := K_le u1979
theorem K15_4_3_le_15 : K 15 4 3 ≤ 15 := K_le u1984
theorem K15_4_4_le_1 : K 15 4 4 ≤ 1 := K_le u1986
theorem K15_5_4_le_15 : K 15 5 4 ≤ 15 := K_le u1992
theorem K15_5_5_le_1 : K 15 5 5 ≤ 1 := K_le u1994
theorem K15_6_5_le_15 : K 15 6 5 ≤ 15 := K_le u2001
theorem K15_6_6_le_1 : K 15 6 6 ≤ 1 := K_le u2003
theorem K15_7_6_le_15 : K 15 7 6 ≤ 15 := K_le u2011
theorem K15_7_7_le_1 : K 15 7 7 ≤ 1 := K_le u2013
theorem K15_8_7_le_15 : K 15 8 7 ≤ 15 := K_le u2022
theorem K15_8_8_le_1 : K 15 8 8 ≤ 1 := K_le u2024
theorem K16_1_1_le_1 : K 16 1 1 ≤ 1 := K_le u2027
theorem K16_2_1_le_16 : K 16 2 1 ≤ 16 := K_le u2030
theorem K16_2_2_le_1 : K 16 2 2 ≤ 1 := K_le u2032
theorem K16_3_1_le_128 : K 16 3 1 ≤ 128 := K_le u2388
theorem K16_3_2_le_16 : K 16 3 2 ≤ 16 := K_le u2036
theorem K16_3_3_le_1 : K 16 3 3 ≤ 1 := K_le u2038
theorem K16_4_3_le_16 : K 16 4 3 ≤ 16 := K_le u2043
theorem K16_4_4_le_1 : K 16 4 4 ≤ 1 := K_le u2045
theorem K16_5_4_le_16 : K 16 5 4 ≤ 16 := K_le u2051
theorem K16_5_5_le_1 : K 16 5 5 ≤ 1 := K_le u2053
theorem K16_6_5_le_16 : K 16 6 5 ≤ 16 := K_le u2060
theorem K16_6_6_le_1 : K 16 6 6 ≤ 1 := K_le u2062
theorem K16_7_6_le_16 : K 16 7 6 ≤ 16 := K_le u2070
theorem K16_7_7_le_1 : K 16 7 7 ≤ 1 := K_le u2072
theorem K16_8_7_le_16 : K 16 8 7 ≤ 16 := K_le u2081
theorem K16_8_8_le_1 : K 16 8 8 ≤ 1 := K_le u2083
theorem K17_1_1_le_1 : K 17 1 1 ≤ 1 := K_le u2086
theorem K17_2_1_le_17 : K 17 2 1 ≤ 17 := K_le u2089
theorem K17_2_2_le_1 : K 17 2 2 ≤ 1 := K_le u2091
theorem K17_3_1_le_145 : K 17 3 1 ≤ 145 := K_le u2389
theorem K17_3_2_le_17 : K 17 3 2 ≤ 17 := K_le u2095
theorem K17_3_3_le_1 : K 17 3 3 ≤ 1 := K_le u2097
theorem K17_4_3_le_17 : K 17 4 3 ≤ 17 := K_le u2102
theorem K17_4_4_le_1 : K 17 4 4 ≤ 1 := K_le u2104
theorem K17_5_4_le_17 : K 17 5 4 ≤ 17 := K_le u2110
theorem K17_5_5_le_1 : K 17 5 5 ≤ 1 := K_le u2112
theorem K17_6_5_le_17 : K 17 6 5 ≤ 17 := K_le u2119
theorem K17_6_6_le_1 : K 17 6 6 ≤ 1 := K_le u2121
theorem K17_7_6_le_17 : K 17 7 6 ≤ 17 := K_le u2129
theorem K17_7_7_le_1 : K 17 7 7 ≤ 1 := K_le u2131
theorem K17_8_7_le_17 : K 17 8 7 ≤ 17 := K_le u2140
theorem K17_8_8_le_1 : K 17 8 8 ≤ 1 := K_le u2142
theorem K18_1_1_le_1 : K 18 1 1 ≤ 1 := K_le u2145
theorem K18_2_1_le_18 : K 18 2 1 ≤ 18 := K_le u2148
theorem K18_2_2_le_1 : K 18 2 2 ≤ 1 := K_le u2150
theorem K18_3_1_le_162 : K 18 3 1 ≤ 162 := K_le u2390
theorem K18_3_2_le_18 : K 18 3 2 ≤ 18 := K_le u2154
theorem K18_3_3_le_1 : K 18 3 3 ≤ 1 := K_le u2156
theorem K18_4_3_le_18 : K 18 4 3 ≤ 18 := K_le u2161
theorem K18_4_4_le_1 : K 18 4 4 ≤ 1 := K_le u2163
theorem K18_5_4_le_18 : K 18 5 4 ≤ 18 := K_le u2169
theorem K18_5_5_le_1 : K 18 5 5 ≤ 1 := K_le u2171
theorem K18_6_5_le_18 : K 18 6 5 ≤ 18 := K_le u2178
theorem K18_6_6_le_1 : K 18 6 6 ≤ 1 := K_le u2180
theorem K18_7_6_le_18 : K 18 7 6 ≤ 18 := K_le u2188
theorem K18_7_7_le_1 : K 18 7 7 ≤ 1 := K_le u2190
theorem K18_8_7_le_18 : K 18 8 7 ≤ 18 := K_le u2199
theorem K18_8_8_le_1 : K 18 8 8 ≤ 1 := K_le u2201
theorem K19_1_1_le_1 : K 19 1 1 ≤ 1 := K_le u2204
theorem K19_2_1_le_19 : K 19 2 1 ≤ 19 := K_le u2207
theorem K19_2_2_le_1 : K 19 2 2 ≤ 1 := K_le u2209
theorem K19_3_2_le_19 : K 19 3 2 ≤ 19 := K_le u2213
theorem K19_3_3_le_1 : K 19 3 3 ≤ 1 := K_le u2215
theorem K19_4_3_le_19 : K 19 4 3 ≤ 19 := K_le u2220
theorem K19_4_4_le_1 : K 19 4 4 ≤ 1 := K_le u2222
theorem K19_5_4_le_19 : K 19 5 4 ≤ 19 := K_le u2228
theorem K19_5_5_le_1 : K 19 5 5 ≤ 1 := K_le u2230
theorem K19_6_5_le_19 : K 19 6 5 ≤ 19 := K_le u2237
theorem K19_6_6_le_1 : K 19 6 6 ≤ 1 := K_le u2239
theorem K19_7_6_le_19 : K 19 7 6 ≤ 19 := K_le u2247
theorem K19_7_7_le_1 : K 19 7 7 ≤ 1 := K_le u2249
theorem K19_8_7_le_19 : K 19 8 7 ≤ 19 := K_le u2258
theorem K19_8_8_le_1 : K 19 8 8 ≤ 1 := K_le u2260
theorem K20_1_1_le_1 : K 20 1 1 ≤ 1 := K_le u2263
theorem K20_2_1_le_20 : K 20 2 1 ≤ 20 := K_le u2266
theorem K20_2_2_le_1 : K 20 2 2 ≤ 1 := K_le u2268
theorem K20_3_2_le_20 : K 20 3 2 ≤ 20 := K_le u2272
theorem K20_3_3_le_1 : K 20 3 3 ≤ 1 := K_le u2274
theorem K20_4_3_le_20 : K 20 4 3 ≤ 20 := K_le u2279
theorem K20_4_4_le_1 : K 20 4 4 ≤ 1 := K_le u2281
theorem K20_5_4_le_20 : K 20 5 4 ≤ 20 := K_le u2287
theorem K20_5_5_le_1 : K 20 5 5 ≤ 1 := K_le u2289
theorem K20_6_5_le_20 : K 20 6 5 ≤ 20 := K_le u2296
theorem K20_6_6_le_1 : K 20 6 6 ≤ 1 := K_le u2298
theorem K20_7_6_le_20 : K 20 7 6 ≤ 20 := K_le u2306
theorem K20_7_7_le_1 : K 20 7 7 ≤ 1 := K_le u2308
theorem K20_8_7_le_20 : K 20 8 7 ≤ 20 := K_le u2317
theorem K20_8_8_le_1 : K 20 8 8 ≤ 1 := K_le u2319
theorem K21_1_1_le_1 : K 21 1 1 ≤ 1 := K_le u2322
theorem K21_2_1_le_21 : K 21 2 1 ≤ 21 := K_le u2325
theorem K21_2_2_le_1 : K 21 2 2 ≤ 1 := K_le u2327
theorem K21_3_2_le_21 : K 21 3 2 ≤ 21 := K_le u2331
theorem K21_3_3_le_1 : K 21 3 3 ≤ 1 := K_le u2333
theorem K21_4_3_le_21 : K 21 4 3 ≤ 21 := K_le u2338
theorem K21_4_4_le_1 : K 21 4 4 ≤ 1 := K_le u2340
theorem K21_5_4_le_21 : K 21 5 4 ≤ 21 := K_le u2346
theorem K21_5_5_le_1 : K 21 5 5 ≤ 1 := K_le u2348
theorem K21_6_5_le_21 : K 21 6 5 ≤ 21 := K_le u2355
theorem K21_6_6_le_1 : K 21 6 6 ≤ 1 := K_le u2357
theorem K21_7_6_le_21 : K 21 7 6 ≤ 21 := K_le u2365
theorem K21_7_7_le_1 : K 21 7 7 ≤ 1 := K_le u2367
theorem K21_8_7_le_21 : K 21 8 7 ≤ 21 := K_le u2376
theorem K21_8_8_le_1 : K 21 8 8 ≤ 1 := K_le u2378

set_option maxRecDepth 100000 in
theorem todas_as_cotas :
    K 2 1 1 ≤ 1 ∧
    K 2 2 1 ≤ 2 ∧
    K 2 2 2 ≤ 1 ∧
    K 2 3 1 ≤ 2 ∧
    K 2 3 2 ≤ 2 ∧
    K 2 3 3 ≤ 1 ∧
    K 2 4 1 ≤ 4 ∧
    K 2 4 2 ≤ 2 ∧
    K 2 4 3 ≤ 2 ∧
    K 2 4 4 ≤ 1 ∧
    K 2 5 1 ≤ 7 ∧
    K 2 5 2 ≤ 2 ∧
    K 2 5 3 ≤ 2 ∧
    K 2 5 4 ≤ 2 ∧
    K 2 5 5 ≤ 1 ∧
    K 2 6 1 ≤ 12 ∧
    K 2 6 2 ≤ 4 ∧
    K 2 6 3 ≤ 2 ∧
    K 2 6 4 ≤ 2 ∧
    K 2 6 5 ≤ 2 ∧
    K 2 6 6 ≤ 1 ∧
    K 2 7 1 ≤ 16 ∧
    K 2 7 2 ≤ 7 ∧
    K 2 7 3 ≤ 2 ∧
    K 2 7 4 ≤ 2 ∧
    K 2 7 5 ≤ 2 ∧
    K 2 7 6 ≤ 2 ∧
    K 2 7 7 ≤ 1 ∧
    K 2 8 1 ≤ 32 ∧
    K 2 8 2 ≤ 12 ∧
    K 2 8 3 ≤ 4 ∧
    K 2 8 4 ≤ 2 ∧
    K 2 8 5 ≤ 2 ∧
    K 2 8 6 ≤ 2 ∧
    K 2 8 7 ≤ 2 ∧
    K 2 8 8 ≤ 1 ∧
    K 2 9 2 ≤ 16 ∧
    K 2 9 3 ≤ 7 ∧
    K 2 9 4 ≤ 2 ∧
    K 2 9 5 ≤ 2 ∧
    K 2 9 6 ≤ 2 ∧
    K 2 9 7 ≤ 2 ∧
    K 2 9 8 ≤ 2 ∧
    K 2 9 9 ≤ 1 ∧
    K 2 10 3 ≤ 12 ∧
    K 2 10 4 ≤ 4 ∧
    K 2 10 5 ≤ 2 ∧
    K 2 10 6 ≤ 2 ∧
    K 2 10 7 ≤ 2 ∧
    K 2 10 8 ≤ 2 ∧
    K 2 10 9 ≤ 2 ∧
    K 2 10 10 ≤ 1 ∧
    K 2 11 1 ≤ 192 ∧
    K 2 11 3 ≤ 16 ∧
    K 2 11 5 ≤ 2 ∧
    K 2 11 6 ≤ 2 ∧
    K 2 11 7 ≤ 2 ∧
    K 2 11 8 ≤ 2 ∧
    K 2 11 9 ≤ 2 ∧
    K 2 11 10 ≤ 2 ∧
    K 2 12 5 ≤ 4 ∧
    K 2 12 6 ≤ 2 ∧
    K 2 12 7 ≤ 2 ∧
    K 2 12 8 ≤ 2 ∧
    K 2 12 9 ≤ 2 ∧
    K 2 12 10 ≤ 2 ∧
    K 2 13 6 ≤ 2 ∧
    K 2 13 7 ≤ 2 ∧
    K 2 13 8 ≤ 2 ∧
    K 2 13 9 ≤ 2 ∧
    K 2 13 10 ≤ 2 ∧
    K 2 14 6 ≤ 4 ∧
    K 2 14 7 ≤ 2 ∧
    K 2 14 8 ≤ 2 ∧
    K 2 14 9 ≤ 2 ∧
    K 2 14 10 ≤ 2 ∧
    K 2 15 7 ≤ 2 ∧
    K 2 15 8 ≤ 2 ∧
    K 2 15 9 ≤ 2 ∧
    K 2 15 10 ≤ 2 ∧
    K 2 16 7 ≤ 4 ∧
    K 2 16 8 ≤ 2 ∧
    K 2 16 9 ≤ 2 ∧
    K 2 16 10 ≤ 2 ∧
    K 2 17 8 ≤ 2 ∧
    K 2 17 9 ≤ 2 ∧
    K 2 17 10 ≤ 2 ∧
    K 2 18 8 ≤ 4 ∧
    K 2 18 9 ≤ 2 ∧
    K 2 18 10 ≤ 2 ∧
    K 2 19 9 ≤ 2 ∧
    K 2 19 10 ≤ 2 ∧
    K 2 20 9 ≤ 4 ∧
    K 2 20 10 ≤ 2 ∧
    K 2 21 10 ≤ 2 ∧
    K 2 22 10 ≤ 4 ∧
    K 3 1 1 ≤ 1 ∧
    K 3 2 1 ≤ 3 ∧
    K 3 2 2 ≤ 1 ∧
    K 3 3 1 ≤ 5 ∧
    K 3 3 2 ≤ 3 ∧
    K 3 3 3 ≤ 1 ∧
    K 3 4 1 ≤ 9 ∧
    K 3 4 2 ≤ 3 ∧
    K 3 4 3 ≤ 3 ∧
    K 3 4 4 ≤ 1 ∧
    K 3 5 1 ≤ 27 ∧
    K 3 5 2 ≤ 8 ∧
    K 3 5 3 ≤ 3 ∧
    K 3 5 4 ≤ 3 ∧
    K 3 5 5 ≤ 1 ∧
    K 3 6 2 ≤ 17 ∧
    K 3 6 3 ≤ 6 ∧
    K 3 6 4 ≤ 3 ∧
    K 3 6 5 ≤ 3 ∧
    K 3 6 6 ≤ 1 ∧
    K 3 7 4 ≤ 3 ∧
    K 3 7 5 ≤ 3 ∧
    K 3 7 6 ≤ 3 ∧
    K 3 7 7 ≤ 1 ∧
    K 3 8 2 ≤ 81 ∧
    K 3 8 3 ≤ 27 ∧
    K 3 8 4 ≤ 9 ∧
    K 3 8 5 ≤ 3 ∧
    K 3 8 6 ≤ 3 ∧
    K 3 8 7 ≤ 3 ∧
    K 3 8 8 ≤ 1 ∧
    K 3 9 6 ≤ 3 ∧
    K 3 9 7 ≤ 3 ∧
    K 3 9 8 ≤ 3 ∧
    K 3 10 6 ≤ 3 ∧
    K 3 10 7 ≤ 3 ∧
    K 3 10 8 ≤ 3 ∧
    K 3 11 5 ≤ 27 ∧
    K 3 11 6 ≤ 9 ∧
    K 3 11 7 ≤ 3 ∧
    K 3 11 8 ≤ 3 ∧
    K 3 12 8 ≤ 3 ∧
    K 3 13 8 ≤ 3 ∧
    K 3 14 7 ≤ 27 ∧
    K 3 14 8 ≤ 9 ∧
    K 4 1 1 ≤ 1 ∧
    K 4 2 1 ≤ 4 ∧
    K 4 2 2 ≤ 1 ∧
    K 4 3 1 ≤ 8 ∧
    K 4 3 2 ≤ 4 ∧
    K 4 3 3 ≤ 1 ∧
    K 4 4 1 ≤ 24 ∧
    K 4 4 2 ≤ 7 ∧
    K 4 4 3 ≤ 4 ∧
    K 4 4 4 ≤ 1 ∧
    K 4 5 3 ≤ 4 ∧
    K 4 5 4 ≤ 4 ∧
    K 4 5 5 ≤ 1 ∧
    K 4 6 4 ≤ 4 ∧
    K 4 6 5 ≤ 4 ∧
    K 4 6 6 ≤ 1 ∧
    K 4 7 5 ≤ 4 ∧
    K 4 7 6 ≤ 4 ∧
    K 4 7 7 ≤ 1 ∧
    K 4 8 6 ≤ 4 ∧
    K 4 8 7 ≤ 4 ∧
    K 4 8 8 ≤ 1 ∧
    K 4 9 6 ≤ 4 ∧
    K 4 9 7 ≤ 4 ∧
    K 4 9 8 ≤ 4 ∧
    K 4 10 6 ≤ 16 ∧
    K 4 10 7 ≤ 4 ∧
    K 4 10 8 ≤ 4 ∧
    K 4 11 8 ≤ 4 ∧
    K 5 1 1 ≤ 1 ∧
    K 5 2 1 ≤ 5 ∧
    K 5 2 2 ≤ 1 ∧
    K 5 3 1 ≤ 13 ∧
    K 5 3 2 ≤ 5 ∧
    K 5 3 3 ≤ 1 ∧
    K 5 4 2 ≤ 11 ∧
    K 5 4 3 ≤ 5 ∧
    K 5 4 4 ≤ 1 ∧
    K 5 5 4 ≤ 5 ∧
    K 5 5 5 ≤ 1 ∧
    K 5 6 4 ≤ 5 ∧
    K 5 6 5 ≤ 5 ∧
    K 5 6 6 ≤ 1 ∧
    K 5 7 5 ≤ 5 ∧
    K 5 7 6 ≤ 5 ∧
    K 5 7 7 ≤ 1 ∧
    K 5 8 6 ≤ 5 ∧
    K 5 8 7 ≤ 5 ∧
    K 5 8 8 ≤ 1 ∧
    K 5 9 7 ≤ 5 ∧
    K 5 9 8 ≤ 5 ∧
    K 5 10 8 ≤ 5 ∧
    K 5 11 8 ≤ 5 ∧
    K 6 1 1 ≤ 1 ∧
    K 6 2 1 ≤ 6 ∧
    K 6 2 2 ≤ 1 ∧
    K 6 3 1 ≤ 18 ∧
    K 6 3 2 ≤ 6 ∧
    K 6 3 3 ≤ 1 ∧
    K 6 4 2 ≤ 15 ∧
    K 6 4 3 ≤ 6 ∧
    K 6 4 4 ≤ 1 ∧
    K 6 5 4 ≤ 6 ∧
    K 6 5 5 ≤ 1 ∧
    K 6 6 5 ≤ 6 ∧
    K 6 6 6 ≤ 1 ∧
    K 6 7 5 ≤ 6 ∧
    K 6 7 6 ≤ 6 ∧
    K 6 7 7 ≤ 1 ∧
    K 6 8 6 ≤ 6 ∧
    K 6 8 7 ≤ 6 ∧
    K 6 8 8 ≤ 1 ∧
    K 6 9 7 ≤ 6 ∧
    K 6 9 8 ≤ 6 ∧
    K 6 10 8 ≤ 6 ∧
    K 7 1 1 ≤ 1 ∧
    K 7 2 1 ≤ 7 ∧
    K 7 2 2 ≤ 1 ∧
    K 7 3 1 ≤ 25 ∧
    K 7 3 2 ≤ 7 ∧
    K 7 3 3 ≤ 1 ∧
    K 7 4 2 ≤ 19 ∧
    K 7 4 3 ≤ 7 ∧
    K 7 4 4 ≤ 1 ∧
    K 7 5 4 ≤ 7 ∧
    K 7 5 5 ≤ 1 ∧
    K 7 6 5 ≤ 7 ∧
    K 7 6 6 ≤ 1 ∧
    K 7 7 6 ≤ 7 ∧
    K 7 7 7 ≤ 1 ∧
    K 7 8 6 ≤ 7 ∧
    K 7 8 7 ≤ 7 ∧
    K 7 8 8 ≤ 1 ∧
    K 7 9 7 ≤ 7 ∧
    K 7 9 8 ≤ 7 ∧
    K 7 10 8 ≤ 7 ∧
    K 8 1 1 ≤ 1 ∧
    K 8 2 1 ≤ 8 ∧
    K 8 2 2 ≤ 1 ∧
    K 8 3 1 ≤ 32 ∧
    K 8 3 2 ≤ 8 ∧
    K 8 3 3 ≤ 1 ∧
    K 8 4 2 ≤ 23 ∧
    K 8 4 3 ≤ 8 ∧
    K 8 4 4 ≤ 1 ∧
    K 8 5 4 ≤ 8 ∧
    K 8 5 5 ≤ 1 ∧
    K 8 6 5 ≤ 8 ∧
    K 8 6 6 ≤ 1 ∧
    K 8 7 6 ≤ 8 ∧
    K 8 7 7 ≤ 1 ∧
    K 8 8 7 ≤ 8 ∧
    K 8 8 8 ≤ 1 ∧
    K 8 9 7 ≤ 8 ∧
    K 8 9 8 ≤ 8 ∧
    K 8 10 8 ≤ 8 ∧
    K 9 1 1 ≤ 1 ∧
    K 9 2 1 ≤ 9 ∧
    K 9 2 2 ≤ 1 ∧
    K 9 3 1 ≤ 41 ∧
    K 9 3 2 ≤ 9 ∧
    K 9 3 3 ≤ 1 ∧
    K 9 4 2 ≤ 27 ∧
    K 9 4 3 ≤ 9 ∧
    K 9 4 4 ≤ 1 ∧
    K 9 5 3 ≤ 27 ∧
    K 9 5 4 ≤ 9 ∧
    K 9 5 5 ≤ 1 ∧
    K 9 6 5 ≤ 9 ∧
    K 9 6 6 ≤ 1 ∧
    K 9 7 6 ≤ 9 ∧
    K 9 7 7 ≤ 1 ∧
    K 9 8 4 ≤ 729 ∧
    K 9 8 7 ≤ 9 ∧
    K 9 8 8 ≤ 1 ∧
    K 9 9 8 ≤ 9 ∧
    K 9 10 8 ≤ 9 ∧
    K 10 1 1 ≤ 1 ∧
    K 10 2 1 ≤ 10 ∧
    K 10 2 2 ≤ 1 ∧
    K 10 3 1 ≤ 50 ∧
    K 10 3 2 ≤ 10 ∧
    K 10 3 3 ≤ 1 ∧
    K 10 4 2 ≤ 34 ∧
    K 10 4 3 ≤ 10 ∧
    K 10 4 4 ≤ 1 ∧
    K 10 5 4 ≤ 10 ∧
    K 10 5 5 ≤ 1 ∧
    K 10 6 5 ≤ 10 ∧
    K 10 6 6 ≤ 1 ∧
    K 10 7 6 ≤ 10 ∧
    K 10 7 7 ≤ 1 ∧
    K 10 8 4 ≤ 1156 ∧
    K 10 8 7 ≤ 10 ∧
    K 10 8 8 ≤ 1 ∧
    K 10 9 8 ≤ 10 ∧
    K 11 1 1 ≤ 1 ∧
    K 11 2 1 ≤ 11 ∧
    K 11 2 2 ≤ 1 ∧
    K 11 3 1 ≤ 61 ∧
    K 11 3 2 ≤ 11 ∧
    K 11 3 3 ≤ 1 ∧
    K 11 4 2 ≤ 41 ∧
    K 11 4 3 ≤ 11 ∧
    K 11 4 4 ≤ 1 ∧
    K 11 5 4 ≤ 11 ∧
    K 11 5 5 ≤ 1 ∧
    K 11 6 5 ≤ 11 ∧
    K 11 6 6 ≤ 1 ∧
    K 11 7 6 ≤ 11 ∧
    K 11 7 7 ≤ 1 ∧
    K 11 8 4 ≤ 1681 ∧
    K 11 8 7 ≤ 11 ∧
    K 11 8 8 ≤ 1 ∧
    K 12 1 1 ≤ 1 ∧
    K 12 2 1 ≤ 12 ∧
    K 12 2 2 ≤ 1 ∧
    K 12 3 1 ≤ 72 ∧
    K 12 3 2 ≤ 12 ∧
    K 12 3 3 ≤ 1 ∧
    K 12 4 2 ≤ 48 ∧
    K 12 4 3 ≤ 12 ∧
    K 12 4 4 ≤ 1 ∧
    K 12 5 4 ≤ 12 ∧
    K 12 5 5 ≤ 1 ∧
    K 12 6 5 ≤ 12 ∧
    K 12 6 6 ≤ 1 ∧
    K 12 7 3 ≤ 3456 ∧
    K 12 7 6 ≤ 12 ∧
    K 12 7 7 ≤ 1 ∧
    K 12 8 4 ≤ 2304 ∧
    K 12 8 7 ≤ 12 ∧
    K 12 8 8 ≤ 1 ∧
    K 13 1 1 ≤ 1 ∧
    K 13 2 1 ≤ 13 ∧
    K 13 2 2 ≤ 1 ∧
    K 13 3 1 ≤ 85 ∧
    K 13 3 2 ≤ 13 ∧
    K 13 3 3 ≤ 1 ∧
    K 13 4 3 ≤ 13 ∧
    K 13 4 4 ≤ 1 ∧
    K 13 5 4 ≤ 13 ∧
    K 13 5 5 ≤ 1 ∧
    K 13 6 5 ≤ 13 ∧
    K 13 6 6 ≤ 1 ∧
    K 13 7 6 ≤ 13 ∧
    K 13 7 7 ≤ 1 ∧
    K 13 8 7 ≤ 13 ∧
    K 13 8 8 ≤ 1 ∧
    K 14 1 1 ≤ 1 ∧
    K 14 2 1 ≤ 14 ∧
    K 14 2 2 ≤ 1 ∧
    K 14 3 1 ≤ 98 ∧
    K 14 3 2 ≤ 14 ∧
    K 14 3 3 ≤ 1 ∧
    K 14 4 3 ≤ 14 ∧
    K 14 4 4 ≤ 1 ∧
    K 14 5 4 ≤ 14 ∧
    K 14 5 5 ≤ 1 ∧
    K 14 6 5 ≤ 14 ∧
    K 14 6 6 ≤ 1 ∧
    K 14 7 6 ≤ 14 ∧
    K 14 7 7 ≤ 1 ∧
    K 14 8 7 ≤ 14 ∧
    K 14 8 8 ≤ 1 ∧
    K 15 1 1 ≤ 1 ∧
    K 15 2 1 ≤ 15 ∧
    K 15 2 2 ≤ 1 ∧
    K 15 3 1 ≤ 113 ∧
    K 15 3 2 ≤ 15 ∧
    K 15 3 3 ≤ 1 ∧
    K 15 4 3 ≤ 15 ∧
    K 15 4 4 ≤ 1 ∧
    K 15 5 4 ≤ 15 ∧
    K 15 5 5 ≤ 1 ∧
    K 15 6 5 ≤ 15 ∧
    K 15 6 6 ≤ 1 ∧
    K 15 7 6 ≤ 15 ∧
    K 15 7 7 ≤ 1 ∧
    K 15 8 7 ≤ 15 ∧
    K 15 8 8 ≤ 1 ∧
    K 16 1 1 ≤ 1 ∧
    K 16 2 1 ≤ 16 ∧
    K 16 2 2 ≤ 1 ∧
    K 16 3 1 ≤ 128 ∧
    K 16 3 2 ≤ 16 ∧
    K 16 3 3 ≤ 1 ∧
    K 16 4 3 ≤ 16 ∧
    K 16 4 4 ≤ 1 ∧
    K 16 5 4 ≤ 16 ∧
    K 16 5 5 ≤ 1 ∧
    K 16 6 5 ≤ 16 ∧
    K 16 6 6 ≤ 1 ∧
    K 16 7 6 ≤ 16 ∧
    K 16 7 7 ≤ 1 ∧
    K 16 8 7 ≤ 16 ∧
    K 16 8 8 ≤ 1 ∧
    K 17 1 1 ≤ 1 ∧
    K 17 2 1 ≤ 17 ∧
    K 17 2 2 ≤ 1 ∧
    K 17 3 1 ≤ 145 ∧
    K 17 3 2 ≤ 17 ∧
    K 17 3 3 ≤ 1 ∧
    K 17 4 3 ≤ 17 ∧
    K 17 4 4 ≤ 1 ∧
    K 17 5 4 ≤ 17 ∧
    K 17 5 5 ≤ 1 ∧
    K 17 6 5 ≤ 17 ∧
    K 17 6 6 ≤ 1 ∧
    K 17 7 6 ≤ 17 ∧
    K 17 7 7 ≤ 1 ∧
    K 17 8 7 ≤ 17 ∧
    K 17 8 8 ≤ 1 ∧
    K 18 1 1 ≤ 1 ∧
    K 18 2 1 ≤ 18 ∧
    K 18 2 2 ≤ 1 ∧
    K 18 3 1 ≤ 162 ∧
    K 18 3 2 ≤ 18 ∧
    K 18 3 3 ≤ 1 ∧
    K 18 4 3 ≤ 18 ∧
    K 18 4 4 ≤ 1 ∧
    K 18 5 4 ≤ 18 ∧
    K 18 5 5 ≤ 1 ∧
    K 18 6 5 ≤ 18 ∧
    K 18 6 6 ≤ 1 ∧
    K 18 7 6 ≤ 18 ∧
    K 18 7 7 ≤ 1 ∧
    K 18 8 7 ≤ 18 ∧
    K 18 8 8 ≤ 1 ∧
    K 19 1 1 ≤ 1 ∧
    K 19 2 1 ≤ 19 ∧
    K 19 2 2 ≤ 1 ∧
    K 19 3 2 ≤ 19 ∧
    K 19 3 3 ≤ 1 ∧
    K 19 4 3 ≤ 19 ∧
    K 19 4 4 ≤ 1 ∧
    K 19 5 4 ≤ 19 ∧
    K 19 5 5 ≤ 1 ∧
    K 19 6 5 ≤ 19 ∧
    K 19 6 6 ≤ 1 ∧
    K 19 7 6 ≤ 19 ∧
    K 19 7 7 ≤ 1 ∧
    K 19 8 7 ≤ 19 ∧
    K 19 8 8 ≤ 1 ∧
    K 20 1 1 ≤ 1 ∧
    K 20 2 1 ≤ 20 ∧
    K 20 2 2 ≤ 1 ∧
    K 20 3 2 ≤ 20 ∧
    K 20 3 3 ≤ 1 ∧
    K 20 4 3 ≤ 20 ∧
    K 20 4 4 ≤ 1 ∧
    K 20 5 4 ≤ 20 ∧
    K 20 5 5 ≤ 1 ∧
    K 20 6 5 ≤ 20 ∧
    K 20 6 6 ≤ 1 ∧
    K 20 7 6 ≤ 20 ∧
    K 20 7 7 ≤ 1 ∧
    K 20 8 7 ≤ 20 ∧
    K 20 8 8 ≤ 1 ∧
    K 21 1 1 ≤ 1 ∧
    K 21 2 1 ≤ 21 ∧
    K 21 2 2 ≤ 1 ∧
    K 21 3 2 ≤ 21 ∧
    K 21 3 3 ≤ 1 ∧
    K 21 4 3 ≤ 21 ∧
    K 21 4 4 ≤ 1 ∧
    K 21 5 4 ≤ 21 ∧
    K 21 5 5 ≤ 1 ∧
    K 21 6 5 ≤ 21 ∧
    K 21 6 6 ≤ 1 ∧
    K 21 7 6 ≤ 21 ∧
    K 21 7 7 ≤ 1 ∧
    K 21 8 7 ≤ 21 ∧
    K 21 8 8 ≤ 1 :=
  ⟨CoveringLedger.K2_1_1_le_1,
   CoveringLedger.K2_2_1_le_2,
   CoveringLedger.K2_2_2_le_1,
   CoveringLedger.K2_3_1_le_2,
   CoveringLedger.K2_3_2_le_2,
   CoveringLedger.K2_3_3_le_1,
   CoveringLedger.K2_4_1_le_4,
   CoveringLedger.K2_4_2_le_2,
   CoveringLedger.K2_4_3_le_2,
   CoveringLedger.K2_4_4_le_1,
   CoveringLedger.K2_5_1_le_7,
   CoveringLedger.K2_5_2_le_2,
   CoveringLedger.K2_5_3_le_2,
   CoveringLedger.K2_5_4_le_2,
   CoveringLedger.K2_5_5_le_1,
   CoveringLedger.K2_6_1_le_12,
   CoveringLedger.K2_6_2_le_4,
   CoveringLedger.K2_6_3_le_2,
   CoveringLedger.K2_6_4_le_2,
   CoveringLedger.K2_6_5_le_2,
   CoveringLedger.K2_6_6_le_1,
   CoveringLedger.K2_7_1_le_16,
   CoveringLedger.K2_7_2_le_7,
   CoveringLedger.K2_7_3_le_2,
   CoveringLedger.K2_7_4_le_2,
   CoveringLedger.K2_7_5_le_2,
   CoveringLedger.K2_7_6_le_2,
   CoveringLedger.K2_7_7_le_1,
   CoveringLedger.K2_8_1_le_32,
   CoveringLedger.K2_8_2_le_12,
   CoveringLedger.K2_8_3_le_4,
   CoveringLedger.K2_8_4_le_2,
   CoveringLedger.K2_8_5_le_2,
   CoveringLedger.K2_8_6_le_2,
   CoveringLedger.K2_8_7_le_2,
   CoveringLedger.K2_8_8_le_1,
   CoveringLedger.K2_9_2_le_16,
   CoveringLedger.K2_9_3_le_7,
   CoveringLedger.K2_9_4_le_2,
   CoveringLedger.K2_9_5_le_2,
   CoveringLedger.K2_9_6_le_2,
   CoveringLedger.K2_9_7_le_2,
   CoveringLedger.K2_9_8_le_2,
   CoveringLedger.K2_9_9_le_1,
   CoveringLedger.K2_10_3_le_12,
   CoveringLedger.K2_10_4_le_4,
   CoveringLedger.K2_10_5_le_2,
   CoveringLedger.K2_10_6_le_2,
   CoveringLedger.K2_10_7_le_2,
   CoveringLedger.K2_10_8_le_2,
   CoveringLedger.K2_10_9_le_2,
   CoveringLedger.K2_10_10_le_1,
   CoveringLedger.K2_11_1_le_192,
   CoveringLedger.K2_11_3_le_16,
   CoveringLedger.K2_11_5_le_2,
   CoveringLedger.K2_11_6_le_2,
   CoveringLedger.K2_11_7_le_2,
   CoveringLedger.K2_11_8_le_2,
   CoveringLedger.K2_11_9_le_2,
   CoveringLedger.K2_11_10_le_2,
   CoveringLedger.K2_12_5_le_4,
   CoveringLedger.K2_12_6_le_2,
   CoveringLedger.K2_12_7_le_2,
   CoveringLedger.K2_12_8_le_2,
   CoveringLedger.K2_12_9_le_2,
   CoveringLedger.K2_12_10_le_2,
   CoveringLedger.K2_13_6_le_2,
   CoveringLedger.K2_13_7_le_2,
   CoveringLedger.K2_13_8_le_2,
   CoveringLedger.K2_13_9_le_2,
   CoveringLedger.K2_13_10_le_2,
   CoveringLedger.K2_14_6_le_4,
   CoveringLedger.K2_14_7_le_2,
   CoveringLedger.K2_14_8_le_2,
   CoveringLedger.K2_14_9_le_2,
   CoveringLedger.K2_14_10_le_2,
   CoveringLedger.K2_15_7_le_2,
   CoveringLedger.K2_15_8_le_2,
   CoveringLedger.K2_15_9_le_2,
   CoveringLedger.K2_15_10_le_2,
   CoveringLedger.K2_16_7_le_4,
   CoveringLedger.K2_16_8_le_2,
   CoveringLedger.K2_16_9_le_2,
   CoveringLedger.K2_16_10_le_2,
   CoveringLedger.K2_17_8_le_2,
   CoveringLedger.K2_17_9_le_2,
   CoveringLedger.K2_17_10_le_2,
   CoveringLedger.K2_18_8_le_4,
   CoveringLedger.K2_18_9_le_2,
   CoveringLedger.K2_18_10_le_2,
   CoveringLedger.K2_19_9_le_2,
   CoveringLedger.K2_19_10_le_2,
   CoveringLedger.K2_20_9_le_4,
   CoveringLedger.K2_20_10_le_2,
   CoveringLedger.K2_21_10_le_2,
   CoveringLedger.K2_22_10_le_4,
   CoveringLedger.K3_1_1_le_1,
   CoveringLedger.K3_2_1_le_3,
   CoveringLedger.K3_2_2_le_1,
   CoveringLedger.K3_3_1_le_5,
   CoveringLedger.K3_3_2_le_3,
   CoveringLedger.K3_3_3_le_1,
   CoveringLedger.K3_4_1_le_9,
   CoveringLedger.K3_4_2_le_3,
   CoveringLedger.K3_4_3_le_3,
   CoveringLedger.K3_4_4_le_1,
   CoveringLedger.K3_5_1_le_27,
   CoveringLedger.K3_5_2_le_8,
   CoveringLedger.K3_5_3_le_3,
   CoveringLedger.K3_5_4_le_3,
   CoveringLedger.K3_5_5_le_1,
   CoveringLedger.K3_6_2_le_17,
   CoveringLedger.K3_6_3_le_6,
   CoveringLedger.K3_6_4_le_3,
   CoveringLedger.K3_6_5_le_3,
   CoveringLedger.K3_6_6_le_1,
   CoveringLedger.K3_7_4_le_3,
   CoveringLedger.K3_7_5_le_3,
   CoveringLedger.K3_7_6_le_3,
   CoveringLedger.K3_7_7_le_1,
   CoveringLedger.K3_8_2_le_81,
   CoveringLedger.K3_8_3_le_27,
   CoveringLedger.K3_8_4_le_9,
   CoveringLedger.K3_8_5_le_3,
   CoveringLedger.K3_8_6_le_3,
   CoveringLedger.K3_8_7_le_3,
   CoveringLedger.K3_8_8_le_1,
   CoveringLedger.K3_9_6_le_3,
   CoveringLedger.K3_9_7_le_3,
   CoveringLedger.K3_9_8_le_3,
   CoveringLedger.K3_10_6_le_3,
   CoveringLedger.K3_10_7_le_3,
   CoveringLedger.K3_10_8_le_3,
   CoveringLedger.K3_11_5_le_27,
   CoveringLedger.K3_11_6_le_9,
   CoveringLedger.K3_11_7_le_3,
   CoveringLedger.K3_11_8_le_3,
   CoveringLedger.K3_12_8_le_3,
   CoveringLedger.K3_13_8_le_3,
   CoveringLedger.K3_14_7_le_27,
   CoveringLedger.K3_14_8_le_9,
   CoveringLedger.K4_1_1_le_1,
   CoveringLedger.K4_2_1_le_4,
   CoveringLedger.K4_2_2_le_1,
   CoveringLedger.K4_3_1_le_8,
   CoveringLedger.K4_3_2_le_4,
   CoveringLedger.K4_3_3_le_1,
   CoveringLedger.K4_4_1_le_24,
   CoveringLedger.K4_4_2_le_7,
   CoveringLedger.K4_4_3_le_4,
   CoveringLedger.K4_4_4_le_1,
   CoveringLedger.K4_5_3_le_4,
   CoveringLedger.K4_5_4_le_4,
   CoveringLedger.K4_5_5_le_1,
   CoveringLedger.K4_6_4_le_4,
   CoveringLedger.K4_6_5_le_4,
   CoveringLedger.K4_6_6_le_1,
   CoveringLedger.K4_7_5_le_4,
   CoveringLedger.K4_7_6_le_4,
   CoveringLedger.K4_7_7_le_1,
   CoveringLedger.K4_8_6_le_4,
   CoveringLedger.K4_8_7_le_4,
   CoveringLedger.K4_8_8_le_1,
   CoveringLedger.K4_9_6_le_4,
   CoveringLedger.K4_9_7_le_4,
   CoveringLedger.K4_9_8_le_4,
   CoveringLedger.K4_10_6_le_16,
   CoveringLedger.K4_10_7_le_4,
   CoveringLedger.K4_10_8_le_4,
   CoveringLedger.K4_11_8_le_4,
   CoveringLedger.K5_1_1_le_1,
   CoveringLedger.K5_2_1_le_5,
   CoveringLedger.K5_2_2_le_1,
   CoveringLedger.K5_3_1_le_13,
   CoveringLedger.K5_3_2_le_5,
   CoveringLedger.K5_3_3_le_1,
   CoveringLedger.K5_4_2_le_11,
   CoveringLedger.K5_4_3_le_5,
   CoveringLedger.K5_4_4_le_1,
   CoveringLedger.K5_5_4_le_5,
   CoveringLedger.K5_5_5_le_1,
   CoveringLedger.K5_6_4_le_5,
   CoveringLedger.K5_6_5_le_5,
   CoveringLedger.K5_6_6_le_1,
   CoveringLedger.K5_7_5_le_5,
   CoveringLedger.K5_7_6_le_5,
   CoveringLedger.K5_7_7_le_1,
   CoveringLedger.K5_8_6_le_5,
   CoveringLedger.K5_8_7_le_5,
   CoveringLedger.K5_8_8_le_1,
   CoveringLedger.K5_9_7_le_5,
   CoveringLedger.K5_9_8_le_5,
   CoveringLedger.K5_10_8_le_5,
   CoveringLedger.K5_11_8_le_5,
   CoveringLedger.K6_1_1_le_1,
   CoveringLedger.K6_2_1_le_6,
   CoveringLedger.K6_2_2_le_1,
   CoveringLedger.K6_3_1_le_18,
   CoveringLedger.K6_3_2_le_6,
   CoveringLedger.K6_3_3_le_1,
   CoveringLedger.K6_4_2_le_15,
   CoveringLedger.K6_4_3_le_6,
   CoveringLedger.K6_4_4_le_1,
   CoveringLedger.K6_5_4_le_6,
   CoveringLedger.K6_5_5_le_1,
   CoveringLedger.K6_6_5_le_6,
   CoveringLedger.K6_6_6_le_1,
   CoveringLedger.K6_7_5_le_6,
   CoveringLedger.K6_7_6_le_6,
   CoveringLedger.K6_7_7_le_1,
   CoveringLedger.K6_8_6_le_6,
   CoveringLedger.K6_8_7_le_6,
   CoveringLedger.K6_8_8_le_1,
   CoveringLedger.K6_9_7_le_6,
   CoveringLedger.K6_9_8_le_6,
   CoveringLedger.K6_10_8_le_6,
   CoveringLedger.K7_1_1_le_1,
   CoveringLedger.K7_2_1_le_7,
   CoveringLedger.K7_2_2_le_1,
   CoveringLedger.K7_3_1_le_25,
   CoveringLedger.K7_3_2_le_7,
   CoveringLedger.K7_3_3_le_1,
   CoveringLedger.K7_4_2_le_19,
   CoveringLedger.K7_4_3_le_7,
   CoveringLedger.K7_4_4_le_1,
   CoveringLedger.K7_5_4_le_7,
   CoveringLedger.K7_5_5_le_1,
   CoveringLedger.K7_6_5_le_7,
   CoveringLedger.K7_6_6_le_1,
   CoveringLedger.K7_7_6_le_7,
   CoveringLedger.K7_7_7_le_1,
   CoveringLedger.K7_8_6_le_7,
   CoveringLedger.K7_8_7_le_7,
   CoveringLedger.K7_8_8_le_1,
   CoveringLedger.K7_9_7_le_7,
   CoveringLedger.K7_9_8_le_7,
   CoveringLedger.K7_10_8_le_7,
   CoveringLedger.K8_1_1_le_1,
   CoveringLedger.K8_2_1_le_8,
   CoveringLedger.K8_2_2_le_1,
   CoveringLedger.K8_3_1_le_32,
   CoveringLedger.K8_3_2_le_8,
   CoveringLedger.K8_3_3_le_1,
   CoveringLedger.K8_4_2_le_23,
   CoveringLedger.K8_4_3_le_8,
   CoveringLedger.K8_4_4_le_1,
   CoveringLedger.K8_5_4_le_8,
   CoveringLedger.K8_5_5_le_1,
   CoveringLedger.K8_6_5_le_8,
   CoveringLedger.K8_6_6_le_1,
   CoveringLedger.K8_7_6_le_8,
   CoveringLedger.K8_7_7_le_1,
   CoveringLedger.K8_8_7_le_8,
   CoveringLedger.K8_8_8_le_1,
   CoveringLedger.K8_9_7_le_8,
   CoveringLedger.K8_9_8_le_8,
   CoveringLedger.K8_10_8_le_8,
   CoveringLedger.K9_1_1_le_1,
   CoveringLedger.K9_2_1_le_9,
   CoveringLedger.K9_2_2_le_1,
   CoveringLedger.K9_3_1_le_41,
   CoveringLedger.K9_3_2_le_9,
   CoveringLedger.K9_3_3_le_1,
   CoveringLedger.K9_4_2_le_27,
   CoveringLedger.K9_4_3_le_9,
   CoveringLedger.K9_4_4_le_1,
   CoveringLedger.K9_5_3_le_27,
   CoveringLedger.K9_5_4_le_9,
   CoveringLedger.K9_5_5_le_1,
   CoveringLedger.K9_6_5_le_9,
   CoveringLedger.K9_6_6_le_1,
   CoveringLedger.K9_7_6_le_9,
   CoveringLedger.K9_7_7_le_1,
   CoveringLedger.K9_8_4_le_729,
   CoveringLedger.K9_8_7_le_9,
   CoveringLedger.K9_8_8_le_1,
   CoveringLedger.K9_9_8_le_9,
   CoveringLedger.K9_10_8_le_9,
   CoveringLedger.K10_1_1_le_1,
   CoveringLedger.K10_2_1_le_10,
   CoveringLedger.K10_2_2_le_1,
   CoveringLedger.K10_3_1_le_50,
   CoveringLedger.K10_3_2_le_10,
   CoveringLedger.K10_3_3_le_1,
   CoveringLedger.K10_4_2_le_34,
   CoveringLedger.K10_4_3_le_10,
   CoveringLedger.K10_4_4_le_1,
   CoveringLedger.K10_5_4_le_10,
   CoveringLedger.K10_5_5_le_1,
   CoveringLedger.K10_6_5_le_10,
   CoveringLedger.K10_6_6_le_1,
   CoveringLedger.K10_7_6_le_10,
   CoveringLedger.K10_7_7_le_1,
   CoveringLedger.K10_8_4_le_1156,
   CoveringLedger.K10_8_7_le_10,
   CoveringLedger.K10_8_8_le_1,
   CoveringLedger.K10_9_8_le_10,
   CoveringLedger.K11_1_1_le_1,
   CoveringLedger.K11_2_1_le_11,
   CoveringLedger.K11_2_2_le_1,
   CoveringLedger.K11_3_1_le_61,
   CoveringLedger.K11_3_2_le_11,
   CoveringLedger.K11_3_3_le_1,
   CoveringLedger.K11_4_2_le_41,
   CoveringLedger.K11_4_3_le_11,
   CoveringLedger.K11_4_4_le_1,
   CoveringLedger.K11_5_4_le_11,
   CoveringLedger.K11_5_5_le_1,
   CoveringLedger.K11_6_5_le_11,
   CoveringLedger.K11_6_6_le_1,
   CoveringLedger.K11_7_6_le_11,
   CoveringLedger.K11_7_7_le_1,
   CoveringLedger.K11_8_4_le_1681,
   CoveringLedger.K11_8_7_le_11,
   CoveringLedger.K11_8_8_le_1,
   CoveringLedger.K12_1_1_le_1,
   CoveringLedger.K12_2_1_le_12,
   CoveringLedger.K12_2_2_le_1,
   CoveringLedger.K12_3_1_le_72,
   CoveringLedger.K12_3_2_le_12,
   CoveringLedger.K12_3_3_le_1,
   CoveringLedger.K12_4_2_le_48,
   CoveringLedger.K12_4_3_le_12,
   CoveringLedger.K12_4_4_le_1,
   CoveringLedger.K12_5_4_le_12,
   CoveringLedger.K12_5_5_le_1,
   CoveringLedger.K12_6_5_le_12,
   CoveringLedger.K12_6_6_le_1,
   CoveringLedger.K12_7_3_le_3456,
   CoveringLedger.K12_7_6_le_12,
   CoveringLedger.K12_7_7_le_1,
   CoveringLedger.K12_8_4_le_2304,
   CoveringLedger.K12_8_7_le_12,
   CoveringLedger.K12_8_8_le_1,
   CoveringLedger.K13_1_1_le_1,
   CoveringLedger.K13_2_1_le_13,
   CoveringLedger.K13_2_2_le_1,
   CoveringLedger.K13_3_1_le_85,
   CoveringLedger.K13_3_2_le_13,
   CoveringLedger.K13_3_3_le_1,
   CoveringLedger.K13_4_3_le_13,
   CoveringLedger.K13_4_4_le_1,
   CoveringLedger.K13_5_4_le_13,
   CoveringLedger.K13_5_5_le_1,
   CoveringLedger.K13_6_5_le_13,
   CoveringLedger.K13_6_6_le_1,
   CoveringLedger.K13_7_6_le_13,
   CoveringLedger.K13_7_7_le_1,
   CoveringLedger.K13_8_7_le_13,
   CoveringLedger.K13_8_8_le_1,
   CoveringLedger.K14_1_1_le_1,
   CoveringLedger.K14_2_1_le_14,
   CoveringLedger.K14_2_2_le_1,
   CoveringLedger.K14_3_1_le_98,
   CoveringLedger.K14_3_2_le_14,
   CoveringLedger.K14_3_3_le_1,
   CoveringLedger.K14_4_3_le_14,
   CoveringLedger.K14_4_4_le_1,
   CoveringLedger.K14_5_4_le_14,
   CoveringLedger.K14_5_5_le_1,
   CoveringLedger.K14_6_5_le_14,
   CoveringLedger.K14_6_6_le_1,
   CoveringLedger.K14_7_6_le_14,
   CoveringLedger.K14_7_7_le_1,
   CoveringLedger.K14_8_7_le_14,
   CoveringLedger.K14_8_8_le_1,
   CoveringLedger.K15_1_1_le_1,
   CoveringLedger.K15_2_1_le_15,
   CoveringLedger.K15_2_2_le_1,
   CoveringLedger.K15_3_1_le_113,
   CoveringLedger.K15_3_2_le_15,
   CoveringLedger.K15_3_3_le_1,
   CoveringLedger.K15_4_3_le_15,
   CoveringLedger.K15_4_4_le_1,
   CoveringLedger.K15_5_4_le_15,
   CoveringLedger.K15_5_5_le_1,
   CoveringLedger.K15_6_5_le_15,
   CoveringLedger.K15_6_6_le_1,
   CoveringLedger.K15_7_6_le_15,
   CoveringLedger.K15_7_7_le_1,
   CoveringLedger.K15_8_7_le_15,
   CoveringLedger.K15_8_8_le_1,
   CoveringLedger.K16_1_1_le_1,
   CoveringLedger.K16_2_1_le_16,
   CoveringLedger.K16_2_2_le_1,
   CoveringLedger.K16_3_1_le_128,
   CoveringLedger.K16_3_2_le_16,
   CoveringLedger.K16_3_3_le_1,
   CoveringLedger.K16_4_3_le_16,
   CoveringLedger.K16_4_4_le_1,
   CoveringLedger.K16_5_4_le_16,
   CoveringLedger.K16_5_5_le_1,
   CoveringLedger.K16_6_5_le_16,
   CoveringLedger.K16_6_6_le_1,
   CoveringLedger.K16_7_6_le_16,
   CoveringLedger.K16_7_7_le_1,
   CoveringLedger.K16_8_7_le_16,
   CoveringLedger.K16_8_8_le_1,
   CoveringLedger.K17_1_1_le_1,
   CoveringLedger.K17_2_1_le_17,
   CoveringLedger.K17_2_2_le_1,
   CoveringLedger.K17_3_1_le_145,
   CoveringLedger.K17_3_2_le_17,
   CoveringLedger.K17_3_3_le_1,
   CoveringLedger.K17_4_3_le_17,
   CoveringLedger.K17_4_4_le_1,
   CoveringLedger.K17_5_4_le_17,
   CoveringLedger.K17_5_5_le_1,
   CoveringLedger.K17_6_5_le_17,
   CoveringLedger.K17_6_6_le_1,
   CoveringLedger.K17_7_6_le_17,
   CoveringLedger.K17_7_7_le_1,
   CoveringLedger.K17_8_7_le_17,
   CoveringLedger.K17_8_8_le_1,
   CoveringLedger.K18_1_1_le_1,
   CoveringLedger.K18_2_1_le_18,
   CoveringLedger.K18_2_2_le_1,
   CoveringLedger.K18_3_1_le_162,
   CoveringLedger.K18_3_2_le_18,
   CoveringLedger.K18_3_3_le_1,
   CoveringLedger.K18_4_3_le_18,
   CoveringLedger.K18_4_4_le_1,
   CoveringLedger.K18_5_4_le_18,
   CoveringLedger.K18_5_5_le_1,
   CoveringLedger.K18_6_5_le_18,
   CoveringLedger.K18_6_6_le_1,
   CoveringLedger.K18_7_6_le_18,
   CoveringLedger.K18_7_7_le_1,
   CoveringLedger.K18_8_7_le_18,
   CoveringLedger.K18_8_8_le_1,
   CoveringLedger.K19_1_1_le_1,
   CoveringLedger.K19_2_1_le_19,
   CoveringLedger.K19_2_2_le_1,
   CoveringLedger.K19_3_2_le_19,
   CoveringLedger.K19_3_3_le_1,
   CoveringLedger.K19_4_3_le_19,
   CoveringLedger.K19_4_4_le_1,
   CoveringLedger.K19_5_4_le_19,
   CoveringLedger.K19_5_5_le_1,
   CoveringLedger.K19_6_5_le_19,
   CoveringLedger.K19_6_6_le_1,
   CoveringLedger.K19_7_6_le_19,
   CoveringLedger.K19_7_7_le_1,
   CoveringLedger.K19_8_7_le_19,
   CoveringLedger.K19_8_8_le_1,
   CoveringLedger.K20_1_1_le_1,
   CoveringLedger.K20_2_1_le_20,
   CoveringLedger.K20_2_2_le_1,
   CoveringLedger.K20_3_2_le_20,
   CoveringLedger.K20_3_3_le_1,
   CoveringLedger.K20_4_3_le_20,
   CoveringLedger.K20_4_4_le_1,
   CoveringLedger.K20_5_4_le_20,
   CoveringLedger.K20_5_5_le_1,
   CoveringLedger.K20_6_5_le_20,
   CoveringLedger.K20_6_6_le_1,
   CoveringLedger.K20_7_6_le_20,
   CoveringLedger.K20_7_7_le_1,
   CoveringLedger.K20_8_7_le_20,
   CoveringLedger.K20_8_8_le_1,
   CoveringLedger.K21_1_1_le_1,
   CoveringLedger.K21_2_1_le_21,
   CoveringLedger.K21_2_2_le_1,
   CoveringLedger.K21_3_2_le_21,
   CoveringLedger.K21_3_3_le_1,
   CoveringLedger.K21_4_3_le_21,
   CoveringLedger.K21_4_4_le_1,
   CoveringLedger.K21_5_4_le_21,
   CoveringLedger.K21_5_5_le_1,
   CoveringLedger.K21_6_5_le_21,
   CoveringLedger.K21_6_6_le_1,
   CoveringLedger.K21_7_6_le_21,
   CoveringLedger.K21_7_7_le_1,
   CoveringLedger.K21_8_7_le_21,
   CoveringLedger.K21_8_8_le_1⟩

end CoveringLedger

#print axioms CoveringLedger.todas_as_cotas
