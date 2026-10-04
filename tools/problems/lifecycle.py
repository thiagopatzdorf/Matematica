#!/usr/bin/env python3
"""Máquina de estados do Cartão de Problema (problems/SPEC.md, seção "Ciclo de vida").

Duas regras viram código aqui, para não dependerem de alguém lembrar:

* transição ilegal falha (`TransicaoIlegal`): não se chega a `certificado` sem passar por
  `verificado`, e nenhum estado além de `aceito`/`aberto` avança sem a evidência exigida;
* o histórico é somente-anexa: `verificar_historico` refaz o caminho inteiro e reprova um
  cartão cujo `estado` não é o da última entrada, ou cuja cadeia tem salto.

Só stdlib. Uso como biblioteca: `transicionar(cartao, ...)` devolve uma cópia nova.
"""
from __future__ import annotations

import copy
import re
from datetime import date, timedelta

ESTADOS = ("proposto", "aceito", "aberto", "reivindicado", "candidato",
           "verificado", "certificado", "publicado", "refutado", "arquivado")
PAPEIS = ("qualquer", "mantenedor", "avaliador", "dono", "sistema")
# Um papel mais forte cobre os mais fracos; "avaliador" (CI) e "sistema" (expiração) são
# papéis de máquina e só valem onde a tabela os cita.
EXPIRACAO_MAX_DIAS = 30

# destino -> (papéis que podem entrar nele). A origem é conferida em TRANSICOES.
PAPEL_PARA = {
    "aceito": {"mantenedor"},
    "aberto": {"mantenedor", "sistema"},   # sistema: reivindicação expirada
    "reivindicado": {"qualquer"},
    "candidato": {"qualquer"},
    "verificado": {"mantenedor", "avaliador"},
    "certificado": {"mantenedor", "avaliador"},
    "publicado": {"dono"},
    "refutado": {"mantenedor"},
    "arquivado": {"mantenedor"},
}

TRANSICOES = {
    None: {"proposto"},
    "proposto": {"aceito", "arquivado"},
    "aceito": {"aberto", "arquivado"},
    "aberto": {"reivindicado", "candidato", "refutado", "arquivado"},
    "reivindicado": {"aberto", "candidato", "refutado", "arquivado"},
    "candidato": {"verificado", "aberto", "refutado", "arquivado"},
    "verificado": {"certificado", "candidato", "refutado", "arquivado"},
    "certificado": {"publicado", "arquivado"},
    "publicado": {"arquivado"},
    "refutado": {"arquivado"},
    "arquivado": set(),
}

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TransicaoIlegal(ValueError):
    """A transição viola o ciclo de vida, o papel ou a exigência de evidência."""


def _txt(ev: dict, chave: str) -> bool:
    return isinstance(ev.get(chave), str) and bool(ev[chave].strip())


def exigencia(cartao: dict, para: str, quando: str, evidencia: dict) -> list[str]:
    """Lista o que falta na evidência para entrar em `para` (vazia = ok)."""
    falta: list[str] = []
    ev = evidencia if isinstance(evidencia, dict) else {}
    if para == "reivindicado":
        exp = ev.get("expira_em")
        if not isinstance(exp, str) or not _DATA.match(exp):
            falta.append("evidencia.expira_em (AAAA-MM-DD)")
        else:
            d0, d1 = date.fromisoformat(quando[:10]), date.fromisoformat(exp)
            if not d0 < d1 <= d0 + timedelta(days=EXPIRACAO_MAX_DIAS):
                falta.append(f"evidencia.expira_em tem de estar entre 1 e {EXPIRACAO_MAX_DIAS} dias depois de {quando[:10]}")
    elif para == "candidato":
        if not _txt(ev, "artefato"):
            falta.append("evidencia.artefato (caminho ou URL do candidato)")
        if not _HEX64.match(str(ev.get("sha256", ""))):
            falta.append("evidencia.sha256 do artefato (64 hex)")
    elif para == "verificado":
        av = (cartao.get("avaliador") or {}).get("id")
        if ev.get("avaliador") != av or not av:
            falta.append(f"evidencia.avaliador == avaliador.id do cartão ({av!r})")
        if ev.get("veredito") != "ok":
            falta.append('evidencia.veredito == "ok" (saída de avaliador exato)')
        if not _txt(ev, "saida"):
            falta.append("evidencia.saida (saída do avaliador, anexada)")
    elif para == "certificado":
        if ev.get("kernel") != "lean":
            falta.append('evidencia.kernel == "lean"')
        if not _txt(ev, "declaracao"):
            falta.append("evidencia.declaracao (nome do teorema aceito pelo kernel)")
    elif para == "refutado":
        if not (_txt(ev, "contraexemplo") or _txt(ev, "ref")):
            falta.append("evidencia.contraexemplo ou evidencia.ref")
    elif para == "arquivado":
        if not _txt(ev, "motivo"):
            falta.append("evidencia.motivo")
    elif para == "proposto":
        pass
    return falta


def checar(cartao: dict, de: str | None, para: str, quem: str, papel: str,
           quando: str, evidencia: dict, importacao: bool = False) -> None:
    """Levanta TransicaoIlegal se a transição de->para não é permitida."""
    if para not in ESTADOS:
        raise TransicaoIlegal(f"estado desconhecido: {para!r}")
    if para not in TRANSICOES.get(de, set()):
        raise TransicaoIlegal(f"transição ilegal: {de} -> {para} (permitidas de {de}: "
                              f"{sorted(TRANSICOES.get(de, set())) or 'nenhuma'})")
    if not quem or not isinstance(quem, str):
        raise TransicaoIlegal("toda transição precisa de `quem`")
    if papel not in PAPEIS:
        raise TransicaoIlegal(f"papel desconhecido: {papel!r}")
    if para == "proposto":
        pass
    elif not importacao and papel not in PAPEL_PARA[para]:
        raise TransicaoIlegal(f"papel {papel!r} não pode entrar em {para} (pode: {sorted(PAPEL_PARA[para])})")
    if importacao and para == "publicado":
        raise TransicaoIlegal("importação nunca publica: `publicado` é só do dono")
    falta = exigencia(cartao, para, quando, evidencia)
    if falta:
        raise TransicaoIlegal(f"evidência insuficiente para {para}: " + "; ".join(falta))
    # Quem submete o candidato de uma reivindicação é quem reivindicou (ou um mantenedor).
    if de == "reivindicado" and para == "candidato" and papel != "mantenedor":
        dono = next((h for h in reversed(cartao.get("historico", [])) if h["para"] == "reivindicado"), None)
        if dono and dono["quem"] != quem:
            raise TransicaoIlegal(f"reivindicado por {dono['quem']}: só ele (ou um mantenedor) submete candidato")


def transicionar(cartao: dict, para: str, quem: str, papel: str, quando: str,
                 evidencia: dict | None = None) -> dict:
    """Devolve cópia do cartão com a transição aplicada e anexada ao histórico."""
    de = cartao.get("estado")
    ev = evidencia or {}
    checar(cartao, de, para, quem, papel, quando, ev)
    novo = copy.deepcopy(cartao)
    novo["estado"] = para
    novo.setdefault("historico", []).append(
        {"quem": quem, "papel": papel, "quando": quando, "de": de, "para": para, "evidencia": ev})
    return novo


def expirar(cartao: dict, hoje: str) -> dict:
    """Reivindicação vencida volta a `aberto` (quem: sistema). Sem vencer, devolve o mesmo cartão."""
    if cartao.get("estado") != "reivindicado":
        return cartao
    ult = next(h for h in reversed(cartao["historico"]) if h["para"] == "reivindicado")
    if hoje <= ult["evidencia"]["expira_em"]:
        return cartao
    return transicionar(cartao, "aberto", "sistema", "sistema", hoje,
                        {"motivo": f"reivindicação de {ult['quem']} expirou em {ult['evidencia']['expira_em']}"})


def verificar_historico(cartao: dict) -> list[str]:
    """Refaz a cadeia do histórico; devolve a lista de erros (vazia = coerente)."""
    erros: list[str] = []
    hist = cartao.get("historico")
    if not isinstance(hist, list) or not hist:
        return ["historico vazio: todo cartão nasce com a entrada `proposto`"]
    atual = None
    parcial: dict = {"avaliador": cartao.get("avaliador"), "historico": []}
    for i, h in enumerate(hist):
        rot = f"historico[{i}]"
        if h.get("de") != atual:
            erros.append(f"{rot}: `de` = {h.get('de')!r}, mas o estado anterior era {atual!r}")
        try:
            checar(parcial, h.get("de"), h.get("para"), h.get("quem"), h.get("papel"),
                   str(h.get("quando", "")), h.get("evidencia") or {},
                   importacao=h.get("origem") == "importacao")
        except (TransicaoIlegal, ValueError) as e:  # ValueError: data malformada
            erros.append(f"{rot}: {e}")
        atual = h.get("para")
        parcial["historico"].append(h)
    if cartao.get("estado") != atual:
        erros.append(f"estado {cartao.get('estado')!r} difere da última entrada do histórico ({atual!r})")
    return erros
