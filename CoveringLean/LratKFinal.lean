import CoveringLean.LratKData

/-!
# `lratk_final_seg`: o fecho de uma refutação dividida, com a cadeia em segmentos

    lratk_final_seg ns "dir" for G

Faz o mesmo que `lratk_final` (de `LratKData`): encadeia `ns.fGood` e os blocos `ns.ok<j>` em
`ns.steps : ∀ v, (∀ c ∈ F, sat) → Good db v (K+1)`, depois `ns.unsat`, `ns.eqF` e
`ns.unsatFor : Unsat G`. A diferença: a cadeia de `good_of_checkRange` é quebrada em teoremas
`ns.seg<s>` de até 200 blocos cada. Medido (2026-10-04): um termo com 12 001 aplicações
aninhadas faz o kernel parar com "deep recursion detected"; o perfil 55 sem quebra tem 8 536
blocos.
-/

namespace LratK

open Lean Elab Command Meta

private def lnat' : Expr := mkApp (mkConst ``List [0]) (mkConst ``Nat)
private def llnat' : Expr := mkApp (mkConst ``List [0]) lnat'

private def eqBoolTrue' (b : Expr) : Expr :=
  mkApp3 (mkConst ``Eq [1]) (mkConst ``Bool) b (mkConst ``Bool.true)

private def reflTrue' (b : Expr) : Expr :=
  mkApp3 (mkConst ``of_decide_eq_true) (eqBoolTrue' b)
    (mkApp2 (mkConst ``instDecidableEqBool) b (mkConst ``Bool.true))
    (mkApp2 (mkConst ``Eq.refl [1]) (mkConst ``Bool) (mkConst ``Bool.true))

private def memF' (fN : Name) : Expr :=
  mkForall `c .default lnat'
    (mkForall `_h .default (mkApp5 (mkConst ``Membership.mem [0, 0]) lnat' llnat'
        (mkApp (mkConst ``List.instMembership [0]) lnat') (mkConst fN) (mkBVar 0))
      (mkApp2 (mkConst ``ClauseSat) (mkBVar 2) (mkBVar 1)))

private def vTy' : Expr := mkForall `_n .default (mkConst ``Nat) (mkConst ``Bool)

private def addThm' (n : Name) (ty val : Expr) : CoreM Unit :=
  addDecl <| Declaration.thmDecl { name := n, levelParams := [], type := ty, value := val }

/-- Blocos por segmento da cadeia. -/
def segBlocos : Nat := 200

syntax "lratk_final_seg " ident str " for " term : command

elab_rules : command
  | `(lratk_final_seg $ns:ident $dirS:str for $ft:term) => do
  let fT ← liftTermElabM do
    let e ← Term.elabTerm ft (some llnat')
    Term.synthesizeSyntheticMVarsNoPostponing
    instantiateMVars e
  let dir := (System.FilePath.mk (← getFileName)).parent.get! / dirS.getString
  let txt ← IO.FS.readFile (dir / "meta.txt")
  let mt := ((txt.trimAscii.toString.splitOn " ").filter (· ≠ "")).map String.toNat!
  let n := mt[0]!
  let K := mt[1]!
  let bloco := mt[2]!
  let nb := mt[3]!
  let base := (← getCurrNamespace) ++ ns.getId
  let dbC := mkConst (base ++ `db)
  let fN := base ++ `F
  liftCoreM do
    let v := mkFVar ⟨`v⟩
    let hF := mkFVar ⟨`hF⟩
    let goodTy (k : Nat) := mkForall `v .default vTy' (mkForall `hF .default (memF' fN)
      (mkApp3 (mkConst ``Good) dbC (mkBVar 1) (mkRawNatLit k)))
    let close (g : Expr) := mkLambda `v .default vTy' (mkLambda `hF .default (memF' fN)
      (g.abstract #[v, hF]))
    let mut prev := mkApp2 (mkConst (base ++ `fGood)) v hF
    let mut s := 0
    let mut j := 0
    while j < nb do
      let mut g := prev
      let fim := min nb (j + segBlocos)
      while j < fim do
        g := mkAppN (mkConst ``good_of_checkRange) #[dbC, v,
          mkConst (base ++ Name.mkSimple s!"H{j}"), mkRawNatLit (n + 1 + j * bloco), g,
          mkConst (base ++ Name.mkSimple s!"ok{j}")]
        j := j + 1
      -- chave depois do último bloco do segmento: n + 1 + (número de passos até aqui)
      let kfim := if j == nb then K + 1 else n + 1 + j * bloco
      let sN := base ++ Name.mkSimple s!"seg{s}"
      addThm' sN (goodTy kfim) (close g)
      prev := mkApp2 (mkConst sN) v hF
      s := s + 1
    addThm' (base ++ `steps) (goodTy (K + 1)) (close prev)
    let uN := base ++ `unsat
    addThm' uN (mkApp (mkConst ``Unsat) (mkConst fN))
      (mkAppN (mkConst ``unsat_of_chain) #[dbC, mkConst fN, mkRawNatLit K, mkConst (base ++ `steps),
        mkConst (base ++ `hK), mkConst (base ++ `hempty)])
    let b := mkApp2 (mkConst ``listsBeq) (mkConst fN) fT
    let eqN := base ++ `eqF
    addThm' eqN (eqBoolTrue' b) (reflTrue' b)
    addThm' (base ++ `unsatFor) (mkApp (mkConst ``Unsat) fT)
      (mkAppN (mkConst ``unsat_of_listsBeq) #[mkConst fN, fT, mkConst uN, mkConst eqN])
    logInfo (toString nb ++ " blocos em " ++ toString s ++ " segmentos")

end LratK
