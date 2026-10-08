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

from campaign_derivation import estado_esperado_de_claim_de_cota, teoremas_kernel_dos_finais

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

    def test_the_heavy_formal_records_are_exactly_the_ones_pointing_to_the_historical_run(self):
        # hoje 9 = os 8 K*_le_*_kernel dos arquivos Final + SC.K_2_6_1_eq12; o número sai dos .lean (nada digitado)
        self.assertEqual(len(self.pesados), len(teoremas_kernel_dos_finais()) + 1)
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

    def test_the_historical_run_does_not_fabricate_host_or_toolchain_provenance(self):
        """O id numérico real da lean-build2 nunca foi capturado (IP/tipo de máquina de um inventário não são id de instância): fica captured_by_tool=false e nulo."""
        hp = self.kr["host"]["provenance"]
        self.assertIs(hp["captured_by_tool"], False)
        for k in ("provider", "project_id", "numeric_instance_id", "instance_name", "zone", "machine_type", "cpu_platform", "captured_at"):
            self.assertIsNone(hp[k], k)
        self.assertIsNone(hp["boot_image"]["source_image"])
        self.assertIs(hp["registrado_de_outro_host"], True)
        tp = self.kr["toolchain_provenance"]
        self.assertIs(tp["captured_by_tool"], False)
        for k in ("lean_version_literal", "lake_version_literal", "lean_toolchain_sha256", "lake_manifest_sha256", "commit_sha", "tree_clean"):
            self.assertIsNone(tp[k], k)
        # host.id continua sendo o texto declarado de sempre
        self.assertEqual(self.kr["host"]["id"], "lean-build2")

    def test_no_level_or_boolean_summary_is_stored_in_the_run(self):
        for k in ("level", "nivel", "status", "kernel_verified", "proved", "verified", "independently_reproduced"):
            self.assertNotIn(k, self.kr)

    def test_every_claim_using_a_heavy_record_is_covered_by_the_run_and_none_changed_state(self):
        usam = {cid for cid, cl in self.claims.items()
                if any(f in self.pesados for f in cl["evidence"]["formal"] + cl.get("complementary_formal", []))}
        self.assertEqual(usam, set(self.kr["claim_ids"]))
        self.assertEqual(len(usam), len(self.kr["claim_ids"]))
        # migração conservadora: o estado de cada claim que usa um registro pesado é o que as guardas dão sem o pesado: cota de código => PROVED se há Syn medido, senão IR;
        # K_2(6,1) (busca exaustiva em Python, Lean pesado só declarado) => EXHAUSTIVE_BOUNDED. Derivado do lakefile, não digitado.
        esperado = {c: ("EXHAUSTIVE_BOUNDED" if c.startswith("k2-6-1-") else estado_esperado_de_claim_de_cota(c)) for c in usam}
        self.assertEqual({c: self.claims[c]["status"] for c in usam}, esperado, "migração conservadora: nenhum estado de claim muda")
        resumo = {}
        for cl in self.claims.values():
            resumo[cl["status"]] = resumo.get(cl["status"], 0) + 1
        self.assertTrue(set(resumo) <= {"PROVED", "INDEPENDENTLY_REPRODUCED", "EXHAUSTIVE_BOUNDED", "REFUTED"}, resumo)
        self.assertEqual(resumo.get("REFUTED", 0), len([c for c in self.claims.values() if c["kind"] == "conjecture"]), "toda hipótese refutada pelo Lean está REFUTED")
        self.assertEqual(resumo.get("EXHAUSTIVE_BOUNDED", 0), len([c for c in self.claims if c.startswith("k2-6-1-") and self.claims[c]["status"] == "EXHAUSTIVE_BOUNDED"]))

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
            self.assertIn("Kernel evidence: EXTERNAL_RUN_REPORTED", r["lean"])  # rótulo do eixo: o nível do kernel nunca aparece como se fosse estado do claim
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
            self.assertEqual(KERNEL.camadas_do_claim(c, cid)["rotulo_dos_eixos"], f"Claim state: {self.claims[cid]['status']} / Kernel evidence: EXTERNAL_RUN_REPORTED")
            cam = KERNEL.camadas_do_claim(c, cid)
            self.assertFalse(cam["reproducao"]["kernel_em_segunda_execucao"])
            self.assertFalse(cam["enunciado"]["revisado"])
            self.assertFalse(cam["novidade"]["avaliada"])
        self.assertTrue(c.verificar_cadeia()["ok"])
        self.assertTrue(c.registro_confere_com_auditoria("kernel_runs", KR_ID)["ok"])
        # N:1 sem inventar: claims <- registros formais pesados <- teoremas da execução (SC.K_2_6_1_ge12 está na execução e nenhum registro o cita: +1)
        res = KERNEL.tabela_claim_formal_execucao(c)["resumo_por_execucao"]
        self.assertEqual([(x["claims"], x["registros_formais"], x["teoremas_verificados"]) for x in res if x["kernel_run"] == KR_ID],
                         [(len(self.kr["claim_ids"]), len(self.pesados), len(self.pesados) + 1)])
        self.assertEqual(KERNEL.problemas_de_cobertura(c, self.kr), [])
        linhas = KERNEL.tabela_claim_formal_execucao(c)["linhas"]
        # a única linha não verificada na execução é o f-syn-1351 (Syn.*, medido LOCALMENTE, fora desta execução): a tabela diz isso em vez de esconder
        self.assertEqual([x["formal_id"] for x in linhas if not x["verificado_na_execucao"]], ["f-syn-1351"])
        self.assertTrue(all(x["fonte_confere"] for x in linhas if x["verificado_na_execucao"]))
        # o claim não herda nada da proveniência: o par independente exige instância capturada (a histórica não tem)
        self.assertTrue(any("host só declarado" in f for f in KERNEL.avaliar(self.kr)["faltam_para_kernel_verified"]))

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
            tr = {}
            for rid in (TR_A, TR_B):
                x = json.load(open(os.path.join(camp, "kernel_runs", rid + ".json"), encoding="utf-8"))
                x.pop("recorded_at")
                tr[rid] = x
            nivel = KERNEL.nivel_do_claim(Campanha(camp), TR_CLAIM)
            return kr, estados, tr, (nivel["nivel"], sorted(nivel["par_independente"] or []))

        a = roda()
        b = roda()
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[1], b[1])
        self.assertEqual(a[2], b[2], "os runs do traçador são os mesmos nas duas migrações (a menos de recorded_at)")
        self.assertEqual(a[3], b[3])


TR = os.path.join(CAMP, "_fatos", "kernel_runs_tracer")
TR_A, TR_B = "kr-1887-syn-1a5fa26-kr-teste-a", "kr-1887-syn-1a5fa26-kr-teste-b"
TR_CLAIM = "k7-8-3-ub-1887"
TR_BUCKET = "gs://factory-cauteloso-telemetria/matematica/kernel-runs"


def _json(*partes):
    with open(os.path.join(*partes), encoding="utf-8") as fh:
        return json.load(fh)


class TracerRunsTest(unittest.TestCase):
    """As duas execuções reais do traçador (Syn_K1887, VMs kr-teste-a e kr-teste-b) e as tentativas de quebrá-las.

    Leem a campanha real. As tentativas que PRECISAM registrar algo usam uma cópia temporária DENTRO do repo (campaigns/_tmp-*), na mesma
    profundidade de campaigns/covering-codes: o `data_root` ("../..") e os caminhos relativos ao repo continuam valendo (fora do repo a
    auditoria dá `stale`). A campanha real nunca é escrita."""

    @classmethod
    def setUpClass(cls):
        cls.runs = carregar("kernel_runs")
        cls.claims = carregar("claims")

    def test_the_two_real_runs_are_registered_with_log_in_the_bucket_named_by_its_own_sha256(self):
        for rid, lado in ((TR_A, "a"), (TR_B, "b")):
            r = self.runs[rid]
            with open(os.path.join(TR, lado, "build.log"), "rb") as fh:
                dados = fh.read()
            sha = hashlib.sha256(dados).hexdigest()
            self.assertEqual(r["raw_log"]["sha256"], sha)
            self.assertEqual(r["raw_log"]["uri"], f"{TR_BUCKET}/{sha}.log")
            self.assertEqual(r["raw_log"]["size_bytes"], len(dados))
            self.assertEqual(r["raw_log"]["verification"]["modo"], "pre_enviado")
            self.assertIn("12622", r["raw_log"]["verification"]["conferido_por"])
        self.assertNotEqual(self.runs[TR_A]["raw_log"]["sha256"], self.runs[TR_B]["raw_log"]["sha256"])

    def test_the_two_runs_carry_tool_captured_provenance_of_distinct_instances_and_it_is_the_one_generated_on_the_vm(self):
        ids = set()
        for rid, lado in ((TR_A, "a"), (TR_B, "b")):
            r = self.runs[rid]
            hp = r["host"]["provenance"]
            self.assertIs(hp["captured_by_tool"], True)
            self.assertIs(r["toolchain_provenance"]["captured_by_tool"], True)
            self.assertIs(r["toolchain_provenance"]["tree_clean"], True)
            self.assertEqual(r["toolchain_provenance"]["commit_sha"], r["commit_sha"])
            ids.add(hp["numeric_instance_id"])
            pac = _json(TR, lado, "prov.json")
            self.assertEqual(hp["numeric_instance_id"], pac["host_provenance"]["numeric_instance_id"], "o id vem do pacote gerado na VM, não de texto digitado")
        self.assertEqual(ids, {"5198467000349702121", "1876810319497476070"})

    def test_the_run_a_copy_attempt_spec_is_not_registered_as_a_second_run(self):
        self.assertNotIn("kr-1887-syn-1a5fa26-copia-de-a", self.runs)
        self.assertEqual(len([k for k in self.runs if k.startswith("kr-1887-syn-")]), 2)

    def test_registering_the_tracer_runs_changes_no_claim_state(self):
        # as guardas dão o estado; registrar um kernel_run não o muda: cada claim de cota está no estado que o lakefile/.lean implicam (sem contagem digitada)
        for cid, cl in self.claims.items():
            if "-ub-" in cid and not cid.startswith("k2-6-1-"):
                self.assertEqual(cl["status"], estado_esperado_de_claim_de_cota(cid), cid)
        self.assertEqual(self.claims[TR_CLAIM]["status"], "PROVED")
        self.assertNotIn(TR_CLAIM, set(self.runs[KR_ID]["claim_ids"]))

    def test_each_tracer_run_covers_only_the_syn_1887_claim_and_no_heavy_claim(self):
        for rid in (TR_A, TR_B):
            self.assertEqual(self.runs[rid]["claim_ids"], [TR_CLAIM])
            self.assertEqual([t["theorem"] for t in self.runs[rid]["theorems"]], ["Syn.K7_8_3_le_1887_syn"])
        self.assertTrue(set(self.runs[KR_ID]["claim_ids"]).isdisjoint({TR_CLAIM}))

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_the_tracer_claim_reaches_independently_reproduced_with_the_pair_a_b_and_the_heavy_ones_do_not(self):
        c = Campanha(CAMP)
        for rid in (TR_A, TR_B):
            self.assertEqual(KERNEL.avaliar(self.runs[rid])["nivel"], "KERNEL_VERIFIED", rid)
        self.assertEqual(KERNEL.par_independente(self.runs[TR_A], self.runs[TR_B]), [])
        n = KERNEL.nivel_do_claim(c, TR_CLAIM)
        self.assertEqual(n["nivel"], "KERNEL_INDEPENDENTLY_REPRODUCED")
        self.assertEqual(sorted(n["par_independente"]), sorted([TR_A, TR_B]))
        self.assertEqual(KERNEL.camadas_do_claim(c, TR_CLAIM)["rotulo_dos_eixos"], "Claim state: PROVED / Kernel evidence: KERNEL_INDEPENDENTLY_REPRODUCED")
        for cid in self.runs[KR_ID]["claim_ids"]:
            self.assertEqual(KERNEL.nivel_do_claim(c, cid)["nivel"], "EXTERNAL_RUN_REPORTED", cid)
        self.assertTrue(c.verificar_cadeia()["ok"])
        for rid in (TR_A, TR_B):
            self.assertTrue(c.registro_confere_com_auditoria("kernel_runs", rid)["ok"], rid)

    # ------------------------------------------------------------ tentativas de quebrar (cópia temporária DENTRO do repo)
    def _copia(self):
        tmp = tempfile.mkdtemp(prefix="_tmp-tr-", dir=os.path.dirname(CAMP))
        self.addCleanup(shutil.rmtree, tmp, True)
        shutil.rmtree(tmp)
        shutil.copytree(CAMP, tmp, symlinks=True)
        return tmp

    def _registra(self, c, lado, run_id=None, prov=None, log=None, spec_extra=None, uri=None, tamanho=None):
        spec = _json(TR, lado, "spec.json")
        if run_id:
            spec["run_id"] = run_id
        spec.update(spec_extra or {})
        log = log or os.path.join(TR, lado, "build.log")
        with open(log, "rb") as fh:
            dados = fh.read()
        sha = hashlib.sha256(dados).hexdigest()
        arm = KERNEL.ArmazenadorPreEnviado(uri or f"{TR_BUCKET}/{sha}.log", len(dados) if tamanho is None else tamanho, "teste: declaração", "2026-10-04")
        kw = {k: spec[k] for k in ("commit_sha", "lean_version", "lean_toolchain", "mathlib_commit", "command", "target", "host", "started_at", "finished_at", "leaves", "measured_by")}
        return KERNEL.registrar_execucao(c, spec["run_id"], log=log, claim_ids=spec["claim_ids"], teoremas=spec["teoremas"], armazenador=arm, ator="agente-kr",
                                         papel="FORMALIZER", raiz_fontes=ROOT, proveniencia_json=prov or os.path.join(TR, lado, "prov.json"), **kw)

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_repeating_a_run_id_is_refused_and_the_registered_run_is_untouched(self):
        c = Campanha(self._copia())
        antes = open(os.path.join(c.raiz, "kernel_runs", TR_A + ".json"), "rb").read()
        with self.assertRaises(Exception) as cm:
            self._registra(c, "a")
        self.assertIn("exist", str(cm.exception).lower())
        self.assertEqual(antes, open(os.path.join(c.raiz, "kernel_runs", TR_A + ".json"), "rb").read())

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_a_tampered_provenance_bundle_is_refused_because_its_bundle_sha256_does_not_match(self):
        c = Campanha(self._copia())
        pac = _json(TR, "b", "prov.json")
        pac["host_provenance"]["numeric_instance_id"] = "1111111111111111111"
        arq = os.path.join(tempfile.mkdtemp(prefix="_tmp-prov-", dir=os.path.dirname(CAMP)), "prov.json")
        self.addCleanup(shutil.rmtree, os.path.dirname(arq), True)
        with open(arq, "w", encoding="utf-8") as fh:
            json.dump(pac, fh)
        with self.assertRaises(Exception) as cm:
            self._registra(c, "b", run_id="kr-teste-adulterada", prov=arq)
        self.assertIn("bundle_sha256", str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(c.raiz, "kernel_runs", "kr-teste-adulterada.json")))

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_a_run_without_provenance_is_only_reported_and_does_not_pair_with_a(self):
        c = Campanha(self._copia())
        # `coletar_proveniencia=False`: host/toolchain só declarados; usa o log de B (outro log, outra janela)
        spec = _json(TR, "b", "spec.json")
        log = os.path.join(TR, "b", "build.log")
        sha = hashlib.sha256(open(log, "rb").read()).hexdigest()
        kw = {k: spec[k] for k in ("commit_sha", "lean_version", "lean_toolchain", "mathlib_commit", "command", "target", "host", "started_at", "finished_at", "leaves", "measured_by")}
        KERNEL.registrar_execucao(c, "kr-teste-b-sem-prov", log=log, claim_ids=spec["claim_ids"], teoremas=spec["teoremas"], armazenador=KERNEL.ArmazenadorPreEnviado(
            f"{TR_BUCKET}/{sha}.log", os.path.getsize(log), "teste: declaração", "2026-10-04"), ator="agente-kr", papel="FORMALIZER", raiz_fontes=ROOT,
            coletar_proveniencia=False, **kw)
        r = c.ler("kernel_runs", "kr-teste-b-sem-prov")
        self.assertEqual(KERNEL.avaliar(r)["nivel"], "EXTERNAL_RUN_REPORTED")
        self.assertTrue(any("host" in f for f in KERNEL.avaliar(r)["faltam_para_kernel_verified"]))
        self.assertTrue(KERNEL.par_independente(c.ler("kernel_runs", TR_A), r))

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_a_wrong_log_size_or_an_object_name_without_the_sha_is_refused_before_anything_is_written(self):
        c = Campanha(self._copia())
        n0 = len(os.listdir(os.path.join(c.raiz, "kernel_runs")))
        with self.assertRaises(Exception) as cm:
            self._registra(c, "b", run_id="kr-teste-tamanho", tamanho=12621)
        self.assertIn("tamanho", str(cm.exception))
        with self.assertRaises(Exception) as cm:
            self._registra(c, "b", run_id="kr-teste-nome", uri=f"{TR_BUCKET}/build.log")
        self.assertIn("sha256", str(cm.exception))
        self.assertEqual(len(os.listdir(os.path.join(c.raiz, "kernel_runs"))), n0)

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_registering_run_a_again_under_another_run_id_does_not_form_an_independent_pair(self):
        c = Campanha(self._copia())
        self._registra(c, "a", run_id="kr-teste-copia-de-a")
        copia = c.ler("kernel_runs", "kr-teste-copia-de-a")
        self.assertEqual(KERNEL.avaliar(copia)["nivel"], "KERNEL_VERIFIED")
        motivos = KERNEL.par_independente(c.ler("kernel_runs", TR_A), copia)
        self.assertTrue(motivos)
        self.assertTrue(any("host.id igual" in m or "log bruto é o mesmo" in m for m in motivos), motivos)
        # sem B (removido só da cópia temporária), A + cópia-de-A fica em KERNEL_VERIFIED: a mesma execução contada duas vezes não é reprodução
        os.remove(os.path.join(c.raiz, "kernel_runs", TR_B + ".json"))
        n = KERNEL.nivel_do_claim(c, TR_CLAIM)
        self.assertEqual(n["nivel"], "KERNEL_VERIFIED")
        self.assertIsNone(n["par_independente"])

    @unittest.skipIf(KERNEL is None, "infraestrutura factory_cauteloso fora do PYTHONPATH")
    def test_the_log_of_b_with_the_provenance_of_a_is_a_mixture_that_does_not_pair(self):
        c = Campanha(self._copia())
        self._registra(c, "b", run_id="kr-teste-mistura", prov=os.path.join(TR, "a", "prov.json"))
        mix = c.ler("kernel_runs", "kr-teste-mistura")
        self.assertEqual(mix["host"]["provenance"]["numeric_instance_id"], "5198467000349702121")
        self.assertTrue(KERNEL.par_independente(c.ler("kernel_runs", TR_A), mix), "a mistura usa a instância de A: não é uma 2ª instância")

    def test_the_migration_script_that_registers_the_tracer_is_deterministic_in_what_it_reads(self):
        """A migração só lê arquivos versionados de _fatos/kernel_runs_tracer: sem hora do relógio nem rede nos campos que comparamos."""
        src = open(os.path.join(ROOT, "tools", "campaign", "migrate_covering.py"), encoding="utf-8").read()
        trecho = src[src.index("o traçador: DUAS execuções reais"):src.index("# ------------------------------------------------------------------ resíduos")]
        self.assertIn("ArmazenadorPreEnviado", trecho)
        self.assertNotIn("datetime.now", trecho)
        self.assertNotIn("urlopen", trecho)

    def test_the_vm_script_parses_with_bash_and_has_no_machine_paths(self):
        p = os.path.join(ROOT, "tools", "kernel_run_na_vm.sh")
        r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        txt = open(p, encoding="utf-8").read()
        self.assertNotRegex(txt, r"/home/[a-z]|/Users/|10\.158\.|ssh factory01")
        self.assertIn("lake build", txt)
        self.assertIn("provenance", txt)
        self.assertIn('COMMIT="${1:', txt)
        self.assertIn('ALVO="${2:', txt)



if __name__ == "__main__":
    unittest.main()
