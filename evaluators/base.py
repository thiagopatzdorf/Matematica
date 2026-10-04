"""Contrato único de verificação: toda avaliação devolve um `Resultado` serializável em JSON.

Doutrina: cabe uma engine onde verificar é mais barato que gerar, e o que decide é o avaliador,
barato e exato. Aqui o avaliador é cidadão de primeira classe: pessoa, agente, CI e MCP chamam
a mesma coisa (`python3 -m evaluators <id> <alvo> [--json]`) e recebem o mesmo formato.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


@dataclass
class Resultado:
    avaliador: str
    versao: str
    ok: bool
    veredito: str  # texto curto, uma linha
    evidencia: dict = field(default_factory=dict)
    sha256_arquivo: str | None = None  # bytes do arquivo como está em disco
    sha256_canonico: str | None = None  # palavras ordenadas por byte, unidas por LF (ver README)
    tempo_s: float = 0.0
    comando_reproducao: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, **kw) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, **kw)

    @property
    def erro_de_ambiente(self) -> bool:
        """True quando o avaliador não conseguiu avaliar (sem compilador, alvo ausente): não é reprovação."""
        return "erro" in self.evidencia


class Avaliador:
    """Subclasse define `id`, `versao`, `descricao` e `avaliar(alvo, **opcoes) -> Resultado`."""

    id: str = ""
    versao: str = "1"
    descricao: str = ""
    alvo_padrao: str | None = None  # usado quando a CLI é chamada sem alvo

    def avaliar(self, alvo: str | Path, **opcoes) -> Resultado:  # pragma: no cover - interface
        raise NotImplementedError

    def executar(self, alvo: str | Path | None, **opcoes) -> Resultado:
        """Chama `avaliar` medindo o tempo, para o chamador não repetir o cronômetro."""
        t0 = time.perf_counter()
        r = self.avaliar(alvo if alvo is not None else self.alvo_padrao, **opcoes)
        r.tempo_s = round(time.perf_counter() - t0, 3)
        return r

    def resultado(self, ok: bool, veredito: str, **kw) -> Resultado:
        return Resultado(avaliador=self.id, versao=self.versao, ok=ok, veredito=veredito, **kw)

    def falha_de_ambiente(self, mensagem: str, codigo: str, **kw) -> Resultado:
        return self.resultado(False, mensagem, evidencia={"erro": codigo}, **kw)


_REGISTRO: dict[str, Avaliador] = {}


def registrar(cls):
    """Decorador de classe: instancia e registra o avaliador pelo `id`."""
    inst = cls()
    if not inst.id or inst.id in _REGISTRO:
        raise ValueError(f"id de avaliador vazio ou repetido: {inst.id!r}")
    _REGISTRO[inst.id] = inst
    return cls


def obter(id_: str) -> Avaliador:
    carregar_todos()
    if id_ not in _REGISTRO:
        raise KeyError(f"avaliador desconhecido: {id_!r}; disponíveis: {', '.join(sorted(_REGISTRO))}")
    return _REGISTRO[id_]


def ids() -> list[str]:
    carregar_todos()
    return sorted(_REGISTRO)


def carregar_todos() -> None:
    from . import covering_code, lean_honesty, ponte_ledger  # noqa: F401  (o import registra)


def sha256_arquivo(caminho: str | Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def sha256_canonico(palavras) -> str:
    """Mesma definição de scripts/codes/codefmt.py e de tools/verify/verify.c."""
    return hashlib.sha256(("\n".join(sorted(palavras)) + "\n").encode()).hexdigest()


def relativo(caminho: str | Path, raiz: Path = RAIZ) -> str:
    p = Path(caminho).resolve()
    try:
        return str(p.relative_to(raiz))
    except ValueError:
        return str(p)
