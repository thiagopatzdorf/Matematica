# Relatório de reprodução: covering-codes

- veredito: **NÃO REPRODUZIDO por completo** (PASS 10, FAIL 1, SKIPPED 0)
- data: 2026-10-03T15:48:46Z   runtime total: 204.18 s
- modo: checkout atual
- commit: 2373b67c4ba9cb0e16ae707b128327de3dfcbd94
- toolchain Lean: leanprover/lean4:v4.34.1; versão medida: Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release); Mathlib: d13f23b723b8a846827a245b89c10fc7d3f11612
- máquina: Linux-6.18.44-fc-v64-x86_64-with-glibc2.39; CPU: Intel(R) Xeon(R) Processor @ 2.10GHz (4 núcleos); RAM: 15.7 GiB

## Passos

### ambiente (ambiente): PASS
- versions: {'cc': 'cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0', 'python3': 'Python 3.11.15'}

### hashes-dos-witnesses (hashes): PASS
- witnesses: 11

### check-all-verify-c (dados): PASS
comando: `bash tools/verify/check_all.sh`
- runtime_s: 2.388
- last_line: check_all: 10 códigos, todos cobrem (0 pontos descobertos).

### estrutura-regenera (gerador): PASS
comando: `python3 scripts/codes/build_structured.py --check`
- runtime_s: 14.395
- last_line: q7_n9_R4_M1351.json: 3 cosets de [9,3]_7 + 46 cosets de [9,1]_7 + 0 palavras

### gerador-1285 (gerador): PASS
comando: `python3 -m unittest tests.test_code_format.GeneratorsRegenerateTheCodes -v`
- runtime_s: 14.03
- last_line: OK

### espelho-busca-k2-6-1 (gerador): PASS
comando: `python3 scripts/k261/sc_ref.py 6 10 2`
- runtime_s: 0.022
- last_line: {"ok": true, "nodes": 46, "frontier_len": 38, "frontier": [[8, 16753531392109382047, 9223372036854775817], [8, 16753531374929249631, 9223372036854775821], [8, 16753531366339183423, 9223372036854775823], [8, 16753531907513352703, 9223372036854775951], [8, 16753540153976393503, 9223372036854777999], [8, 16755783157706326303, 9223372036855302287], [8, 16755792563541180703, 9223372071215040655], [8, 16753531379224282735, 9223372036854775815], [8, 16753531396404415151, 9223372036854775823], [8, 16753531636926268159, 9223372036854775887], [8, 16753535760157789999, 9223372036854776911], [8, 16754657262023148079, 9223372036855039055], [8, 16754661990709985839, 9223372054034908239], [8, 16753531404994481359, 9223372036854775823], [8, 16753531508075275519, 9223372036854775855], [8, 16753533569691037519, 9223372036854776367], [8, 16754094320624010319, 9223372036854907439], [8, 16754096704294487119, 9223372045444842031], [8, 16753531456534878463, 9223372036854775839], [8, 16753531559615672563, 9223372036854775871], [8, 16753533621231434611, 9223372036854776383], [8, 16754094372164407411, 9223372036854907455], [8, 16754096755834884211, 9223372045444842047], [8, 16753532487342759823, 9223372036854776095], [8, 16753532590423553971, 9223372036854776127], [8, 16753534652039315203, 9223372036854776639], [8, 16754095402972288771, 9223372036854907711], [8, 16754097786642765571, 9223372045444842303], [8, 16753812862809344143, 9223372036854841631], [8, 16753812965890138291, 9223372036854841663], [8, 16753815027505900291, 9223372036854842175], [8, 16754375778438676483, 9223372036854973247], [8, 16754378162109349891, 9223372045444907839], [8, 16753814061086935183, 9223372041149808927], [8, 16753814164167729331, 9223372041149808959], [8, 16753816225783491331, 9223372041149809471], [8, 16754376976716464131, 9223372041149940543], [8, 16754379347502039043, 9223372049739875135]]}

### testes-unittest (teste): PASS
comando: `python3 -m unittest discover -s tests -v`
- runtime_s: 35.827
- last_line: OK

### verificadores-sobre-witnesses (verificadores): PASS
- runs: {'verify-c@w-q2-n6-r1-m12': 'PASS', 'verify-py-dilation@w-q2-n6-r1-m12': 'PASS', 'verify-rust@w-q2-n6-r1-m12': 'PASS', 'verify-c@w-q4-n10-r4-m192': 'PASS', 'verify-py-dilation@w-q4-n10-r4-m192': 'PASS', 'verify-rust@w-q4-n10-r4-m192': 'PASS', 'verify-c@w-q5-n10-r4-m625': 'PASS', 'verify-py-dilation@w-q5-n10-r4-m625': 'PASS', 'verify-rust@w-q5-n10-r4-m625': 'PASS', 'verify-c@w-q5-n7-r2-m500': 'PASS', 'verify-py-dilation@w-q5-n7-r2-m500': 'PASS', 'verify-rust@w-q5-n7-r2-m500': 'PASS', 'verify-c@w-q5-n9-r3-m1250': 'PASS', 'verify-py-dilation@w-q5-n9-r3-m1250': 'PASS', 'verify-rust@w-q5-n9-r3-m1250': 'PASS', 'verify-c@w-q5-n9-r4-m250': 'PASS', 'verify-py-dilation@w-q5-n9-r4-m250': 'PASS', 'verify-rust@w-q5-n9-r4-m250': 'PASS', 'verify-c@w-q5-n9-r5-m50': 'PASS', 'verify-py-dilation@w-q5-n9-r5-m50': 'PASS', 'verify-rust@w-q5-n9-r5-m50': 'PASS', 'verify-c@w-q7-n8-r3-m1887': 'PASS', 'verify-py-dilation@w-q7-n8-r3-m1887': 'PASS', 'verify-rust@w-q7-n8-r3-m1887': 'PASS', 'verify-c@w-q7-n8-r3-m1893': 'PASS', 'verify-py-dilation@w-q7-n8-r3-m1893': 'PASS', 'verify-rust@w-q7-n8-r3-m1893': 'PASS', 'verify-c@w-q7-n9-r4-m1285': 'PASS', 'verify-py-dilation@w-q7-n9-r4-m1285': 'PASS', 'verify-rust@w-q7-n9-r4-m1285': 'PASS', 'verify-c@w-q7-n9-r4-m1351': 'PASS', 'verify-py-dilation@w-q7-n9-r4-m1351': 'PASS', 'verify-rust@w-q7-n9-r4-m1351': 'PASS'}

### lake-build-alvo-padrao (lean_build): PASS
- runtime_s: 5.597
- log_sha256: e13ecc10200abc4101c57bf20d463042bf738a151ff84aa6db6f9d8b0eba9423

### axiomas-dos-registros-formais (axiomas): FAIL
motivo: f-k2-6-1-eq12: axiomas reais ERROR: saída sem axiomas de SC.K_2_6_1_eq12 (rc=1) != registrados None; f-k7-9-4-le-1351: axiomas reais ERROR: saída sem axiomas de CoveringKernel.K7_9_4_le_1351_kernel (rc=1) != registrados None
- axioms: {'f-cert-of-go': ['propext', 'Classical.choice', 'Quot.sound'], 'f-chkn-sound': ['propext', 'Classical.choice', 'Quot.sound'], 'f-code12-card': ['propext', 'Classical.choice', 'Quot.sound'], 'f-code12-covers': ['propext', 'Classical.choice', 'Quot.sound'], 'f-even-inter': ['propext', 'Classical.choice', 'Quot.sound'], 'f-excess-bound': ['propext', 'Classical.choice', 'Quot.sound'], 'f-h2-counterexample': ['propext', 'Classical.choice', 'Quot.sound'], 'f-k2-6-1-eq12': 'ERROR: saída sem axiomas de SC.K_2_6_1_eq12 (rc=1)', 'f-k2-6-1-ge-11': ['propext', 'Classical.choice', 'Quot.sound'], 'f-k7-9-4-le-1351': 'ERROR: saída sem axiomas de CoveringKernel.K7_9_4_le_1351_kernel (rc=1)', 'f-sph-k4-10-4': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sph-k5-10-4': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sph-k5-7-2': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sph-k5-9-3': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sph-k5-9-4': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sph-k5-9-5': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sph-k7-8-3': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sph-k7-9-4': ['propext', 'Classical.choice', 'Quot.sound'], 'f-sphere-covering': ['propext', 'Classical.choice', 'Quot.sound']}

### auditoria-da-cadeia (auditoria): PASS
- events: 355

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
- w-q7-n9-r4-m1285: 89cbd6b290a10d8d708e9783a405b8a12ce5efd6a8ea2ee17568b3ee25c50f31
- w-q7-n9-r4-m1351: 6d1b0e1abb8079df06a28d5301607d3d5247e0f2005d72e13f695ce26f6e6b52

## Teoremas e axiomas registrados

- CoveringKernel.cert_of_go: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- SC.chkN_sound: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.code12_card: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.code12_covers: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.even_inter: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.excess_bound: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA6.H2_counterexample_uncond: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- SC.K_2_6_1_eq12: axiomas None; sorry_free=True; clean_build=False
- CoveringA6.K_2_6_1_ge_11: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringKernel.K7_9_4_le_1351_kernel: axiomas None; sorry_free=True; clean_build=False
- CoveringChain.SPH_K4_10_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_10_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_7_2_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_9_3_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_9_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K5_9_5_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K7_8_3_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringChain.SPH_K7_9_4_lb: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True
- CoveringA2.sphere_covering: axiomas ['propext', 'Classical.choice', 'Quot.sound']; sorry_free=True; clean_build=True

## Falhas

- axiomas-dos-registros-formais: f-k2-6-1-eq12: axiomas reais ERROR: saída sem axiomas de SC.K_2_6_1_eq12 (rc=1) != registrados None; f-k7-9-4-le-1351: axiomas reais ERROR: saída sem axiomas de CoveringKernel.K7_9_4_le_1351_kernel (rc=1) != registrados None
