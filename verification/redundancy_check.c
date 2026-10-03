/* redundancy_check.c -- redundância individual: para cada c_i, C - {c_i} ainda cobre (Z/7)^9 com raio R?
 *
 * Só os pontos da bola B(c_i, R) podem perder cobertura ao remover c_i. Para cada x nessa bola
 * (enumerada recursivamente aqui: escolhe posições crescentes e valores != c_i[j]), procura OUTRA
 * palavra c_k (k != i) com d(x, c_k) <= R. Se algum x não tem, c_i é necessária; se todos têm,
 * c_i é redundante (e o programa sai com código 3, que pela regra da campanha manda PARAR).
 * Imprime, por palavra, quantos pontos só ela cobre (pontos "exclusivos").
 * Uso: redundancy_check code.txt [R=4]     Compilar: gcc -O2 -fopenmp -o redundancy_check redundancy_check.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 7
#define N 9
static int nw, R;
static unsigned char W[4096][N];

static int other_covers(const unsigned char *x, int skip){
  for (int k = 0; k < nw; k++){
    if (k == skip) continue;
    int d = 0;
    for (int j = 0; j < N && d <= R; j++) d += (x[j] != W[k][j]);
    if (d <= R) return 1;
  }
  return 0;
}
/* percorre B(c_i,R): a partir da posição pos, com wt erros ainda permitidos */
static long walk(unsigned char *x, int i, int pos, int left){
  long excl = other_covers(x, i) ? 0 : 1;
  if (!left) return excl;
  for (int p = pos; p < N; p++){
    unsigned char o = x[p];
    for (int v = 0; v < Q; v++) if (v != o){ x[p] = (unsigned char)v; excl += walk(x, i, p + 1, left - 1); }
    x[p] = o;
  }
  return excl;
}
int main(int argc, char **argv){
  if (argc < 2){ fprintf(stderr, "uso: %s code.txt [R]\n", argv[0]); return 2; }
  R = argc > 2 ? atoi(argv[2]) : 4;
  FILE *f = fopen(argv[1], "r"); char line[64];
  if (!f){ perror(argv[1]); return 2; }
  while (fgets(line, sizeof line, f)){
    if (strlen(line) != N + 1){ fprintf(stderr, "FAIL formato\n"); return 1; }
    for (int j = 0; j < N; j++){ if (line[j] < '0' || line[j] > '6'){ fprintf(stderr, "FAIL formato\n"); return 1; } W[nw][j] = (unsigned char)(line[j] - '0'); }
    nw++;
  }
  long *excl = calloc(nw, sizeof(long));
  #pragma omp parallel for schedule(dynamic, 4)
  for (int i = 0; i < nw; i++){ unsigned char x[N]; memcpy(x, W[i], N); excl[i] = walk(x, i, 0, R); }
  int red = 0; long mn = -1, sum = 0; int arg = 0;
  for (int i = 0; i < nw; i++){
    sum += excl[i];
    if (mn < 0 || excl[i] < mn){ mn = excl[i]; arg = i; }
    if (excl[i] == 0){ red++; printf("REDUNDANTE: palavra %d = ", i + 1); for (int j = 0; j < N; j++) putchar('0' + W[i][j]); putchar('\n'); }
  }
  printf("redundancy_check (C/OpenMP)\n|C| = %d\nR = %d\n", nw, R);
  printf("min_exclusive_points = %ld (palavra %d = ", mn, arg + 1);
  for (int j = 0; j < N; j++) putchar('0' + W[arg][j]);
  printf(")\ntotal_exclusive_points = %ld\nredundant_words = %d\n%s\n", sum, red,
         red ? "STOP: há palavra individualmente redundante" : "PASS: nenhuma palavra individualmente redundante");
  return red ? 3 : 0;
}
