"""tools/infra/lake_cache.sh: cache da Mathlib compartilhado entre worktrees por hardlink.

Cada teste monta um repositório falso (manifesto com dois pacotes, cada um um repo git numa revisão)
e confere a garantia que motivou o script: o worktree ganha os pacotes sem duplicar disco, sem depender
de pasta alheia, e nada que ele faça com a própria cópia apaga ou altera o cache.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "tools" / "infra" / "lake_cache.sh"

pytestmark = pytest.mark.skipif(shutil.which("git") is None or shutil.which("bash") is None,
                                reason="precisa de git e bash")

GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}


def git(*args, cwd):
    out = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                         env={**os.environ, **GIT_ENV})
    return out.stdout.strip()


def pacote(pasta: Path, olean: str) -> str:
    """Repo git com um .olean em .lake/build (ignorado pelo git, como na Mathlib); devolve o HEAD."""
    pasta.mkdir(parents=True)
    git("init", "-q", cwd=pasta)
    (pasta / "Fonte.lean").write_text("-- fonte\n")
    (pasta / ".gitignore").write_text(".lake\n")
    build = pasta / ".lake" / "build" / "lib" / "lean"
    build.mkdir(parents=True)
    (build / "Mod.olean").write_text(olean)
    git("add", ".", cwd=pasta)
    git("commit", "-qm", "c", cwd=pasta)
    return git("rev-parse", "HEAD", cwd=pasta)


@pytest.fixture
def cenario(tmp_path):
    origem = tmp_path / "origem" / "packages"
    revs = {nome: pacote(origem / nome, f"olean de {nome}") for nome in ("mathlib", "batteries")}
    principal = tmp_path / "Repo"
    principal.mkdir()
    git("init", "-q", "-b", "main", cwd=principal)
    manifesto = {"packages": [{"name": n, "rev": r} for n, r in revs.items()]}
    (principal / "lake-manifest.json").write_text(json.dumps(manifesto))
    (principal / ".gitignore").write_text("/.lake\n")
    git("add", ".", cwd=principal)
    git("commit", "-qm", "base", cwd=principal)
    wt = tmp_path / "wt"
    git("worktree", "add", "-q", str(wt), cwd=principal)
    cache = tmp_path / "cache"
    return {"origem": origem, "wt": wt, "cache": cache, "revs": revs, "raiz": tmp_path, "principal": principal}


def rodar(c, *args, cwd=None, cache=True):
    env = {**os.environ, **GIT_ENV}
    env.pop("LAKE_CACHE_DIR", None)
    if cache:
        env["LAKE_CACHE_DIR"] = str(c["cache"])
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd or c["wt"], capture_output=True, text=True, env=env)


def semeado(c):
    r = rodar(c, "semear", str(c["origem"]))
    assert r.returncode == 0, r.stderr
    return c["cache"] / c["revs"]["mathlib"] / "packages"


def test_ligar_entrega_os_pacotes_por_hardlink_sem_duplicar_disco(cenario):
    destino = semeado(cenario)
    r = rodar(cenario, "ligar")
    assert r.returncode == 0, r.stderr
    rel = Path("mathlib/.lake/build/lib/lean/Mod.olean")
    no_wt = cenario["wt"] / ".lake" / "packages" / rel
    assert not (cenario["wt"] / ".lake" / "packages").is_symlink()
    assert no_wt.stat().st_ino == (destino / rel).stat().st_ino


def test_desligar_o_worktree_nao_apaga_nem_altera_o_cache(cenario):
    destino = semeado(cenario)
    assert rodar(cenario, "ligar").returncode == 0
    assert rodar(cenario, "desligar").returncode == 0
    assert not (cenario["wt"] / ".lake" / "packages").exists()
    assert rodar(cenario, "verificar").returncode == 0
    assert (destino / "mathlib/.lake/build/lib/lean/Mod.olean").read_text() == "olean de mathlib"


def test_apagar_o_cache_nao_quebra_o_worktree_ja_ligado(cenario):
    destino = semeado(cenario)
    assert rodar(cenario, "ligar").returncode == 0
    shutil.rmtree(destino.parent)
    olean = cenario["wt"] / ".lake/packages/mathlib/.lake/build/lib/lean/Mod.olean"
    assert olean.read_text() == "olean de mathlib"


def test_ligar_recusa_apagar_packages_existente_sem_forcar(cenario):
    semeado(cenario)
    meu = cenario["wt"] / ".lake" / "packages" / "meu"
    meu.mkdir(parents=True)
    r = rodar(cenario, "ligar")
    assert r.returncode != 0 and "--forcar" in r.stderr
    assert meu.exists()
    assert rodar(cenario, "ligar", "--forcar").returncode == 0
    assert not meu.exists()


def test_ligar_troca_symlink_para_pasta_alheia_pela_copia(cenario):
    semeado(cenario)
    (cenario["wt"] / ".lake").mkdir()
    (cenario["wt"] / ".lake" / "packages").symlink_to(cenario["raiz"] / "worktree-que-sumiu")
    r = rodar(cenario, "ligar")
    assert r.returncode == 0, r.stderr
    pacotes = cenario["wt"] / ".lake" / "packages"
    assert not pacotes.is_symlink() and (pacotes / "batteries").is_dir()


def test_semear_recusa_origem_em_revisao_diferente_do_manifesto(cenario):
    bat = cenario["origem"] / "batteries"
    (bat / "Outro.lean").write_text("x\n")
    git("add", ".", cwd=bat)
    git("commit", "-qm", "avanca", cwd=bat)
    r = rodar(cenario, "semear", str(cenario["origem"]))
    assert r.returncode != 0 and "batteries" in r.stderr
    assert not (cenario["cache"] / cenario["revs"]["mathlib"]).exists()


def test_verificar_acusa_olean_do_cache_alterado(cenario):
    destino = semeado(cenario)
    (destino / "batteries/.lake/build/lib/lean/Mod.olean").write_text("corrompido")
    r = rodar(cenario, "verificar")
    assert r.returncode != 0 and "mudou" in r.stderr


def test_raiz_padrao_do_cache_fica_ao_lado_do_checkout_principal(cenario):
    r = rodar(cenario, "onde", cache=False)
    assert r.returncode == 0, r.stderr
    esperado = cenario["raiz"].resolve() / ".mathlib-cache" / cenario["revs"]["mathlib"] / "packages"
    assert Path(r.stdout.strip()) == esperado
