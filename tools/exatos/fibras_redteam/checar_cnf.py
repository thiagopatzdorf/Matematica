"""Confere, com um solver, se um código JÁ na forma normal satisfaz a CNF (fib_encode.codificar)
do seu perfil: fixa as variáveis x pelas palavras (assunções) e pede SAT. Sem cobertura, as
cláusulas de cobertura são retiradas (códigos aleatórios que não cobrem)."""



class Checador:
    def __init__(self, enc, q, n, M, smin, quebra_kw=None):
        self.enc, self.q, self.n, self.M, self.smin = enc, q, n, M, smin
        self.kw = quebra_kw or {}
        self._cache = {}

    def _cnf(self, prefixo, cobertura):
        chave = (prefixo, cobertura)
        if chave not in self._cache:
            if len(self._cache) > 64:
                for s in self._cache.values():
                    s[0].delete()
                self._cache.clear()
            cnf, x, sim0, _ = self.enc.codificar(self.q, self.n, self.M, prefixo, self.smin, **self.kw)
            cl = list(cnf.cl)
            if not cobertura:
                n0 = len(self.enc.codificar(self.q, self.n, self.M, prefixo, self.smin, quebra=False)[0].cl)
                ini = n0 - self.q ** self.n
                cl = cl[:ini] + cl[n0:]
            from pysat.solvers import Solver  # import tardio (CI sem pysat)

            s = Solver(name="cadical195", bootstrap_with=cl)
            self._cache[chave] = (s, x, sim0)
        return self._cache[chave]

    def satisfaz(self, prefixo, norm, cobertura):
        s, x, sim0 = self._cnf(prefixo, cobertura)
        if [w[0] for w in norm] != sim0:
            return False
        ass = []
        for w, c in enumerate(norm):
            for i in range(1, self.n):
                for a in range(self.q):
                    ass.append(x[w][i][a] if c[i] == a else -x[w][i][a])
        return s.solve(assumptions=ass)
