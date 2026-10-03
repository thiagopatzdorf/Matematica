"""Hipóteses refutadas: a biblioteca, a campanha e o texto público não podem discordar sobre o que é falso.

Nasceu da autópsia do único claim REFUTED da campanha (`h2-gap-nondecreasing`, 2026-10-03): `A6_Finite.lean` refutava H1, H3 e H5 desde o
início e a campanha só sabia de H2, então a evidência negativa de três hipóteses existia no Lean e não existia no sistema. Cada teste descreve a
falha que impede. Só lê arquivos (sem Lean, sem a infraestrutura da Fábrica).
"""
import glob
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMP = os.path.join(ROOT, "campaigns", "covering-codes")

# Ordem dos estados de verdade (factory_cauteloso.matematica.model.ESTADOS); REFUTED é terminal e fica fora da escada.
ESCADA = ["IDEA", "CONJECTURE", "EMPIRICAL", "EXHAUSTIVE_BOUNDED", "INDEPENDENTLY_REPRODUCED", "PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED"]
MARCADOR_DE_REFUTACAO = re.compile(r"refut|contra-?\s?exemplo|counter-?example|\bfals[ao]s?\b|\bfalse\b|REFUTED", re.I)
# Como cada hipótese refutada costuma ser reescrita em prosa (afirmada como verdadeira). Se uma nova hipótese for refutada, acrescente a linha
# aqui: o teste `test_every_refuted_hypothesis_has_a_prose_pattern` falha enquanto faltar.
PARAFRASES = {
    1: re.compile(r"α.{0,120}(n[ãa]o[- ]crescente|non-?increasing)", re.I | re.S),
    2: re.compile(r"gap.{0,160}(n[ãa]o[- ]decrescente|non-?decreasing|monot[oó]n|monotone)", re.I | re.S),
    3: re.compile(r"α\s*(≤|<=|\\le)\s*2\b"),
    5: re.compile(r"(⌈|ceil).{0,60}(s[óo]|apenas|only).{0,80}perfeit", re.I | re.S),
}


def carregar(pasta):
    out = {}
    for p in sorted(glob.glob(os.path.join(CAMP, pasta, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            out[os.path.basename(p)[:-5]] = json.load(fh)
    return out


def hipoteses_refutadas_no_lean():
    """{n: [(arquivo, teorema)]} para todo `theorem H<n>_counterexample*` / `H<n>_unconditional*` em CoveringLean/*.lean."""
    achados = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "CoveringLean", "*.lean"))):
        with open(p, encoding="utf-8") as fh:
            texto = fh.read()
        for m in re.finditer(r"^(?:theorem|lemma)\s+((?:\w+\.)*H(\d+)_(?:counterexample|unconditional)\w*)", texto, re.M):
            achados.setdefault(int(m.group(2)), []).append((os.path.basename(p), m.group(1)))
    return achados


def numero_da_hipotese(claim):
    m = re.match(r"H(\d+):", claim.get("statement", ""))
    return int(m.group(1)) if m else None


def afirma_hipotese_refutada_sem_dizer(texto, refutadas):
    """Parágrafos que citam `H<n>` ou reescrevem a hipótese em prosa SEM nenhuma palavra de refutação no mesmo parágrafo."""
    problemas = []
    for par in re.split(r"\n\s*\n", texto):
        if MARCADOR_DE_REFUTACAO.search(par):
            continue
        for n in refutadas:
            if re.search(rf"\bH{n}\b", par):
                problemas.append((n, "cita H%d sem dizer que foi refutada" % n, par.strip()[:160]))
            elif n in PARAFRASES and PARAFRASES[n].search(par):
                problemas.append((n, "afirma o conteúdo de H%d como verdadeiro" % n, par.strip()[:160]))
    return problemas


class RefutedHypothesesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claims = carregar("claims")
        cls.formal = carregar("formal")
        cls.refutadas = {numero_da_hipotese(c): cid for cid, c in cls.claims.items() if c["status"] == "REFUTED" and numero_da_hipotese(c)}

    def test_every_hypothesis_the_lean_library_refutes_is_a_refuted_claim_with_a_measured_counterexample(self):
        # falha que impede: A6_Finite refutava H1/H3/H5 e a campanha não tinha o claim (evidência negativa só no Lean)
        no_lean = hipoteses_refutadas_no_lean()
        self.assertTrue(no_lean, "nenhum H<n>_counterexample em CoveringLean/*.lean: o padrão do teste envelheceu")
        for n, teoremas in sorted(no_lean.items()):
            with self.subTest(hipotese="H%d" % n, teoremas=teoremas):
                self.assertIn(n, self.refutadas, f"H{n} é refutada em {teoremas} e não há claim REFUTED com enunciado 'H{n}:' na campanha")
                cl = self.claims[self.refutadas[n]]
                self.assertEqual(cl["kind"], "conjecture")
                self.assertTrue(cl["evidence"]["counterexamples"], "REFUTED sem contraexemplo registrado")
                registros = [self.formal[f] for f in cl["evidence"]["formal"]]
                casam = [r for r in registros if r["theorem"].startswith(f"CoveringA6.H{n}_counterexample")]
                self.assertTrue(casam, f"o claim H{n} não aponta para o registro formal do teorema H{n}_counterexample*")
                for r in casam:
                    self.assertEqual(r["axioms_status"], "OK")
                    self.assertTrue(r["sorry_free"])
                    self.assertTrue(set(r["axioms"]) <= {"propext", "Classical.choice", "Quot.sound"})

    def test_every_refuted_claim_is_an_hypothesis_that_a_lean_theorem_refutes(self):
        # o inverso: claim REFUTED sem teorema no Lean seria refutação só de texto
        no_lean = hipoteses_refutadas_no_lean()
        for n, cid in self.refutadas.items():
            with self.subTest(claim=cid):
                self.assertIn(n, no_lean)

    def test_every_refuted_hypothesis_has_a_prose_pattern(self):
        faltam = sorted(set(self.refutadas) - set(PARAFRASES))
        self.assertEqual(faltam, [], f"hipóteses refutadas sem paráfrase em PARAFRASES (o teste de texto público não as pegaria): {faltam}")

    def test_public_text_never_states_a_refuted_hypothesis_as_true(self):
        # README, nota e docs não podem reintroduzir H2 (ou H1/H3/H5) como se valesse; o paper é só lido (publicação: mudança é do dono)
        arquivos = [os.path.join(ROOT, "README.md"), os.path.join(ROOT, "nota.md"), os.path.join(ROOT, "paper", "main.tex")]
        arquivos += sorted(glob.glob(os.path.join(ROOT, "docs", "*.md")))
        for p in arquivos:
            if not os.path.isfile(p):
                continue
            with open(p, encoding="utf-8") as fh:
                texto = fh.read()
            for n, motivo, trecho in afirma_hipotese_refutada_sem_dizer(texto, self.refutadas):
                self.fail(f"{os.path.relpath(p, ROOT)}: {motivo}: «{trecho}»")

    def test_the_prose_check_catches_h2_reintroduced_as_true(self):
        # controle positivo: sem ele o teste acima poderia passar por não enxergar nada
        refutadas = [1, 2, 3, 5]
        for frase in ("Sabemos que o gap K_q(n,R) − ⌈esfera⌉ é não decrescente em n.",
                      "H2 vale: o gap cresce.",
                      "The gap K - ceil(S) is nondecreasing in n.",
                      "H1: α é não crescente em n.",
                      "Por H3, α ≤ 2 sempre."):
            with self.subTest(frase=frase):
                self.assertTrue(afirma_hipotese_refutada_sem_dizer(frase, refutadas))
        for frase in ("`H2_counterexample_uncond` refuta H2 (o gap é não decrescente) sem hipótese.",
                      "H2 é falsa: o gap não é não decrescente.",
                      "Texto sem relação com nenhuma hipótese."):
            with self.subTest(frase=frase):
                self.assertFalse(afirma_hipotese_refutada_sem_dizer(frase, refutadas))

    def test_no_claim_at_or_above_empirical_depends_on_a_refuted_claim_directly_or_through_others(self):
        # base refutada contamina tudo que se apoia nela; a guarda de promoção só olha dependência direta, aqui confere-se o fecho
        refutados = {cid for cid, c in self.claims.items() if c["status"] == "REFUTED"}
        self.assertTrue(refutados)

        def fecho(cid, visto):
            for d in self.claims[cid]["depends_on"]:
                self.assertIn(d, self.claims, f"{cid} depende de {d}, que não existe")
                if d not in visto:
                    visto.add(d)
                    fecho(d, visto)
            return visto

        for cid, cl in self.claims.items():
            if cl["status"] in ESCADA and ESCADA.index(cl["status"]) >= ESCADA.index("EMPIRICAL"):
                with self.subTest(claim=cid, status=cl["status"]):
                    self.assertFalse(fecho(cid, set()) & refutados, f"{cid} ({cl['status']}) depende de claim REFUTED")


if __name__ == "__main__":
    unittest.main()
