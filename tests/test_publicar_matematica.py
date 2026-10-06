"""Publicador de /matematica: o que sobe para o bucket, sem rede."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "site"))
import publicar_matematica as p  # noqa: E402


def _pasta(tmp_path, html='<html><head><title>x</title></head><body><a href="#a">a</a></body></html>'):
    (tmp_path / "index.html").write_text(html, encoding="utf-8")
    (tmp_path / "estilo.css").write_text("body{}", encoding="utf-8")
    (tmp_path / "README.md").write_text("não sobe", encoding="utf-8")
    return tmp_path


def test_index_nao_vira_o_objeto_sem_extensao_que_o_worker_serve_em_barra_matematica(tmp_path):
    nomes = [n for n, _, _ in p.plano(_pasta(tmp_path))]
    assert nomes == ["genesis/matematica/estilo.css", "genesis/matematica"]


def test_css_relativo_resolveria_na_raiz_do_site_sem_base(tmp_path):
    html = dict((n, d) for n, _, d in p.plano(_pasta(tmp_path)))["genesis/matematica"].decode()
    assert '<head><base href="/matematica/">' in html


def test_ancora_recarregaria_a_pagina_com_base(tmp_path):
    html = dict((n, d) for n, _, d in p.plano(_pasta(tmp_path)))["genesis/matematica"].decode()
    assert 'href="/matematica#a"' in html


def test_index_com_base_proprio_e_aceito_e_quebra_os_caminhos(tmp_path):
    with pytest.raises(p.Recusa):
        p.plano(_pasta(tmp_path, '<html><head><base href="/"></head></html>'))


def test_arquivo_com_extensao_sem_content_type_sobe_sem_tipo(tmp_path):
    (_pasta(tmp_path) / "dados.bin").write_bytes(b"\0")
    with pytest.raises(p.Recusa):
        p.plano(tmp_path)


def test_pasta_sem_index_publica_um_site_sem_pagina(tmp_path):
    (tmp_path / "estilo.css").write_text("x", encoding="utf-8")
    with pytest.raises(p.Recusa):
        p.plano(tmp_path)


def test_publicador_escreve_fora_do_prefixo_da_pagina(tmp_path):
    for nome, _, _ in p.plano(_pasta(tmp_path)):
        assert nome == p.PREFIXO or nome.startswith(p.PREFIXO + "/")


def test_conferencia_no_ar_usa_user_agent_python_urllib_que_a_cloudflare_barra(monkeypatch):
    vistos = []

    class Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"x"

    def falso_urlopen(req, timeout=None):
        vistos.append(req.get_header("User-agent"))
        return Resp()

    monkeypatch.setattr(p.urllib.request, "urlopen", falso_urlopen)
    assert p.conferir_no_ar([("genesis/matematica", "text/html", b"x")]) == []
    assert vistos and not vistos[0].lower().startswith("python-urllib")


def test_beacon_injetado_pela_cloudflare_reprova_publicacao_identica():
    html = b'<html><body>x\n</body></html>'
    injetado = (b'<html><body>x\n<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v1" '
                b'data-cf-beacon=\'{"token": "t"}\' crossorigin="anonymous"></script>\n</body></html>')
    assert p.sem_beacon(injetado) == html
    assert p.sem_beacon(b"<script src='/app.js'></script>") == b"<script src='/app.js'></script>"
