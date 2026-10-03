"""Onde as propostas moram: um bucket GCS com ACL por objeto.

Por que ACL por objeto e não o bucket público de sempre: medido em
2026-09-28, o `mybagcenter-static-legado` dá `roles/storage.objectViewer` a
`allUsers`, e esse papel inclui `storage.objects.list` -- qualquer um lista
`genesis/` pela API JSON sem credencial. Uma proposta ali teria o token da URL
exposto na listagem, e com ele o preço do cliente. Aqui o bucket é privado
(nenhum papel para allUsers, então ninguém lista) e só os objetos de
`propostas/` recebem `publicRead`: quem tem a URL exata lê, ninguém descobre.

Layout (o Worker só busca `propostas/`; o resto nunca sai pela borda):

    propostas/<id>/index.html, img/*, marca/*   publicRead, no-cache
    _fonte/<id>/proposta.json                    privado (o dado que gera a página)
    _fonte/<id>/meta.json                        privado (quem criou, quando, estado)
    _fonte/<id>/historico/<ts>.json              privado (versão anterior a cada atualizar)
    _arquivo/<id>/...                            privado (arquivar move para cá)
    _cache/logos/<slug>.svg + logos.json         privado (logos registrados pela tool `logo`)

Credencial: a service account anexada ao Cloud Run, pelo metadata server.
Nenhuma chave em lugar nenhum.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Protocol

API = "https://storage.googleapis.com/storage/v1"
UPLOAD = "https://storage.googleapis.com/upload/storage/v1"
METADATA = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"


class ErroArmazem(Exception):
    pass


class Armazem(Protocol):
    def por(self, nome: str, dados: bytes, tipo: str, *, publico: bool) -> None: ...
    def ler(self, nome: str) -> bytes | None: ...
    def listar(self, prefixo: str) -> list[str]: ...
    def mover(self, de: str, para: str, *, publico: bool) -> None: ...


class ArmazemGCS:
    def __init__(self, bucket: str, token=None):
        self.bucket = bucket
        self._token_fn = token or self._token_metadata
        self._tok: tuple[str, float] | None = None

    def _token_metadata(self) -> str:
        if self._tok and self._tok[1] > time.time() + 60:
            return self._tok[0]
        req = urllib.request.Request(METADATA, headers={"Metadata-Flavor": "Google"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        self._tok = (d["access_token"], time.time() + int(d.get("expires_in", 300)))
        return self._tok[0]

    def _pedir(self, metodo: str, url: str, dados: bytes | None = None, tipo: str | None = None):
        h = {"Authorization": "Bearer " + self._token_fn()}
        if tipo:
            h["Content-Type"] = tipo
        req = urllib.request.Request(url, data=dados, method=metodo, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def _obj(self, nome: str) -> str:
        return f"{API}/b/{self.bucket}/o/{urllib.parse.quote(nome, safe='')}"

    def por(self, nome: str, dados: bytes, tipo: str, *, publico: bool) -> None:
        # no-cache: atualizar e arquivar valem na hora (o Worker e o navegador
        # revalidam em vez de servir a versão anterior por minutos).
        meta = json.dumps({"name": nome, "contentType": tipo, "cacheControl": "no-cache"}).encode()
        b = "infinitofronteira7d1"
        corpo = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode() + meta
                 + f"\r\n--{b}\r\nContent-Type: {tipo}\r\n\r\n".encode() + dados + f"\r\n--{b}--".encode())
        acl = "publicRead" if publico else "private"
        st, r = self._pedir("POST", f"{UPLOAD}/b/{self.bucket}/o?uploadType=multipart&predefinedAcl={acl}",
                            corpo, f"multipart/related; boundary={b}")
        if st != 200:
            raise ErroArmazem(f"upload de {nome}: HTTP {st}: {r[:300]!r}")

    def ler(self, nome: str) -> bytes | None:
        st, r = self._pedir("GET", self._obj(nome) + "?alt=media")
        if st == 404:
            return None
        if st != 200:
            raise ErroArmazem(f"leitura de {nome}: HTTP {st}: {r[:300]!r}")
        return r

    def listar(self, prefixo: str) -> list[str]:
        nomes, pagina = [], None
        while True:
            q = {"prefix": prefixo, "fields": "items(name),nextPageToken", "maxResults": 1000}
            if pagina:
                q["pageToken"] = pagina
            st, r = self._pedir("GET", f"{API}/b/{self.bucket}/o?{urllib.parse.urlencode(q)}")
            if st != 200:
                raise ErroArmazem(f"listagem de {prefixo}: HTTP {st}: {r[:300]!r}")
            d = json.loads(r)
            nomes += [i["name"] for i in d.get("items", [])]
            pagina = d.get("nextPageToken")
            if not pagina:
                return nomes

    def mover(self, de: str, para: str, *, publico: bool) -> None:
        acl = "publicRead" if publico else "private"
        url = (f"{self._obj(de)}/rewriteTo/b/{self.bucket}/o/{urllib.parse.quote(para, safe='')}"
               f"?destinationPredefinedAcl={acl}")
        st, r = self._pedir("POST", url, b"{}", "application/json")
        if st != 200 or not json.loads(r).get("done", False):
            raise ErroArmazem(f"cópia {de} -> {para}: HTTP {st}: {r[:300]!r}")
        # só apaga a origem depois que a cópia existe (a prova vem antes)
        st, r = self._pedir("GET", self._obj(para))
        if st != 200:
            raise ErroArmazem(f"cópia {para} não confirmada (HTTP {st}); origem mantida")
        st, r = self._pedir("DELETE", self._obj(de))
        if st not in (200, 204, 404):
            raise ErroArmazem(f"remoção de {de} depois da cópia: HTTP {st}")


class ArmazemMemoria:
    """Para os testes: mesmo contrato, num dicionário. Guarda se é público."""

    def __init__(self):
        self.objs: dict[str, tuple[bytes, str, bool]] = {}

    def por(self, nome, dados, tipo, *, publico):
        self.objs[nome] = (dados, tipo, publico)

    def ler(self, nome):
        o = self.objs.get(nome)
        return o[0] if o else None

    def listar(self, prefixo):
        return sorted(n for n in self.objs if n.startswith(prefixo))

    def mover(self, de, para, *, publico):
        dados, tipo, _ = self.objs[de]
        self.objs[para] = (dados, tipo, publico)
        del self.objs[de]
