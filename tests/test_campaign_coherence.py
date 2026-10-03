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
        for rid in ("res-keri-edition-unidentified", "res-lb-264-source-unidentified"):
            self.assertIn(rid, self.residuals)
            self.assertTrue(set(self.residuals[rid]["instances"]) <= universo)
            self.assertIn("fonte não identificada", self.residuals[rid]["reason"])

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
