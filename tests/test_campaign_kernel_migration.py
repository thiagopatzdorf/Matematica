"""Migração dos 9 registros pesados (CoveringHeavy) para o eixo do kernel (kernel_runs/): cada teste descreve a falha que impede.

Lê JSON (como test_campaign_coherence). Os testes que comparam com a infraestrutura da Fábrica ou refazem a migração só rodam se
`factory_cauteloso` estiver no PYTHONPATH (skip explícito; o CI deste repositório não a tem).
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMP = os.path.join(ROOT, "campaigns", "covering-codes")
KR_ID = "kr-heavy-ddb16b7-lean-build2"
HEX64 = re.compile(r"[0-9a-f]{64}")
ESTADOS_DE_VERDADE = ("PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED")


def carregar(pasta):
    out = {}
    for p in sorted(glob.glob(os.path.join(CAMP, pasta, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            out[os.path.basename(p)[:-5]] = json.load(fh)
    return out


try:
    from factory_cauteloso.matematica import kernel as KERNEL
    from factory_cauteloso.matematica.store import Campanha
except ImportError:  # CI deste repositório: sem a infraestrutura
    KERNEL = None


class KernelRunMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claims = carregar("claims")
        cls.formal = carregar("formal")
        cls.runs = carregar("kernel_runs")
        with open(os.path.join(CAMP, "_fatos", "medicao_heavy_vm.json"), encoding="utf-8") as fh:
            cls.vm = json.load(fh)
        cls.pesados = {fid: f for fid, f in cls.formal.items() if fid.startswith("f-heavy-") or fid == "f-k2-6-1-eq12"}
        cls.kr = cls.runs.get(KR_ID)

    def test_the_nine_heavy_formal_records_are_exactly_the_ones_pointing_to_the_historical_run(self):
        self.assertEqual(len(self.pesados), 9)
        self.assertEqual({fid for fid, f in self.formal.items() if f.get("kernel_run")}, set(self.pesados))
        for fid, f in self.pesados.items():
            self.assertEqual(f["kernel_run"], KR_ID, fid)

    def test_the_historical_run_is_recorded_as_a_report_without_inventing_a_persisted_log_or_a_full_hash(self):
        self.assertIsNotNone(self.kr)
        lg = self.kr["raw_log"]
        self.assertIs(lg["persisted"], False)
        self.assertIsNone(lg["sha256"], "não há hash de 64 hex do log: não se fabrica")
        self.assertIsNone(lg["uri"])
        self.assertEqual(lg["sha256_prefix"], self.vm["sha256_prefixo_log_completo"])
        self.assertEqual(len(lg["sha256_prefix"]), 16)
        for k, v in lg.items():
            self.assertFalse(isinstance(v, str) and HEX64.fullmatch(v), f"raw_log.{k} parece um sha256 completo inventado")

    def test_the_historical_run_copies_the_recorded_evidence_and_nothing_more(self):
        kr, vm = self.kr, self.vm
        self.assertEqual(kr["commit_sha"], vm["repo_commit"])
        self.assertEqual(kr["lean_version"], vm["lean"])
        self.assertEqual((kr["started_at"], kr["finished_at"]), (vm["inicio_utc"], vm["fim_utc"]))
        self.assertEqual(kr["build"], {"status": "OK", "jobs": vm["jobs_final"], "leaves": vm["folhas_ok"], "failures": vm["folhas_falhou"]})
        self.assertEqual((kr["sorry_count"], kr["native_decide_count"]), (vm["sorry_no_log"], vm["native_decide_ou_ofReduceBool_no_log"]))
        self.assertEqual(kr["target"], "CoveringHeavy")
        self.assertEqual(kr["host"]["id"], "lean-build2")
        self.assertIs(kr["independent_reproduction"], False)
        self.assertEqual(sorted(kr["axioms_allowlist"]), ["Classical.choice", "Quot.sound", "propext"])
        por = {t["teorema"]: t["axiomas"] for t in vm["teoremas"]}
        self.assertEqual({t["theorem"]: t["axioms"] for t in kr["theorems"]}, por)
        for t in kr["theorems"]:
            self.assertIsNone(t["print_axioms_output"], "a saída literal de #print axioms não foi guardada: não se reconstrói")

    def test_no_level_or_boolean_summary_is_stored_in_the_run(self):
        for k in ("level", "nivel", "status", "kernel_verified", "proved", "verified", "independently_reproduced"):
            self.assertNotIn(k, self.kr)

    def test_every_claim_using_a_heavy_record_is_covered_by_the_run_and_none_changed_state(self):
        usam = {cid for cid, cl in self.claims.items()
                if any(f in self.pesados for f in cl["evidence"]["formal"] + cl.get("complementary_formal", []))}
        self.assertEqual(usam, set(self.kr["claim_ids"]))
        self.assertEqual(len(usam), 10)
        esperado = {"k4-10-4-ub-192": "INDEPENDENTLY_REPRODUCED", "k5-10-4-ub-625": "INDEPENDENTLY_REPRODUCED", "k5-7-2-ub-500": "INDEPENDENTLY_REPRODUCED",
                    "k5-9-3-ub-1250": "INDEPENDENTLY_REPRODUCED", "k5-9-4-ub-250": "INDEPENDENTLY_REPRODUCED", "k5-9-5-ub-50": "INDEPENDENTLY_REPRODUCED",
                    "k7-8-3-ub-1893": "INDEPENDENTLY_REPRODUCED", "k7-9-4-ub-1351": "PROVED", "k2-6-1-eq-12": "EXHAUSTIVE_BOUNDED",
                    "k2-6-1-lb-12": "EXHAUSTIVE_BOUNDED"}
        self.assertEqual({c: self.claims[c]["status"] for c in usam}, esperado, "migração conservadora: nenhum estado de claim muda")
        resumo = {}
        for cl in self.claims.values():
            resumo[cl["status"]] = resumo.get(cl["status"], 0) + 1
        self.assertEqual(resumo, {"PROVED": 21, "INDEPENDENTLY_REPRODUCED": 7, "EXHAUSTIVE_BOUNDED": 2, "REFUTED": 4})

    def test_the_heavy_formal_records_still_do_not_pass_the_local_guard_so_nothing_was_promoted_by_transcription(self):
        for fid, f in self.pesados.items():
            self.assertIsNone(f["axioms"], fid)
            self.assertIs(f["clean_build"], False, fid)
            self.assertTrue(f["validation_problems"], fid)

    def test_each_theorem_of_a_covered_claim_is_in_the_run_with_the_same_source_hash_as_the_formal_record(self):
        por = {t["theorem"]: t for t in self.kr["theorems"]}
        for cid in self.kr["claim_ids"]:
            for fid in self.claims[cid]["evidence"]["formal"] + self.claims[cid].get("complementary_formal", []):
                if fid in self.pesados:
                    f = self.formal[fid]
                    with self.subTest(claim=cid, formal=fid):
                        self.assertIn(f["theorem"], por)
                        self.assertEqual(por[f["theorem"]]["source_sha256"], f["source_sha256"])

    @unittest.skipUnless(shutil.which("git") and os.path.isdir(os.path.join(ROOT, ".git")), "sem git")
    def test_source_hashes_in_the_run_are_what_git_says_the_verified_commit_contained(self):
        if subprocess.run(["git", "cat-file", "-e", self.kr["commit_sha"]], cwd=ROOT, capture_output=True).returncode != 0:
            self.skipTest("clone raso: o commit verificado não está no histórico local")
        for t in self.kr["theorems"]:
            r = subprocess.run(["git", "show", f"{self.kr['commit_sha']}:{t['source_file']}"], cwd=ROOT, capture_output=True)
            self.assertEqual(r.returncode, 0, t["source_file"])
            self.assertEqual(hashlib.sha256(r.stdout).hexdigest(), t["source_sha256"], t["theorem"])

    def test_the_snapshot_reports_the_external_run_as_reported_and_never_as_verified(self):
        with open(os.path.join(CAMP, "snapshot", "SNAPSHOT.json"), encoding="utf-8") as fh:
            rows = json.load(fh)["rows"]
        pesados = [r for r in rows if r["lean_theorems_external_vm"]]
        self.assertGreaterEqual(len(pesados), 8)
        for r in pesados:
            self.assertIn("EXTERNAL_KERNEL_RUN", r["lean"])
            self.assertIn("nível EXTERNAL_RUN_REPORTED", r["lean"])
            self.assertIn("NÃO é reprodução independente", r["lean"])
            self.assertNotIn("KERNEL_VERIFIED", r["lean"])

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_the_infrastructure_computes_reported_for_the_run_and_for_every_covered_claim_and_the_snapshot_rule_agrees(self):
        c = Campanha(CAMP)
        self.assertEqual(KERNEL.avaliar(self.kr)["nivel"], "EXTERNAL_RUN_REPORTED")
        sys.path.insert(0, os.path.join(ROOT, "tools", "campaign"))
        try:
            import snapshot_covering as SNAP
        finally:
            sys.path.pop(0)
        self.assertEqual(SNAP.nivel_kernel_run(self.kr), "EXTERNAL_RUN_REPORTED")
        for cid in self.kr["claim_ids"]:
            n = KERNEL.nivel_do_claim(c, cid)
            self.assertEqual(n["nivel"], "EXTERNAL_RUN_REPORTED", (cid, n["execucoes"]))
            cam = KERNEL.camadas_do_claim(c, cid)
            self.assertFalse(cam["reproducao"]["kernel_em_segunda_execucao"])
            self.assertFalse(cam["enunciado"]["revisado"])
            self.assertFalse(cam["novidade"]["avaliada"])
        self.assertTrue(c.verificar_cadeia()["ok"])
        self.assertTrue(c.registro_confere_com_auditoria("kernel_runs", KR_ID)["ok"])

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_migration_is_idempotent_regenerating_twice_gives_the_same_kernel_run_and_claim_states(self):
        src = os.path.dirname(os.path.dirname(os.path.dirname(KERNEL.__file__)))
        tmp = tempfile.mkdtemp(prefix="mig-")
        self.addCleanup(shutil.rmtree, tmp, True)
        dst = os.path.join(tmp, "repo")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".lake", ".pytest_cache", "__pycache__"), symlinks=True)

        def roda():
            r = subprocess.run([sys.executable, "tools/campaign/migrate_covering.py", "--factory-src", src, "--sem-lean", "--sem-corridas"],
                               cwd=dst, capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 0, r.stderr[-800:])
            camp = os.path.join(dst, "campaigns", "covering-codes")
            kr = json.load(open(os.path.join(camp, "kernel_runs", KR_ID + ".json"), encoding="utf-8"))
            kr.pop("recorded_at")  # único campo que carrega a hora da migração
            estados = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8"))["status"] for p in sorted(glob.glob(os.path.join(camp, "claims", "*.json")))}
            return kr, estados

        a = roda()
        b = roda()
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[1], b[1])


if __name__ == "__main__":
    unittest.main()
