"""psc_io.py -- leitura do formato PSC1 (patch_inst.c) e ILP exato de referência (HiGHS)."""
import struct, sys
import numpy as np


def load(path):
    with open(path, "rb") as f:
        hdr = struct.unpack("<7I", f.read(28))
        if hdr[0] != 0x31435350:
            raise ValueError("formato inválido")
        q, n, R, T, npts, nsets = hdr[1:]
        (npairs,) = struct.unpack("<Q", f.read(8))
        pts = np.frombuffer(f.read(4 * npts), dtype="<u4")
        sets = np.frombuffer(f.read(4 * nsets), dtype="<u4")
        off = np.frombuffer(f.read(8 * (nsets + 1)), dtype="<u8")
        elem = np.frombuffer(f.read(4 * npairs), dtype="<u4")
    return dict(q=q, n=n, R=R, T=T, pts=pts, sets=sets, off=off, elem=elem)


def write(path, q, n, R, T, pts, sets, members):
    """members: lista (por conjunto) de índices de pontos."""
    off = np.zeros(len(sets) + 1, dtype="<u8")
    off[1:] = np.cumsum([len(m) for m in members])
    with open(path, "wb") as f:
        f.write(struct.pack("<7I", 0x31435350, q, n, R, T, len(pts), len(sets)))
        f.write(struct.pack("<Q", int(off[-1])))
        f.write(np.asarray(pts, dtype="<u4").tobytes())
        f.write(np.asarray(sets, dtype="<u4").tobytes())
        f.write(off.tobytes())
        for m in members:
            f.write(np.asarray(m, dtype="<u4").tobytes())


def ilp(inst, tlim=600.0):
    import highspy
    nsets, npts = len(inst["sets"]), len(inst["pts"])
    off, elem = inst["off"], inst["elem"]
    h = highspy.Highs(); h.setOptionValue("output_flag", False); h.setOptionValue("time_limit", tlim)
    h.addVars(nsets, np.zeros(nsets), np.ones(nsets))
    idx = np.arange(nsets, dtype=np.int32)
    h.changeColsCost(nsets, idx, np.ones(nsets))
    h.changeColsIntegrality(nsets, idx, np.array([highspy.HighsVarType.kInteger] * nsets))
    col = np.repeat(np.arange(nsets), np.diff(off).astype(np.int64))
    order = np.argsort(elem, kind="stable")
    r, c = elem[order].astype(np.int64), col[order]
    starts = np.searchsorted(r, np.arange(npts))
    h.addRows(npts, np.ones(npts), np.full(npts, highspy.kHighsInf), len(r), starts.astype(np.int32), c.astype(np.int32), np.ones(len(r)))
    h.run()
    info = h.getInfo()
    return dict(status=h.modelStatusToString(h.getModelStatus()), obj=info.objective_function_value, dual=info.mip_dual_bound)


if __name__ == "__main__":
    print(ilp(load(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 600.0))


def from_orlib(txt_path, out_path):
    """Converte uma instância da OR-Library (scp*.txt: m n, custos, depois por linha k e as
    k colunas 1-indexadas) para PSC1, IGNORANDO os custos (versão unicusto, como na
    literatura de USCP)."""
    tok = open(txt_path).read().split()
    it = iter(tok)
    m, n = int(next(it)), int(next(it))
    for _ in range(n):
        next(it)
    members = [[] for _ in range(n)]
    for i in range(m):
        k = int(next(it))
        for _ in range(k):
            members[int(next(it)) - 1].append(i)
    keep = [j for j in range(n) if members[j]]
    write(out_path, 0, 0, 0, 0, np.arange(m), np.array(keep), [members[j] for j in keep])
    return m, len(keep)
