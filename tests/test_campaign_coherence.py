"""Coerência dos registros da campanha `covering-codes` (campaigns/covering-codes/) com o contrato de verificação do red team.

Só lê JSON (sem a infraestrutura da Fábrica): cada teste descreve a falha que impede, não a função.
"""
import glob
import json
import os
import re
import unittest

from campaign_derivation import codigos_de_data_codes, estado_esperado_de_claim_de_cota, teoremas_declarados_no_main, teoremas_kernel_dos_finais

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
        cls.formal = carregar("formal")
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

    def test_verifiers_have_a_real_author_distinct_groups_and_receive_the_parameters_they_can_take(self):
        self.assertGreaterEqual(len(self.verifiers), 2)
        for vid, v in self.verifiers.items():
            with self.subTest(verifier=vid):
                self.assertTrue((v.get("implemented_by") or "").strip(), "sem implemented_by: independência seria só rótulo")
                cmd = " ".join(v["command"])
                # os verificadores de verification/ têm q, n (e R) cravados no código: só recebem o que podem receber, e declaram `applies_to`
                if v.get("applies_to") is None:
                    for k in "qnRM":
                        self.assertIn("{param:%s}" % k, cmd, "o verificador precisaria ler o parâmetro do nome do arquivo")
                else:
                    self.assertIn("{param:M}", cmd)
                    self.assertEqual(set(v["applies_to"]), {"q", "n", "R"})
                self.assertEqual(v["fail_exit_codes"][0], 1, "FAIL = 1 (descoberto); 3 é ERRO e nunca entra em fail_exit_codes")
                self.assertNotIn(3, v["fail_exit_codes"])
        self.assertEqual(len({v["independence_group"] for v in self.verifiers.values()}), len(self.verifiers))

    def test_verifiers_of_the_same_author_declare_that_they_share_logic_so_they_never_add_independence(self):
        # os 3 de verification/ vieram do mesmo autor de verify.c (git log): têm de aparecer ligados a ele, senão a contagem de independência inflaria
        por_autor = {}
        for vid, v in self.verifiers.items():
            por_autor.setdefault(v["implemented_by"].strip().lower(), []).append(vid)
        for autor, vids in por_autor.items():
            for vid in vids:
                outros = set(vids) - {vid}
                self.assertTrue(outros <= set(self.verifiers[vid]["compartilha_logica_com"]), f"{vid} (autor {autor}) não declara compartilhar lógica com {sorted(outros)}")
        self.assertGreaterEqual(len(por_autor), 4, "esperava ≥4 autores: verify.c, dilatação (autor dos claims), rust, clean-room")

    def test_the_cleanroom_verifier_is_registered_with_its_own_author_group_and_go_build(self):
        v = self.verifiers["verify-cleanroom"]
        self.assertEqual(v["language"], "go")
        self.assertTrue(any(step[:2] == ["go", "build"] for step in v["build"]), "o pipeline de build tem de ser `go build`")
        for outro in self.verifiers:
            if outro != "verify-cleanroom":
                self.assertNotEqual(v["implemented_by"], self.verifiers[outro]["implemented_by"])
                self.assertNotEqual(v["independence_group"], self.verifiers[outro]["independence_group"])
        self.assertEqual(v["compartilha_logica_com"], [])

    def test_latest_run_of_every_verifier_on_every_witness_it_applies_to_passed_the_claim_parameters_and_records_the_verifier_hash(self):
        ultimas = {}
        for r in sorted(self.runs.values(), key=lambda r: (r["ts"], r["run_id"])):
            ultimas[(r["verifier_id"], r["subject_id"])] = r
        aplicaveis = sorted((vid, wid) for vid, v in self.verifiers.items() for wid, w in self.witnesses.items()
                            if v.get("applies_to") is None or v["applies_to"] == {k: w["parameters"][k] for k in "qnR"})
        self.assertEqual(sorted(ultimas), aplicaveis, "toda corrida aplicável existe e nenhuma corrida foi feita fora do que o verificador declara aplicar")
        for (vid, wid), r in ultimas.items():
            with self.subTest(verifier=vid, witness=wid):
                self.assertEqual(r["result"], "PASS")
                self.assertTrue(r.get("verifier_sha256"))
                self.assertEqual(r["params_passed"], self.witnesses[wid]["parameters"])
                self.assertEqual(r["subject_sha256"], self.witnesses[wid]["sha256"])

    def test_literature_records_have_a_real_version_and_the_unsourced_numbers_are_declared_residuals(self):
        for lid, lit in self.literature.items():
            self.assertFalse(re.search(r"n[aã]o identificad|sem vers|n/a", lit["version"], re.I), f"{lid}: versão que diz que não há versão")
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
                # a classe sai da comparação numérica dos registros, não de texto
                self.assertEqual(cmp_["classificacao"] == "MELHORA_APARENTE_A_CONFIRMAR", cmp_["nosso"] < cmp_["melhor_registrada"], cid)
                if cmp_["classificacao"] == "MELHORA_APARENTE_A_CONFIRMAR":
                    melhoras += 1
                    self.assertIn("a confirmar por revisão externa", cmp_["nota"], cid)
        codigos = [f for f in os.listdir(os.path.join(ROOT, "data", "codes")) if re.search(r"q\d+_n\d+_R\d+_M\d+\.txt$", f)]
        self.assertEqual(melhoras, len(codigos), "um claim de cota superior com comparação por código de data/codes (nenhum fixado à mão)")

    def test_no_campaign_record_attributes_external_novelty_confirmation(self):
        # NOVELTY_EXTERNALLY_CONFIRMED não se autoatribui
        for pasta in ("claims", "literature", "residuals", "experiments"):
            for p in glob.glob(os.path.join(CAMP, pasta, "*.json")):
                with open(p, encoding="utf-8") as fh:
                    txt = fh.read()
                self.assertNotIn("NOVELTY_EXTERNALLY_CONFIRMED", txt, os.path.basename(p))
        with open(os.path.join(CAMP, "snapshot", "SNAPSHOT.json"), encoding="utf-8") as fh:
            for row in json.load(fh)["rows"]:
                self.assertNotEqual(row["literature_state"], "NOVELTY_EXTERNALLY_CONFIRMED", row["witness_id"])

    def test_each_apparent_improvement_cell_has_an_open_residual_naming_what_was_not_read(self):
        celulas = {cid.rsplit("-ub-", 1)[0] for cid in self.claims if "-ub-" in cid and cid.split("-ub-")[0] != "k2-6-1"}
        self.assertTrue(celulas)
        for cel in sorted(celulas):
            r = self.residuals[f"res-confirmar-{cel}"]
            self.assertEqual(r["instances"], [cel])
            self.assertIn("MELHORA_APARENTE_A_CONFIRMAR", r["reason"])
            self.assertRegex(r["reason"], r"(?i)n[ãa]o (foram |foi )?lid")
        self.assertIn("verify_cov.py", self.residuals["res-confirmar-k7-9-4"]["reason"])
        self.assertIn("931", self.residuals["res-confirmar-k7-9-4"]["reason"], "o risco ADS 931 (< 1137) é o que mais pode tirar a melhora aparente")
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

    def test_a_claim_is_proved_only_when_every_formal_record_in_its_evidence_is_measured_and_clean(self):
        # PROVED sem Lean medido seria o erro grave: o teorema pesado (CoveringHeavy) é só declarado e nunca fica em evidence.formal de claim PROVED
        esperados = {"propext", "Classical.choice", "Quot.sound"}
        fortes = ("PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED")
        for cid, cl in self.claims.items():
            if cl["status"] in fortes and cl["evidence"]["formal"]:
                for fid in cl["evidence"]["formal"]:
                    with self.subTest(claim=cid, formal=fid):
                        f = self.formal[fid]
                        self.assertIsNotNone(f["axioms"], "axiomas não medidos num claim promovido")
                        self.assertTrue(set(f["axioms"]) <= esperados)
                        self.assertIs(f["sorry_free"], True)
                        self.assertIs(f["clean_build"], True)
                        self.assertEqual(f["axioms_status"], "OK")
                        self.assertFalse(f["validation_problems"])
        for fid, f in self.formal.items():
            if fid.startswith("f-heavy-") or fid == "f-k2-6-1-eq12":
                with self.subTest(heavy=fid):
                    # a guarda só vê o que a campanha mediu: medição externa (VM do autor) vive em measured_external e NUNCA preenche axioms/clean_build
                    self.assertIsNone(f["axioms"])
                    self.assertTrue(f["axioms_status"].startswith(("DECLARED_NOT_REPRODUCED", "MEASURED_ON_EXTERNAL_VM")))
                    self.assertIs(f["clean_build"], False)
                    self.assertTrue(f["validation_problems"])
                    if f["axioms_status"].startswith("MEASURED_ON_EXTERNAL_VM"):
                        me = f["measured_external"]
                        self.assertTrue(set(me["axioms"]) <= esperados)
                        self.assertEqual(me["folhas_falhou"], 0)
                        self.assertIn("não refeita em segundo ambiente", me["ressalva"])
                        self.assertFalse(me["log_versionado"])

    def test_the_external_vm_measurement_of_coveringheavy_is_recorded_on_every_heavy_record_and_matches_the_facts_file(self):
        with open(os.path.join(CAMP, "_fatos", "medicao_heavy_vm.json"), encoding="utf-8") as fh:
            vm = json.load(fh)
        por_teorema = {t["teorema"]: t for t in vm["teoremas"]}
        pesados = {fid: f for fid, f in self.formal.items() if fid.startswith("f-heavy-") or fid == "f-k2-6-1-eq12"}
        # 9 hoje = os 8 K*_le_*_kernel dos arquivos Final + SC.K_2_6_1_eq12; o número sai dos .lean, não é digitado
        self.assertEqual(len(pesados), len(teoremas_kernel_dos_finais()) + 1)
        for fid, f in pesados.items():
            with self.subTest(formal=fid):
                me = f["measured_external"]
                self.assertEqual(me["axioms"], por_teorema[f["theorem"]]["axiomas"])
                self.assertEqual(me["repo_commit"], vm["repo_commit"])
                self.assertEqual((me["jobs"], me["folhas_ok"]), (vm["jobs_final"], vm["folhas_ok"]))
                self.assertEqual(me["log_sha256_prefixo"], vm["sha256_prefixo_log_completo"])

    def test_external_vm_measurement_never_promotes_a_claim_to_proved_through_the_heavy_record_alone(self):
        for cid, cl in self.claims.items():
            if any(fid.startswith("f-heavy-") or fid == "f-k2-6-1-eq12" for fid in cl["evidence"]["formal"]):
                with self.subTest(claim=cid):
                    self.assertNotIn(cl["status"], ("PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED"))

    def test_the_syn_theorems_that_exist_in_the_lean_library_are_measured_formal_records_of_their_code_claims(self):
        with open(os.path.join(ROOT, "lakefile.toml"), encoding="utf-8") as fh:
            tags = re.findall(r"CoveringLean\.Syn_K(\d+)", fh.read())
        self.assertTrue(tags, "o lakefile não declara mais a lib CoveringSyn: o teste envelheceu")
        for m in tags:
            with self.subTest(M=m):
                f = self.formal[f"f-syn-{m}"]
                self.assertEqual(f["module"], f"CoveringLean.Syn_K{m}")
                self.assertEqual(f["axioms_status"], "OK")
                cl = [c for c in self.claims.values() if f"f-syn-{m}" in c["evidence"]["formal"]]
                self.assertEqual(len(cl), 1)
                self.assertIn(f"-ub-{m}", cl[0]["claim_id"])
                self.assertIn(cl[0]["status"], ("PROVED", "FORMALLY_VERIFIED", "EXTERNALLY_REPRODUCED"), "teorema medido + 2 componentes independentes: a guarda de PROVED deveria passar")

    def test_every_kernel_theorem_in_the_lean_final_files_has_a_declared_heavy_record_on_a_claim(self):
        finais = glob.glob(os.path.join(ROOT, "CoveringLean", "K3_K*_Final.lean"))
        self.assertTrue(finais)
        teoremas = set()
        for p in finais:
            with open(p, encoding="utf-8") as fh:
                teoremas |= set(re.findall(r"^theorem (K\d+_\d+_\d+_le_\d+_kernel)", fh.read(), re.M))
        registrados = {f["theorem"].split(".")[-1] for fid, f in self.formal.items() if fid.startswith("f-heavy-")}
        self.assertEqual(teoremas, registrados)

    def test_state_of_art_md_is_cross_checked_against_the_registered_sources_and_never_diverges(self):
        with open(os.path.join(CAMP, "experiments", "exp-state-of-art-crosscheck.json"), encoding="utf-8") as fh:
            ex = json.load(fh)["result"]
        self.assertEqual(ex["resumo"]["diverge"], 0, [i for i in ex["itens"] if i["veredito"] == "DIVERGE"])
        self.assertEqual(ex["resumo"]["nao_encontrada"], 0)
        self.assertGreater(ex["resumo"]["sem_registro"], 0, "o que a campanha não tem como confirmar (Florath 2401, coldcase) tem de aparecer como SEM_REGISTRO")

    def test_the_previous_audit_chain_is_preserved_with_a_checksum_before_each_regeneration(self):
        import hashlib
        pastas = sorted(p for p in glob.glob(os.path.join(CAMP, "_autopsia", "audit-pre-regeneracao-*")) if os.path.isdir(p))
        self.assertTrue(pastas)
        for base in pastas:
            pasta = os.path.basename(base)
            with open(os.path.join(base, "SHA256SUMS"), encoding="utf-8") as fh:
                linhas = [l.split() for l in fh if l.strip()]
            self.assertEqual(sorted(l[1] for l in linhas), ["audit/anchors.jsonl", "audit/log.jsonl"], pasta)
            for soma, rel in linhas:
                with open(os.path.join(base, rel), "rb") as fh:
                    self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), soma, f"{pasta}/{rel}")

    def test_every_code_in_data_codes_has_a_witness_a_claim_and_a_lean_theorem_record(self):
        codigos = codigos_de_data_codes()
        self.assertTrue(codigos)
        paths = {os.path.basename(w["path"])[:-4] for w in self.witnesses.values()}
        for q, n, r, M in codigos:
            nome = f"q{q}_n{n}_R{r}_M{M}"
            self.assertIn(nome, paths, "código de data/codes sem witness: rode tools/campaign/migrate_covering.py")
            cl = [c for c in self.claims.values() if c.get("bound") and c["bound"]["direction"] == "upper" and c["bound"]["value"] == M
                  and c["bound"]["parameters"] == {"q": q, "n": n, "R": r} and c["evidence"]["witnesses"]]
            with self.subTest(code=nome):
                self.assertEqual(len(cl), 1, "um claim de cota superior com o witness em evidence.witnesses")
                formais = cl[0]["evidence"]["formal"] + cl[0].get("complementary_formal", [])
                self.assertTrue(formais, "todo código do main tem um teorema Lean (medido ou declarado)")
                # o estado sai das guardas, não de texto: Lean por síndromes medido + 2 componentes independentes => PROVED; só prefixos (declarado/relatado) => IR
                self.assertEqual(cl[0]["status"], estado_esperado_de_claim_de_cota(cl[0]["claim_id"]))

    def test_every_lean_theorem_declared_in_the_main_has_a_formal_record_measured_or_declared_not_reproduced_with_a_reason(self):
        # o main declara os teoremas em lakefile.toml (CoveringSyn, CoveringHeavy, ...) e nos .lean; teorema sem registro formal na campanha é buraco silencioso
        esperados = {"propext", "Classical.choice", "Quot.sound"}
        por_nome = {}
        for fid, f in self.formal.items():
            por_nome.setdefault(f["theorem"].split(".")[-1], []).append(f)
        faltam = sorted(teoremas_declarados_no_main() - set(por_nome))
        self.assertEqual(faltam, [], "teorema Lean declarado no main sem registro formal")
        for nome in sorted(teoremas_declarados_no_main()):
            f = por_nome[nome][0]
            with self.subTest(theorem=nome):
                if f["axioms"] is not None:  # MEDIDO: axiomas só os esperados, sem sorry, build limpo
                    self.assertTrue(set(f["axioms"]) <= esperados)
                    self.assertIs(f["sorry_free"], True)
                    self.assertIs(f["clean_build"], True)
                    self.assertEqual(f["axioms_status"], "OK")
                else:  # NÃO medido pela campanha: o registro diz por quê e a guarda continua negando
                    self.assertTrue(f["axioms_status"].startswith(("DECLARED_NOT_REPRODUCED", "MEASURED_ON_EXTERNAL_VM")), f["axioms_status"])
                    self.assertTrue(f["validation_problems"])
                    self.assertIs(f["clean_build"], False)
                    self.assertGreater(len(f["axioms_status"]), 60, "declarado sem motivo")


if __name__ == "__main__":
    unittest.main()
