// Inércia "excepcional" dos ideais primos acima de p | disc(f)*lc(f), como o CADO-NFS a calcula em
// renumber_t::inertia_from_p_r (utils/renumber.cpp). O dup2 divide o expoente de p na relação por esse número.
//
//   inercia <arquivo.poly>   ->   uma linha "lado p r inercia" por ideal com inércia != 1 (r = p é o ponto no infinito)
//
// Compilar dentro de uma árvore construída do CADO: veja tools/fatoracao/cado/README.md.
#include "cado.h" // IWYU pragma: keep
#include <cstdio>
#include <vector>
#include <iostream>
#include "badideals.hpp"
#include "cxx_mpz.hpp"
#include "mpz_poly.h"
#include "cado_poly.hpp"
#include "gmp_aux.h"
#include "misc.h"

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "uso: %s <poly>\n", argv[0]); return 2; }
    cxx_cado_poly cpoly;
    if (!cpoly.read(argv[1])) { fprintf(stderr, "poly ilegível\n"); return 1; }
    for (int side = 0; side < cpoly.nsides(); side++) {
        cxx_mpz_poly f(cpoly[side]);
        if (f.degree() == 1) continue;
        cxx_mpz disc;
        mpz_poly_discriminant(disc, f);
        mpz_mul(disc, disc, mpz_poly_lc(f));
        auto pr = trial_division(disc, 10000000, disc);
        for (auto const & y : pr) {
            cxx_mpz const & p = y.first;
            unsigned long const pu = mpz_get_ui(p);
            // só ideais que existem: raiz de f mod p (varredura barata) ou o ponto no infinito se p | lc(f);
            // chamar get_inertia_of_prime_ideal para todo r custa O(p) chamadas caras (p chega a 1e7)
            cxx_mpz v;
            for (unsigned long r = 0; r <= pu; r++) {
                if (r < pu) {
                    cxx_mpz rr(r);
                    mpz_poly_eval_mod_mpz(v, f, rr, p);
                    if (mpz_cmp_ui(v, 0) != 0) continue;
                } else if (!mpz_divisible_p(mpz_poly_lc(f), p)) {
                    continue;
                }
                cxx_mpz rr(r);
                int in = get_inertia_of_prime_ideal(f, p, rr);
                if (in != 1) printf("%d %lu %lu %d\n", side, pu, r, in);
            }
        }
    }
    return 0;
}
