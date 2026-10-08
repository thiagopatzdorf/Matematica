"""Captura das relações do CADO: o que o filtro consumiu, hexadecimal do purge e nada de caminho de máquina."""
import gzip
import json
import sys

import pytest

from conftest import RAIZ

sys.path.insert(0, str(RAIZ / "tools" / "fatoracao"))
import captura_relacoes as cap  # noqa: E402

REL1 = ["-816765,122:3d,97:2,2,b,fa07", "1805781,1052:6d,3a9:2,5,fa07,608a5"]
REL2 = ["1805781,1052:6d,3a9:2,5,fa07,608a5", "290567,300:191,b89:2,3,fa0b"]  # a primeira repete a do bloco 1
EXTRA = ["999,7:5,7:2,fa11"]


def _bloco(pasta, nome, relacoes, q, n_reports, cpu):
    texto = ("# (abc1234) /home/fulano/cado-nfs/build/vm/sieve/las -poly /home/fulano/x.poly\n"
             f"# Sieving side-1 q={q}; rho=3; a0=1; b0=2;\n" + "\n".join(relacoes) + "\n"
             f"# Total {n_reports} reports [0.5s/r, 2.0r/sq]\n# Total cpu time {cpu}s [add -T for a breakdown]\n")
    with gzip.open(pasta / "c9.upload" / nome, "wt", encoding="utf-8") as fh:
        fh.write(texto)


@pytest.fixture
def pasta_cado(tmp_path):
    """Uma pasta de trabalho do CADO em miniatura, com as armadilhas que apareceram de verdade."""
    w = tmp_path / "wd"
    (w / "c9.upload").mkdir(parents=True)
    _bloco(w, "c9.1-2.gz", REL1, 11, 2, "3.50")
    _bloco(w, "c9.2-3.gz", REL2, 13, 2, "4.00")
    _bloco(w, "c9.9-10.gz", EXTRA, 17, 1, "1.00")  # chegou depois do fim da coleta: o filtro não consumiu
    (w / "c9.dup1.filelist.1").write_text("/x/y/c9.upload/c9.1-2.gz\n/x/y/c9.upload/c9.2-3.gz\n", encoding="utf-8")
    with gzip.open(w / "c9.freerel.gz", "wt", encoding="utf-8") as fh:
        fh.write("# free\n3d,0:30,31,32\n")
    with gzip.open(w / "c9.purged.gz", "wt", encoding="utf-8") as fh:
        fh.write("# 3 100 2\n-1f,b:1,2,3\n11,2:4,5\n3d,0:30,31,32\n")  # tudo em hexadecimal: 11 hex é 17
    with gzip.open(w / "c9.index.gz", "wt", encoding="utf-8") as fh:
        fh.write("2\n2 0 1\n1 2\n")
    (w / "c9.purge.stdout.1").write_text(
        "Sing. rem.: begin with: nrows=10 ncols=8 excess=2 at 0.1\nSing. rem.:   iter 001: nrows=7 ncols=6 excess=1 at 0.1\n"
        "Step 1 of 10: target excess is 1\nCliq. rem.: x\nSing. rem.: begin with: nrows=5 ncols=4 excess=1 at 0.2\n", encoding="utf-8")
    (w / "c9.poly").write_text("n: 15\nskew: 1.0\nc0: 1\nc1: 2\nY0: -3\nY1: 4\n", encoding="utf-8")
    (w / "c9.parameters_snapshot.0").write_text("tasks.I=10\nworkdir=/home/fulano/wd\nname=c9\n", encoding="utf-8")
    return w


def test_bloco_extra_do_upload_que_o_filtro_nao_consumiu_entra_na_captura(pasta_cado, tmp_path):
    m = cap.empacotar(pasta_cado, "c9", tmp_path / "cap")
    assert (m["n_blocos"], m["n_brutas"]) == (2, 4)
    linhas = gzip.open(tmp_path / "cap" / "relacoes.tsv.gz", "rt").read()
    assert "999\t7" not in linhas


def test_purgadas_em_hexadecimal_lidas_como_decimal(pasta_cado, tmp_path):
    cap.empacotar(pasta_cado, "c9", tmp_path / "cap")
    linhas = [l for l in gzip.open(tmp_path / "cap" / "purgadas.tsv.gz", "rt").read().splitlines() if not l.startswith("#")]
    assert linhas == ["-31\t11", "17\t2", "61\t0"]


def test_estatisticas_de_special_q_e_cpu_por_bloco(pasta_cado, tmp_path):
    cap.empacotar(pasta_cado, "c9", tmp_path / "cap")
    blocos = json.loads((tmp_path / "cap" / "arquivos.json").read_text())
    assert [(b["n_relacoes"], b["n_sq"], b["cpu_s"]) for b in blocos] == [(2, 1, 3.5), (2, 1, 4.0)]


def test_captura_com_caminho_de_maquina_no_conteudo(pasta_cado, tmp_path):
    cap.empacotar(pasta_cado, "c9", tmp_path / "cap")
    for arquivo in (tmp_path / "cap").iterdir():
        dados = gzip.open(arquivo, "rb").read() if arquivo.suffix == ".gz" and arquivo.name != "index.gz" else arquivo.read_bytes()
        assert b"/home/" not in dados and b"/tmp/" not in dados and b"fulano" not in dados, arquivo.name


def test_captura_que_muda_de_sha256_ao_ser_refeita(pasta_cado, tmp_path):
    a = cap.empacotar(pasta_cado, "c9", tmp_path / "a")
    b = cap.empacotar(pasta_cado, "c9", tmp_path / "b")
    assert a["sha256"] == b["sha256"]


def test_gzip_da_captura_com_data_no_cabecalho_que_so_aparece_um_segundo_depois(pasta_cado, tmp_path):
    cap.empacotar(pasta_cado, "c9", tmp_path / "cap")
    for nome in ("relacoes.tsv.gz", "livres.tsv.gz", "purgadas.tsv.gz"):
        cabecalho = (tmp_path / "cap" / nome).read_bytes()[:10]
        assert cabecalho[4:8] == b"\x00\x00\x00\x00", nome  # campo MTIME do gzip zerado
        assert cabecalho[3] == 0, nome  # sem nome de arquivo no cabeçalho


def test_manifesto_com_sha256_que_nao_confere_com_o_arquivo(pasta_cado, tmp_path):
    m = cap.empacotar(pasta_cado, "c9", tmp_path / "cap")
    for nome, h in m["sha256"].items():
        assert cap.sha256_arquivo(tmp_path / "cap" / nome) == h


def test_filtro_que_leu_arquivos_na_linha_de_comando_sem_filelist(pasta_cado, tmp_path):
    (pasta_cado / "c9.dup1.filelist.1").unlink()
    (pasta_cado / "c9.log").write_text(
        "x Debug:ignorar\nPID1 Command:Command: /a/filter/dup1 -prefix dup1.0 -out /b/c9.dup1/ -n 1 /z/c9.upload/c9.1-2.gz /z/c9.upload/c9.2-3.gz\n",
        encoding="utf-8")
    assert cap.arquivos_consumidos(pasta_cado, "c9") == ["c9.1-2.gz", "c9.2-3.gz"]


def test_captura_sem_saber_o_que_o_filtro_consumiu_cai_num_glob(pasta_cado):
    (pasta_cado / "c9.dup1.filelist.1").unlink()
    with pytest.raises(FileNotFoundError, match="não dá para saber"):
        cap.arquivos_consumidos(pasta_cado, "c9")


def test_bloco_do_filelist_que_sumiu_do_upload_passa_em_silencio(pasta_cado):
    (pasta_cado / "c9.upload" / "c9.2-3.gz").unlink()
    with pytest.raises(FileNotFoundError, match="ausentes"):
        cap.arquivos_consumidos(pasta_cado, "c9")


def test_purge_do_cado_lido_com_a_etapa_errada(pasta_cado, tmp_path):
    p = cap.empacotar(pasta_cado, "c9", tmp_path / "cap")["purge"]
    assert p["inicio"] == {"nrows": 10, "ncols": 8, "excess": 2}
    assert p["apos_singletons"] == {"nrows": 7, "ncols": 6, "excess": 1}  # a última linha ANTES da primeira etapa de cliques
    assert p["final"] == {"nrows": 3, "ncols": 2, "excess": 1}


LOG_DUAS_RODADAS = ("PID1 Command:Command: /a/filter/dup1 -prefix dup1.0 -out /b/c9.dup1/ -n 1 -filelist /b/c9.dup1.filelist.1 > o 2> e\n"
                    "PID1 Command:Command: /a/filter/dup1 -prefix dup1.1 -out /b/c9.dup1/ -n 1 /z/c9.upload/c9.9-10.gz > o 2> e\n")


def test_rodada_de_filtragem_posterior_que_a_captura_ignorava(pasta_cado, tmp_path):
    # o filtro faltou de relação na 1ª rodada, o CADO sorteou mais um bloco e o passou só na linha de comando do dup1
    (pasta_cado / "c9.log").write_text(LOG_DUAS_RODADAS, encoding="utf-8")
    assert cap.arquivos_consumidos(pasta_cado, "c9") == ["c9.1-2.gz", "c9.2-3.gz", "c9.9-10.gz"]
    m = cap.empacotar(pasta_cado, "c9", tmp_path / "cap")
    assert m["n_brutas"] == len(REL1) + len(REL2) + len(EXTRA)


def test_purge_final_lido_da_primeira_rodada_quando_houve_mais_de_uma(pasta_cado, tmp_path):
    (pasta_cado / "c9.purge.stdout.2").write_text(
        "Sing. rem.: begin with: nrows=12 ncols=9 excess=3 at 0.1\nSing. rem.:   iter 001: nrows=9 ncols=7 excess=2 at 0.1\n"
        "Step 1 of 10: target excess is 1\n", encoding="utf-8")
    p = cap.empacotar(pasta_cado, "c9", tmp_path / "cap")["purge"]
    assert p["inicio"] == {"nrows": 12, "ncols": 9, "excess": 3} and p["apos_singletons"] == {"nrows": 9, "ncols": 7, "excess": 2}
    assert [r["inicio"]["nrows"] for r in p["rodadas"]] == [10, 12]


def test_ideais_ruins_que_a_pasta_do_cado_nao_guarda_vem_da_ferramenta(pasta_cado, tmp_path):
    # a ferramenta de verdade sai com código 1 mas grava os arquivos; o falso imita isso
    f = tmp_path / "nt.sh"
    f.write_text('#!/bin/sh\nwhile [ $# -gt 0 ]; do [ "$1" = -badidealinfo ] && echo "2 1 2 1 2 -2" > "$2"; shift; done\nexit 1\n')
    f.chmod(0o755)
    cap.empacotar(pasta_cado, "c9", tmp_path / "cap", numbertheory=f)
    assert (tmp_path / "cap" / "badideais.txt").read_text().strip() == "2 1 2 1 2 -2"
    assert "badideais.txt" in json.loads((tmp_path / "cap" / "manifest.json").read_text())["sha256"]
