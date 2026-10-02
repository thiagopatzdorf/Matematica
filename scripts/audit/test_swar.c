/* test_swar.c -- a subtração SWAR do exactT2 (sub8 + idx18) é igual a kit_sub em Z_7^6.
 * (1) exaustivo por dígito: todos os 7x7 pares em cada uma das 6 posições, com os outros dígitos
 *     aleatórios (vale porque o argumento de "sem vai-um/empréstimo entre bytes" torna os dígitos
 *     independentes; o teste confere isso também); (2) 10^7 pares completos aleatórios;
 * (3) idx18 é injetiva em Z_7^6 (a bijeção que indexa o bitset de B). */
#include "../search/kit.h"
static inline uint64_t pk8(long x, int q){ uint64_t v = 0; for (int i = 0; i < 6; i++){ v |= (uint64_t)(x % q) << (8 * i); x /= q; } return v; }
static inline uint64_t sub8(uint64_t a, uint64_t b, uint64_t Q8, uint64_t A8, int q){
  uint64_t c = a + Q8 - b; uint64_t mge = ((c + A8) >> 7) & 0x010101010101ULL; return c - mge * (uint64_t)q; }
static inline uint32_t idx18(uint64_t c){ uint64_t t = c | (c >> 5);
  return (uint32_t)((t & 0x3F) | ((t >> 10) & 0xFC0) | ((t >> 20) & 0x3F000)); }
int main(void){
  Kit K = {0}; K.q = 7; K.n = 9; K.r = 6; kit_init_tables(&K);
  const int q = 7; const uint64_t Q8 = 0x010101010101ULL * q, A8 = 0x010101010101ULL * (128 - q);
  long bad = 0, tests = 0;
  for (int pos = 0; pos < 6; pos++) for (int da = 0; da < q; da++) for (int db = 0; db < q; db++) for (int rep = 0; rep < 200; rep++){
    long a = kit_rnd() % K.N, b = kit_rnd() % K.N;
    a = a - ((a / K.pw[pos]) % q) * K.pw[pos] + da * K.pw[pos]; b = b - ((b / K.pw[pos]) % q) * K.pw[pos] + db * K.pw[pos];
    if (sub8(pk8(a, q), pk8(b, q), Q8, A8, q) != pk8(kit_sub(&K, (int)a, (int)b), q)) bad++; tests++; }
  for (long t = 0; t < 10000000; t++){ long a = kit_rnd() % K.N, b = kit_rnd() % K.N;
    if (sub8(pk8(a, q), pk8(b, q), Q8, A8, q) != pk8(kit_sub(&K, (int)a, (int)b), q)) bad++; tests++; }
  uint8_t *seen = calloc(1 << 18, 1); long coll = 0;
  for (long x = 0; x < K.N; x++){ uint32_t i = idx18(pk8(x, q)); if (seen[i]++) coll++; }
  printf("sub8: %ld testes, %ld divergências; idx18: %ld colisões em %ld elementos\n", tests, bad, coll, K.N);
  return (bad || coll) ? 1 : 0;
}
