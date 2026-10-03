"""Coerência dos registros da campanha `covering-codes` (campaigns/covering-codes/) com o contrato de verificação do red team.

Só lê JSON (sem a infraestrutura da Fábrica): cada teste descreve a falha que impede, não a função.
"""
import glob
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMP = os.path.join(ROOT, "campaigns", "covering-codes")


def carregar(pasta):
    out = {}
    for p in sorted(glob.glob(os.path.join(CAMP, pasta, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            out[os.path.basename(p)[:-5]] = json.load(fh)
    return out


class CampaignCoherenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.witnesses = carregar("witnesses")
        cls.claims = carregar("claims")
        cls.verifiers = carregar("verifiers")
        cls.runs = carregar("verifier_runs")
        cls.residuals = carregar("residuals")
        cls.literature = carregar("literature")
        with open(os.path.join(CAMP, "campaign.json"), encoding="utf-8") as fh:
            cls.meta = json.load(fh)

    def test_every_witness_declares_the_instance_it_belongs_to_and_the_file_name_agrees(self):
        # sem `parameters` o witness não diz de qual instância é; o nome do arquivo não pode contradizê-lo
        self.assertTrue(self.witnesses)
        for wid, w in self.witnesses.items():
            with self.subTest(witness=wid):
                self.assertEqual(w.get("parameters"), {"q": w["q"], "n": w["n"], "R": w["R"], "M": w["M"]})
                m = re.search(r"q(\d+)_n(\d+)_R(\d+)_M(\d+)\.txt$", w["path"])
                self.assertEqual(tuple(int(x) for x in m.groups()), (w["q"], w["n"], w["R"], w["M"]))

    def test_claim_parameters_equal_the_witness_parameters_and_the_bound(self):
        for cid, cl in self.claims.items():
            for wid in cl["evidence"]["witnesses"]:
                with self.subTest(claim=cid, witness=wid):
                    p = cl["scope"].get("parameters")
                    self.assertEqual(p, self.witnesses[wid]["parameters"])
                    if cl.get("bound"):  # igualdade (K = 12) não tem bound; as cotas têm: valor = M, parâmetros = q,n,R
                        self.assertEqual(cl["bound"]["value"], p["M"])
                        self.assertEqual(cl["bound"]["parameters"], {k: p[k] for k in "qnR"})

    def test_no_claim_with_witnesses_in_evidence_is_proved_without_two_independent_verifiers(self):
        # PROVED ou INDEPENDENTLY_REPRODUCED com witness exige 2 verificadores de autores distintos E distintos de quem criou o claim
        for cid, cl in self.claims.items():
            if cl["evidence"]["witnesses"] and cl["status"] in ("PROVED", "INDEPENDENTLY_REPRODUCED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED"):
                autores = {v["implemented_by"] for v in self.verifiers.values()
                           if v.get("implemented_by") and v["implemented_by"].strip().lower() != cl["created_by"].strip().lower()}
                self.assertGreaterEqual(len(autores), 2, f"{cid} está {cl['status']} sem 2 autores de verificador distintos do criador")

    def test_verifiers_have_real_distinct_authors_distinct_groups_and_receive_the_parameters(self):
        self.assertGreaterEqual(len(self.verifiers), 2)
        for vid, v in self.verifiers.items():
            with self.subTest(verifier=vid):
                self.assertTrue((v.get("implemented_by") or "").strip(), "sem implemented_by: independência seria só rótulo")
                cmd = " ".join(v["command"])
                for k in "qnRM":
                    self.assertIn("{param:%s}" % k, cmd, "o verificador precisaria ler o parâmetro do nome do arquivo")
                self.assertEqual(v["fail_exit_codes"], [1, 2], "FAIL = 1 (descoberto) e 2 (contradição); 3 é ERRO")
        self.assertEqual(len({v["implemented_by"].strip().lower() for v in self.verifiers.values()}), len(self.verifiers))
        self.assertEqual(len({v["independence_group"] for v in self.verifiers.values()}), len(self.verifiers))

    def test_latest_run_of_every_verifier_on_every_witness_passed_the_claim_parameters_and_records_the_verifier_hash(self):
        ultimas = {}
        for r in sorted(self.runs.values(), key=lambda r: (r["ts"], r["run_id"])):
            ultimas[(r["verifier_id"], r["subject_id"])] = r
        self.assertEqual(sorted(ultimas), sorted((v, w) for v in self.verifiers for w in self.witnesses))
        for (vid, wid), r in ultimas.items():
            with self.subTest(verifier=vid, witness=wid):
                self.assertEqual(r["result"], "PASS")
                self.assertTrue(r.get("verifier_sha256"))
                self.assertEqual(r["params_passed"], self.witnesses[wid]["parameters"])
                self.assertEqual(r["subject_sha256"], self.witnesses[wid]["sha256"])

    def test_literature_records_have_a_real_version_and_the_unsourced_numbers_are_declared_residuals(self):
        for lid, lit in self.literature.items():
            self.assertFalse(re.search(r"n[aã]o identificad|sem vers|n/a", lit["version"], re.I), f"{lid}: versão que diz que não há versão")
        universo = {i["id"] for i in self.meta["universe"]["instancias"]}
        for i in self.meta["universe"]["instancias"]:
            self.assertNotIn("lb_literatura_declarada", i, "número de paper sem registro de literatura não entra no universo")
        # Os dois resíduos "fonte não identificada" foram FECHADOS (2026-10-03) porque fonte, versão e data agora estão em literature/;
        # se alguém os reabrir sem tirar o registro, ou apagar o registro sem reabrir, isto falha.
        for rid in ("res-keri-edition-unidentified", "res-lb-264-source-unidentified"):
            self.assertNotIn(rid, self.residuals, f"{rid} está fechado: fonte e versão registradas")

    def test_the_keri_edition_and_the_264_source_are_registered_with_a_real_version_and_date(self):
        # 264 = Kéri 6-21_tables.pdf (PDF de 2009-10-15), e as 7 cotas "previous" do paper + o 1843 também são do Kéri
        k = self.literature["lit-keri-k7-9-4-lb"]
        self.assertEqual((k["bound"]["value"], k["bound"]["direction"]), (264, "lower"))
        self.assertEqual(k["version_date"], "2009-10-15")
        previous = {"k5-7-2": 525, "k4-10-4": 208, "k5-9-3": 1275, "k5-10-4": 875, "k5-9-5": 55, "k5-9-4": 255, "k7-8-3": 2337, "k7-9-4": 1843}
        for cel, v in previous.items():
            self.assertEqual(self.literature[f"lit-keri-{cel}-ub"]["bound"]["value"], v, cel)

    def test_marosi_history_for_k7_9_4_is_1743_then_1475_then_1475_with_each_version_dated(self):
        v = {lid: self.literature[lid] for lid in ("lit-marosi-2608-19872-v1", "lit-marosi-2608-19872-v2", "lit-marosi-2608-19872-v3")}
        self.assertEqual([(x["version"], x["version_date"], x["bound"]["value"]) for x in v.values()],
                         [("v1", "2026-08-20", 1743), ("v2", "2026-08-23", 1475), ("v3", "2026-09-02", 1475)])

    def test_stanton_kalbfleisch_is_a_cited_reference_never_a_paper_we_read(self):
        sk = self.literature["lit-stanton-kalbfleisch-1968"]
        self.assertFalse(sk["reproduced"])
        self.assertIn("NÃO foi lido", sk["exact_statement"])
        self.assertEqual(sk["date_read"], "2026-10-03")

    def test_every_upper_bound_claim_carries_its_literature_comparison_without_claiming_novelty(self):
        melhoras = 0
        for cid, cl in self.claims.items():
            if cl.get("bound", {}) and cl["bound"]["direction"] == "upper" and "-ub-" in cid:
                cmp_ = cl["literature_comparison"]
                self.assertIn(cmp_["classificacao"], ("MELHORA_APARENTE_A_CONFIRMAR", "PREDECESSOR_ENCONTRADO"), cid)
                self.assertNotIn("novidade confirmada", cmp_["nota"].lower())
                if cmp_["classificacao"] == "MELHORA_APARENTE_A_CONFIRMAR":
                    melhoras += 1
                    self.assertIn("a confirmar por revisão externa", cmp_["nota"], cid)
        self.assertEqual(melhoras, 10, "as 10 linhas MELHORA_APARENTE_A_CONFIRMAR de LITERATURA_CC.md")

    def test_each_apparent_improvement_cell_has_an_open_residual_naming_what_was_not_read(self):
        for cel in ("k7-9-4", "k7-8-3", "k5-7-2", "k4-10-4", "k5-9-3", "k5-10-4", "k5-9-5", "k5-9-4"):
            r = self.residuals[f"res-confirmar-{cel}"]
            self.assertEqual(r["instances"], [cel])
            self.assertIn("MELHORA_APARENTE_A_CONFIRMAR", r["reason"])
            self.assertRegex(r["reason"], r"(?i)n[ãa]o (foram |foi )?lid")
        self.assertIn("verify_cov.py", self.residuals["res-confirmar-k7-9-4"]["reason"])
        self.assertIn("l_5(6,4)", self.residuals["res-confirmar-k5-10-4"]["reason"])

    def test_every_residual_lists_its_instances_and_they_are_cells_of_the_universe(self):
        universo = {i["id"] for i in self.meta["universe"]["instancias"]}
        for rid, r in self.residuals.items():
            with self.subTest(residual=rid):
                self.assertIsInstance(r.get("instances"), list)
                self.assertTrue(set(r["instances"]) <= universo)
                if not r["instances"]:
                    self.assertTrue(r.get("instances_note"), "resíduo sem célula precisa dizer por quê")

    def test_the_audit_chain_has_a_versionable_anchor_of_a_head_that_exists(self):
        with open(os.path.join(CAMP, "audit", "log.jsonl"), encoding="utf-8") as fh:
            eventos = [json.loads(x) for x in fh if x.strip()]
        with open(os.path.join(CAMP, "audit", "anchors.jsonl"), encoding="utf-8") as fh:
            ancoras = [json.loads(x) for x in fh if x.strip()]
        self.assertTrue(ancoras)
        for a in ancoras:
            self.assertEqual(eventos[a["seq"] - 1]["hash"], a["hash"], "a âncora aponta para um evento que não é o do log")


if __name__ == "__main__":
    unittest.main()
