import Lean
import CoveringLean.LratK

/-!
# LratKData: lê CNF + LRAT e monta os dados e as provas de `LratK`

O comando

    lratk_refute nome "arquivo.cnf" "arquivo.lrat" (bloco := 400)

lê os dois arquivos (caminho relativo ao `.lean`), e declara, dentro do namespace `nome`:

* `F` : a fórmula como `List (List Nat)` (concatenação de pedaços `F_i`, para o kernel não estourar
  a pilha ao conferir listas longas);
* `db` : a árvore com as cláusulas originais (chaves `1..n`) e as derivadas, renumeradas
  `n+1, n+2, …` (subárvores em declarações separadas);
* `okF_i`, `ok_i` : um teorema por pedaço, cada um provado por `decide +kernel`
  (o termo `of_decide_eq_true (Eq.refl true)`, conferido pelo kernel);
* `unsat : LratK.Unsat F`.

Nada aqui precisa de confiança: o elaborador só monta dados e termos; o kernel confere tudo, e
a correção é `LratK.unsat_of_chain`. Passos de deleção são ignorados (o banco nunca apaga), e
dicas negativas (RAT) fazem o comando falhar.
-/

namespace LratK

theorem good_one (db : Tree) (v : Nat → Bool) : Good db v 1 :=
  fun i _ h0 hi _ => absurd hi (by omega)

/-- `checkF` em pedaços. -/
theorem good_of_checkF' {db : Tree} {v : Nat → Bool} (A : List (List Nat)) (k : Nat)
    (hg : Good db v k) (hchk : checkF db A k = true) (hA : ∀ c ∈ A, ClauseSat v c) :
    Good db v (k + A.length) := by
  intro i c h0 hi hc
  by_cases hik : i < k
  · exact hg i c h0 hik hc
  · exact checkF_sound A k hchk hA i c (by omega) hi hc

theorem unsat_of_chain {db : Tree} {F : List (List Nat)} {K : Nat}
    (hsteps : ∀ v : Nat → Bool, (∀ c ∈ F, ClauseSat v c) → Good db v (K + 1))
    (hK : 0 < K) (hempty : db.get K = some []) : Unsat F := by
  intro v
  refine Classical.byContradiction fun hn => ?_
  have hn' : ∀ c ∈ F, ClauseSat v c := fun c hc =>
    Classical.byContradiction fun h => hn ⟨c, hc, h⟩
  obtain ⟨l, hl, _⟩ := hsteps v hn' K [] hK (Nat.lt_succ_self K) hempty
  simp at hl

theorem forall_mem_append_left {p : List Nat → Prop} {A B : List (List Nat)}
    (h : ∀ c ∈ A ++ B, p c) : ∀ c ∈ A, p c := fun c hc => h c (List.mem_append_left _ hc)

theorem forall_mem_append_right {p : List Nat → Prop} {A B : List (List Nat)}
    (h : ∀ c ∈ A ++ B, p c) : ∀ c ∈ B, p c := fun c hc => h c (List.mem_append_right _ hc)

/-- Igualdade booleana de listas de cláusulas. -/
noncomputable def listsBeq (xs : List (List Nat)) : List (List Nat) → Bool :=
  List.rec (motive := fun _ => List (List Nat) → Bool)
    (fun ys => List.rec (motive := fun _ => Bool) true (fun _ _ _ => false) ys)
    (fun x _ ih ys => List.rec (motive := fun _ => Bool) false
      (fun y ys' _ => listBeq x y && ih ys') ys) xs

theorem listsBeq_eq : ∀ (xs ys : List (List Nat)), listsBeq xs ys = true → xs = ys := by
  intro xs
  induction xs with
  | nil =>
    intro ys h
    cases ys with
    | nil => rfl
    | cons y ys => cases h
  | cons x xs ih =>
    intro ys h
    cases ys with
    | nil => cases h
    | cons y ys =>
      change (listBeq x y && listsBeq xs ys) = true at h
      rw [Bool.and_eq_true] at h
      rw [listBeq_eq x y h.1, ih ys h.2]

theorem unsat_of_listsBeq {F G : List (List Nat)} (hF : Unsat F) (h : listsBeq F G = true) :
    Unsat G := listsBeq_eq F G h ▸ hF

open Lean Elab Command Meta

private def encLit (x : Int) : Nat := if x > 0 then 2 * x.toNat else 2 * (-x).toNat + 1

private def lnat : Expr := mkApp (mkConst ``List [0]) (mkConst ``Nat)
private def llnat : Expr := mkApp (mkConst ``List [0]) lnat

private def natList (xs : List Nat) : Expr :=
  xs.foldr (fun n acc => mkApp3 (mkConst ``List.cons [0]) (mkConst ``Nat) (mkRawNatLit n) acc)
    (mkApp (mkConst ``List.nil [0]) (mkConst ``Nat))

private def listOf (ty : Expr) (xs : Array Expr) : Expr :=
  xs.foldr (fun e acc => mkApp3 (mkConst ``List.cons [0]) ty e acc) (mkApp (mkConst ``List.nil [0]) ty)

/-- Lê um arquivo DIMACS/LRAT texto: uma linha de inteiros por linha útil. Pula comentários
(`c`), o cabeçalho (`p`) e as linhas de deleção do LRAT (`<id> d …`). Parser por bytes: a versão
com `String.splitOn` gastava ~7 GB de memória num LRAT de 5 MB (medido). -/
private def parseFile (b : ByteArray) : Array (Array Int) := Id.run do
  let mut out : Array (Array Int) := #[]
  let mut cur : Array Int := #[]
  let mut num : Nat := 0
  let mut neg := false
  let mut inNum := false
  let mut skip := false
  for i in [0:b.size] do
    let c := b.get! i
    if c == 10 then
      if inNum then cur := cur.push (if neg then -(num : Int) else num)
      if !skip && cur.size > 0 then out := out.push cur
      cur := #[]; num := 0; neg := false; inNum := false; skip := false
    else if skip then
      pure ()
    else if 48 ≤ c && c ≤ 57 then
      num := num * 10 + (c.toNat - 48); inNum := true
    else if c == 45 then
      neg := true
    else if c == 32 || c == 9 || c == 13 then
      if inNum then cur := cur.push (if neg then -(num : Int) else num)
      num := 0; neg := false; inNum := false
    else
      -- `c`/`p` no início da linha, ou `d` depois do id: linha ignorada
      skip := true
  if inNum then cur := cur.push (if neg then -(num : Int) else num)
  if !skip && cur.size > 0 then out := out.push cur
  return out

private def addDef (n : Name) (ty val : Expr) : CoreM Unit :=
  addDecl <| Declaration.defnDecl
    { name := n, levelParams := [], type := ty, value := val, hints := .regular 0, safety := .safe }

private def addThm (n : Name) (ty val : Expr) : CoreM Unit :=
  addDecl <| Declaration.thmDecl { name := n, levelParams := [], type := ty, value := val }

/-- Prova por reflexão de `b = true`: o que `decide +kernel` gera. -/
private def reflTrue (b : Expr) : Expr :=
  let p := mkApp3 (mkConst ``Eq [1]) (mkConst ``Bool) b (mkConst ``Bool.true)
  mkApp3 (mkConst ``of_decide_eq_true) p
    (mkApp2 (mkConst ``instDecidableEqBool) b (mkConst ``Bool.true))
    (mkApp2 (mkConst ``Eq.refl [1]) (mkConst ``Bool) (mkConst ``Bool.true))

/-- Declara a árvore; subárvores abaixo da profundidade `cut` viram declarações próprias. -/
private partial def treeDecls (base : Name) (cut : Nat) (cnt : IO.Ref Nat) :
    Nat → Tree → CoreM Expr
  | _, .leaf => pure (mkConst ``Tree.leaf)
  | d, .node l v r => do
    let le ← treeDecls base cut cnt (d + 1) l
    let re ← treeDecls base cut cnt (d + 1) r
    let ve := match v with
      | none => mkApp (mkConst ``Option.none [0]) lnat
      | some c => mkApp2 (mkConst ``Option.some [0]) lnat (natList c)
    let e := mkApp3 (mkConst ``Tree.node) le ve re
    if d == cut then
      let i ← cnt.modifyGet fun i => (i, i + 1)
      let n := base ++ Name.mkSimple s!"t{i}"
      addDef n (mkConst ``Tree) e
      pure (mkConst n)
    else pure e

syntax "lratk_refute " ident str str (num)? (" for " term)? : command

elab_rules : command
  | `(lratk_refute $ns:ident $cnf:str $lrat:str $[$bl:num]? $[for $ft:term]?) => do
  let fTerm? ← ft.mapM fun stx => liftTermElabM do
    let e ← Term.elabTerm stx (some (mkApp (mkConst ``List [0]) (mkApp (mkConst ``List [0]) (mkConst ``Nat))))
    Term.synthesizeSyntheticMVarsNoPostponing
    instantiateMVars e
  let bloco := (bl.map (·.getNat)).getD 400
  let fn ← getFileName
  let dir := (System.FilePath.mk fn).parent.get!
  let cnfL := parseFile (← IO.FS.readBinFile (dir / cnf.getString))
  let lratL := parseFile (← IO.FS.readBinFile (dir / lrat.getString))
  let base := (← getCurrNamespace) ++ ns.getId
  -- fórmula
  let mut db : Tree := .leaf
  let mut cls : Array (List Nat) := #[]
  for xs in cnfL do
    let c := (xs.toList.takeWhile (· != 0)).map encLit
    cls := cls.push c
    db := db.ins 64 cls.size c
  let n := cls.size
  -- prova: renumera as cláusulas derivadas para n+1, n+2, …
  let mut ren : Std.HashMap Nat Nat := {}
  let mut k := n
  let mut steps : Array (List Nat) := #[]
  let mut last : List Nat := [0]
  for xs in lratL do
    let rest := xs.toList.drop 1
    let c := rest.takeWhile (· != 0)
    let h := (rest.drop (c.length + 1)).takeWhile (· != 0)
    if h.any (· < 0) then throwError "dica negativa (RAT) não suportada"
    k := k + 1
    ren := ren.insert xs[0]!.toNat k
    last := c.map encLit
    db := db.ins 64 k last
    steps := steps.push (h.map fun x => if x ≤ (n : Int) then x.toNat else ren.getD x.toNat 0)
    if c.isEmpty then break
  unless last.isEmpty do throwError "a prova não termina na cláusula vazia"
  let K := k
  liftCoreM do
    let t0 ← IO.monoMsNow
    -- a árvore
    let cnt ← IO.mkRef 0
    let dbE ← treeDecls base 8 cnt 0 db
    let dbN := base ++ `db
    addDef dbN (mkConst ``Tree) dbE
    let dbC := mkConst dbN
    -- a fórmula, em pedaços
    let mut fNames : Array Name := #[]
    for j in [0:(n + bloco - 1) / bloco] do
      let nm := base ++ Name.mkSimple s!"F{j}"
      addDef nm llnat (listOf lnat ((cls.extract (j * bloco) ((j + 1) * bloco)).map natList))
      fNames := fNames.push nm
    let fE := fNames.foldr (fun nm acc =>
        if acc.isAppOf ``List.nil then mkConst nm
        else mkApp3 (mkConst ``List.append [0]) lnat (mkConst nm) acc)
      (mkApp (mkConst ``List.nil [0]) lnat)
    let fN := base ++ `F
    addDef fN llnat fE
    let t1 ← IO.monoMsNow
    -- teoremas por pedaço
    let mut fOk : Array Name := #[]
    for j in [0:fNames.size] do
      let nm := base ++ Name.mkSimple s!"okF{j}"
      let b := mkApp3 (mkConst ``checkF) dbC (mkConst fNames[j]!) (mkRawNatLit (1 + j * bloco))
      addThm nm (mkApp3 (mkConst ``Eq [1]) (mkConst ``Bool) b (mkConst ``Bool.true)) (reflTrue b)
      fOk := fOk.push nm
    let t2 ← IO.monoMsNow
    let mut hNames : Array (Name × Nat) := #[]
    let mut times : Array Nat := #[]
    for j in [0:(steps.size + bloco - 1) / bloco] do
      let hn := base ++ Name.mkSimple s!"H{j}"
      addDef hn llnat (listOf lnat ((steps.extract (j * bloco) ((j + 1) * bloco)).map natList))
      let k0 := n + 1 + j * bloco
      let nm := base ++ Name.mkSimple s!"ok{j}"
      let b := mkApp3 (mkConst ``checkRange) dbC (mkConst hn) (mkRawNatLit k0)
      let s ← IO.monoMsNow
      addThm nm (mkApp3 (mkConst ``Eq [1]) (mkConst ``Bool) b (mkConst ``Bool.true)) (reflTrue b)
      times := times.push ((← IO.monoMsNow) - s)
      hNames := hNames.push (hn, k0)
    let t3 ← IO.monoMsNow
    -- montagem: ∀ v, (∀ c ∈ F, sat) → Good db v (K+1)
    let v := mkFVar ⟨`v⟩
    let hF := mkFVar ⟨`hF⟩
    let sat := mkApp (mkConst ``ClauseSat) v
    -- hipóteses de cada pedaço de F, descendo pela concatenação à direita
    let mut rest := hF
    let mut restTy := fE
    let mut g := mkApp2 (mkConst ``good_one) dbC v
    let mut kk := 1
    for j in [0:fNames.size] do
      let Fj := mkConst fNames[j]!
      let hA ← if j + 1 == fNames.size then pure rest else do
        let tail := restTy.appArg!
        let hA := mkApp4 (mkConst ``forall_mem_append_left) sat Fj tail rest
        rest := mkApp4 (mkConst ``forall_mem_append_right) sat Fj tail rest
        restTy := tail
        pure hA
      g := mkAppN (mkConst ``good_of_checkF') #[dbC, v, Fj, mkRawNatLit kk, g, mkConst fOk[j]!, hA]
      kk := kk + (cls.extract (j * bloco) ((j + 1) * bloco)).size
    for j in [0:hNames.size] do
      let (hn, k0) := hNames[j]!
      g := mkAppN (mkConst ``good_of_checkRange) #[dbC, v, mkConst hn, mkRawNatLit k0, g,
        mkConst (base ++ Name.mkSimple s!"ok{j}")]
    let hstepsTy := mkForall `v .default (mkForall `_n .default (mkConst ``Nat) (mkConst ``Bool))
      (mkForall `hF .default
        (mkForall `c .default lnat
          (mkForall `_h .default (mkApp5 (mkConst ``Membership.mem [0, 0]) lnat llnat
              (mkApp (mkConst ``List.instMembership [0]) lnat) (mkConst fN) (mkBVar 0))
            (mkApp2 (mkConst ``ClauseSat) (mkBVar 2) (mkBVar 1))))
        (mkApp3 (mkConst ``Good) dbC (mkBVar 1) (mkRawNatLit (K + 1))))
    let hsteps := (g.abstract #[v, hF])
    let hstepsV := mkLambda `v .default (mkForall `_n .default (mkConst ``Nat) (mkConst ``Bool))
      (mkLambda `hF .default
        (mkForall `c .default lnat
          (mkForall `_h .default (mkApp5 (mkConst ``Membership.mem [0, 0]) lnat llnat
              (mkApp (mkConst ``List.instMembership [0]) lnat) (mkConst fN) (mkBVar 0))
            (mkApp2 (mkConst ``ClauseSat) (mkBVar 2) (mkBVar 1))))
        hsteps)
    let hsN := base ++ `steps
    addThm hsN hstepsTy hstepsV
    -- 0 < K e a cláusula vazia na chave K
    let hKty := mkApp4 (mkConst ``LT.lt [0]) (mkConst ``Nat) (mkConst ``instLTNat) (mkRawNatLit 0)
      (mkRawNatLit K)
    let hK := mkApp3 (mkConst ``of_decide_eq_true) hKty
      (mkApp2 (mkConst ``Nat.decLt) (mkRawNatLit 0) (mkRawNatLit K))
      (mkApp2 (mkConst ``Eq.refl [1]) (mkConst ``Bool) (mkConst ``Bool.true))
    let optl := mkApp (mkConst ``Option [0]) lnat
    let lhs := mkApp2 (mkConst ``Tree.get) dbC (mkRawNatLit K)
    let rhs := mkApp2 (mkConst ``Option.some [0]) lnat (mkApp (mkConst ``List.nil [0]) (mkConst ``Nat))
    let heTy := mkApp3 (mkConst ``Eq [1]) optl lhs rhs
    let decL := mkApp2 (mkConst ``instDecidableEqList [0]) (mkConst ``Nat) (mkConst ``instDecidableEqNat)
    let he := mkApp3 (mkConst ``of_decide_eq_true) heTy
      (mkAppN (mkConst ``Option.instDecidableEq [0]) #[lnat, decL, lhs, rhs])
      (mkApp2 (mkConst ``Eq.refl [1]) (mkConst ``Bool) (mkConst ``Bool.true))
    let uN := base ++ `unsat
    addThm uN (mkApp (mkConst ``Unsat) (mkConst fN))
      (mkAppN (mkConst ``unsat_of_chain) #[dbC, mkConst fN, mkRawNatLit K, mkConst hsN, hK, he])
    -- a mesma refutação para a fórmula dada como termo (ex.: o gerador `K742Cnf.cnf`)
    if let some fT := fTerm? then
      let b := mkApp2 (mkConst ``listsBeq) (mkConst fN) fT
      let eqN := base ++ `eqF
      addThm eqN (mkApp3 (mkConst ``Eq [1]) (mkConst ``Bool) b (mkConst ``Bool.true)) (reflTrue b)
      addThm (base ++ `unsatFor) (mkApp (mkConst ``Unsat) fT)
        (mkAppN (mkConst ``unsat_of_listsBeq) #[mkConst fN, fT, mkConst uN, mkConst eqN])
    let t4 ← IO.monoMsNow
    let tot := times.foldl (· + ·) 0
    let mx := times.foldl max 0
    logInfo m!"{n} cláusulas, {steps.size} passos, chave final {K}; {hNames.size} blocos de {bloco}; \
      dados {t1 - t0} ms, checkF {t2 - t1} ms, passos {t3 - t2} ms (maior bloco {mx} ms, soma {tot} ms), \
      montagem {t4 - t3} ms (tempos do elaborador; a checagem do kernel é assíncrona e não entra)"

end LratK

#print axioms LratK.good_of_checkF'
#print axioms LratK.unsat_of_chain
#print axioms LratK.unsat_of_listsBeq
