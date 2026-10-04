# Relatório de reprodução: covering-codes

- veredito: **NÃO REPRODUZIDO por completo** (PASS 11, FAIL 0, SKIPPED 3, dos quais 2 opcional(is))
- data: 2026-10-04T06:57:00Z   runtime total: 766.74 s
- modo: checkout atual
- commit: 893c5c7d354d8ad3945c2cd8abec6579b265cac2
- toolchain Lean: leanprover/lean4:v4.34.1; versão medida: Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release); Mathlib: d13f23b723b8a846827a245b89c10fc7d3f11612
- máquina: Linux-6.18.44-fc-v64-x86_64-with-glibc2.39; CPU: Intel(R) Xeon(R) Processor @ 2.10GHz (4 núcleos); RAM: 15.7 GiB

## Passos

### ambiente (ambiente): PASS
- versions: {'cc': 'cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0', 'python3': 'Python 3.11.15', 'go': 'flag provided but not defined: -version', 'rustc': 'rustc 1.97.0 (2d8144b78 2026-07-07)'}

### hashes-dos-witnesses (hashes): PASS
- witnesses: 13

### check-all-verify-c (dados): PASS
comando: `bash tools/verify/check_all.sh`
- runtime_s: 3.902
- last_line: check_all: 12 códigos, todos cobrem (0 pontos descobertos).

### estrutura-regenera (gerador): PASS
comando: `python3 scripts/codes/build_structured.py --check`
- runtime_s: 14.09
- last_line: q7_n9_R4_M1351.json: 3 cosets de [9,3]_7 + 46 cosets de [9,1]_7 + 0 palavras

### gerador-1285 (gerador): PASS
comando: `python3 -m unittest tests.test_code_format.GeneratorsRegenerateTheCodes -v`
- runtime_s: 12.359
- last_line: OK

### gerador-1137 (gerador): PASS
comando: `python3 scripts/search/gen.py data/search/p1137.json /tmp/covering_p1137_regen.txt`
- runtime_s: 0.024
- last_line: 1137 1137

### espelho-busca-k2-6-1 (gerador): PASS
comando: `python3 scripts/k261/sc_ref.py 6 10 2`
- runtime_s: 0.021
- last_line: {"ok": true, "nodes": 46, "frontier_len": 38, "frontier": [[8, 16753531392109382047, 9223372036854775817], [8, 16753531374929249631, 9223372036854775821], [8, 16753531366339183423, 9223372036854775823], [8, 16753531907513352703, 9223372036854775951], [8, 16753540153976393503, 9223372036854777999], [8, 16755783157706326303, 9223372036855302287], [8, 16755792563541180703, 9223372071215040655], [8, 16753531379224282735, 9223372036854775815], [8, 16753531396404415151, 9223372036854775823], [8, 16753531636926268159, 9223372036854775887], [8, 16753535760157789999, 9223372036854776911], [8, 16754657262023148079, 9223372036855039055], [8, 16754661990709985839, 9223372054034908239], [8, 16753531404994481359, 9223372036854775823], [8, 16753531508075275519, 9223372036854775855], [8, 16753533569691037519, 9223372036854776367], [8, 16754094320624010319, 9223372036854907439], [8, 16754096704294487119, 9223372045444842031], [8, 16753531456534878463, 9223372036854775839], [8, 16753531559615672563, 9223372036854775871], [8, 16753533621231434611, 9223372036854776383], [8, 16754094372164407411, 9223372036854907455], [8, 16754096755834884211, 9223372045444842047], [8, 16753532487342759823, 9223372036854776095], [8, 16753532590423553971, 9223372036854776127], [8, 16753534652039315203, 9223372036854776639], [8, 16754095402972288771, 9223372036854907711], [8, 16754097786642765571, 9223372045444842303], [8, 16753812862809344143, 9223372036854841631], [8, 16753812965890138291, 9223372036854841663], [8, 16753815027505900291, 9223372036854842175], [8, 16754375778438676483, 9223372036854973247], [8, 16754378162109349891, 9223372045444907839], [8, 16753814061086935183, 9223372041149808927], [8, 16753814164167729331, 9223372041149808959], [8, 16753816225783491331, 9223372041149809471], [8, 16754376976716464131, 9223372041149940543], [8, 16754379347502039043, 9223372049739875135]]}

### testes-pytest (teste): PASS
comando: `python3 -m pytest -q tests`
- runtime_s: 87.013
- last_line: 120 passed in 86.22s (0:01:26)

### verificadores-gerais-sobre-witnesses (verificadores): PASS
- runs: {'verify-c@w-q2-n6-r1-m12': 'PASS', 'verify-py-dilation@w-q2-n6-r1-m12': 'PASS', 'verify-rust@w-q2-n6-r1-m12': 'PASS', 'verify-cleanroom@w-q2-n6-r1-m12': 'PASS', 'verify-c@w-q4-n10-r4-m192': 'PASS', 'verify-py-dilation@w-q4-n10-r4-m192': 'PASS', 'verify-rust@w-q4-n10-r4-m192': 'PASS', 'verify-cleanroom@w-q4-n10-r4-m192': 'PASS', 'verify-c@w-q5-n10-r4-m625': 'PASS', 'verify-py-dilation@w-q5-n10-r4-m625': 'PASS', 'verify-rust@w-q5-n10-r4-m625': 'PASS', 'verify-cleanroom@w-q5-n10-r4-m625': 'PASS', 'verify-c@w-q5-n7-r2-m500': 'PASS', 'verify-py-dilation@w-q5-n7-r2-m500': 'PASS', 'verify-rust@w-q5-n7-r2-m500': 'PASS', 'verify-cleanroom@w-q5-n7-r2-m500': 'PASS', 'verify-c@w-q5-n9-r3-m1250': 'PASS', 'verify-py-dilation@w-q5-n9-r3-m1250': 'PASS', 'verify-rust@w-q5-n9-r3-m1250': 'PASS', 'verify-cleanroom@w-q5-n9-r3-m1250': 'PASS', 'verify-c@w-q5-n9-r4-m250': 'PASS', 'verify-py-dilation@w-q5-n9-r4-m250': 'PASS', 'verify-rust@w-q5-n9-r4-m250': 'PASS', 'verify-cleanroom@w-q5-n9-r4-m250': 'PASS', 'verify-c@w-q5-n9-r5-m50': 'PASS', 'verify-py-dilation@w-q5-n9-r5-m50': 'PASS', 'verify-rust@w-q5-n9-r5-m50': 'PASS', 'verify-cleanroom@w-q5-n9-r5-m50': 'PASS', 'verify-c@w-q7-n8-r3-m1887': 'PASS', 'verify-py-dilation@w-q7-n8-r3-m1887': 'PASS', 'verify-rust@w-q7-n8-r3-m1887': 'PASS', 'verify-cleanroom@w-q7-n8-r3-m1887': 'PASS', 'verify-c@w-q7-n8-r3-m1893': 'PASS', 'verify-py-dilation@w-q7-n8-r3-m1893': 'PASS', 'verify-rust@w-q7-n8-r3-m1893': 'PASS', 'verify-cleanroom@w-q7-n8-r3-m1893': 'PASS', 'verify-c@w-q7-n9-r4-m1137': 'PASS', 'verify-py-dilation@w-q7-n9-r4-m1137': 'PASS', 'verify-rust@w-q7-n9-r4-m1137': 'PASS', 'verify-cleanroom@w-q7-n9-r4-m1137': 'PASS', 'verify-c@w-q7-n9-r4-m1141': 'PASS', 'verify-py-dilation@w-q7-n9-r4-m1141': 'PASS', 'verify-rust@w-q7-n9-r4-m1141': 'PASS', 'verify-cleanroom@w-q7-n9-r4-m1141': 'PASS', 'verify-c@w-q7-n9-r4-m1285': 'PASS', 'verify-py-dilation@w-q7-n9-r4-m1285': 'PASS', 'verify-rust@w-q7-n9-r4-m1285': 'PASS', 'verify-cleanroom@w-q7-n9-r4-m1285': 'PASS', 'verify-c@w-q7-n9-r4-m1351': 'PASS', 'verify-py-dilation@w-q7-n9-r4-m1351': 'PASS', 'verify-rust@w-q7-n9-r4-m1351': 'PASS', 'verify-cleanroom@w-q7-n9-r4-m1351': 'PASS'}

### verificadores-k794-sobre-witnesses-k7-9-4 (verificadores): PASS
- runs: {'verify-val-bruteforce@w-q7-n9-r4-m1351': 'PASS', 'verify-val-balls@w-q7-n9-r4-m1351': 'PASS', 'verify-val-bfs@w-q7-n9-r4-m1351': 'PASS', 'verify-val-bruteforce@w-q7-n9-r4-m1285': 'PASS', 'verify-val-balls@w-q7-n9-r4-m1285': 'PASS', 'verify-val-bfs@w-q7-n9-r4-m1285': 'PASS', 'verify-val-bruteforce@w-q7-n9-r4-m1141': 'PASS', 'verify-val-balls@w-q7-n9-r4-m1141': 'PASS', 'verify-val-bfs@w-q7-n9-r4-m1141': 'PASS', 'verify-val-bruteforce@w-q7-n9-r4-m1137': 'PASS', 'verify-val-balls@w-q7-n9-r4-m1137': 'PASS', 'verify-val-bfs@w-q7-n9-r4-m1137': 'PASS'}

### lake-build-alvo-padrao (lean_build): SKIPPED
SKIPPED (opcional): não bloqueia o veredito. NÃO reproduzido neste ambiente: build Lean não solicitado (use lean=True / --lean)

### lake-build-coveringsyn (lean_build): SKIPPED
SKIPPED (opcional): não bloqueia o veredito. NÃO reproduzido neste ambiente: build Lean não solicitado (use lean=True / --lean)

### axiomas-dos-registros-formais (axiomas): SKIPPED
NÃO reproduzido neste ambiente: axiomas reais exigem Lean: rode com lean=True / --lean (sem isso nada foi medido)

### auditoria-da-cadeia (auditoria): PASS
- events: 570

## Hashes dos witnesses

- w-q2-n6-r1-m12: 3841679b4baf076b395d811e76cea94937e1c973a31564c7701cbdb5ff335cb5
- w-q4-n10-r4-m192: 83c0f109876b9773867e2e3680e2e04862c3ad641df47d8c56139445403d7410
- w-q5-n10-r4-m625: ba1ec554be784e105c9c729c0cb5ea08c5cf10d120ee617ede96d864a83e53b9
- w-q5-n7-r2-m500: 52a85f1b069e06df3c8503a3001e90d8d8170139e05b4ced05c5b8dabe5c27c3
- w-q5-n9-r3-m1250: 334d055a45bcc7fffd7cc7ed5cefd719e8787587ced1b66b44cc85785a6bdea6
- w-q5-n9-r4-m250: c605e57c41117da0141fdd88dc3972598fb4dd6e02bedc3edd477330f3bf5922
- w-q5-n9-r5-m50: 136e55ebc1151ce5b1eaac414f6735209e8d4f4136352018b516d65140b58499
- w-q7-n8-r3-m1887: 98531afbd8afbcec54ec01d441836ce706f8702ece4df594447789af6732643b
- w-q7-n8-r3-m1893: 07e2f3c1c65608b037fb13a2e85fd9ea25c2ace2bcc9e30a128e1833c2d06e28
- w-q7-n9-r4-m1137: df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102
- w-q7-n9-r4-m1141: 315692c9c722de4a9865727d8f02419c1e93701f0109683d0574af6b15685e67
- w-q7-n9-r4-m1285: 89cbd6b290a10d8d708e9783a405b8a12ce5efd6a8ea2ee17568b3ee25c50f31
- w-q7-n9-r4-m1351: 6d1b0e1abb8079df06a28d5301607d3d5247e0f2005d72e13f695ce26f6e6b52

## Teoremas e axiomas registrados

- CoveringKernel.cert_of_go: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- SC.chkN_sound: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.code12_card: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.code12_covers: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.even_inter: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.excess_bound: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.H1_counterexample: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.H2_counterexample_uncond: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.H3_counterexample: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.H5_counterexample: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringKernel.K4_10_4_le_192_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringKernel.K5_10_4_le_625_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringKernel.K5_7_2_le_500_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringKernel.K5_9_3_le_1250_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringKernel.K5_9_4_le_250_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringKernel.K5_9_5_le_50_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringKernel.K7_8_3_le_1893_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringKernel.K7_9_4_le_1351_kernel: axiomas None; sorry_free=True; clean_build=False
- SC.K_2_6_1_eq12: axiomas None; sorry_free=True; clean_build=False
- CoveringA6.K_2_6_1_ge_11: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K4_10_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_10_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_7_2_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_9_3_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_9_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_9_5_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K7_8_3_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K7_9_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA2.sphere_covering: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- Syn.K7_9_4_le_1137_syn: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- Syn.K7_9_4_le_1141_syn: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- Syn.K7_9_4_le_1285_syn: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- Syn.K7_9_4_le_1351_syn: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- Syn.K7_8_3_le_1887_syn: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- Syn.syn_cert: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True

## Falhas

nenhuma
