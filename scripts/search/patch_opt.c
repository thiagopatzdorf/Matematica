/* patch_opt.c -- otimizador genérico de remendo para coberturas q-árias de raio R.
 *
 * Congela uma BASE (classes laterais de um código linear, dada em JSON, ou qualquer lista
 * de palavras) e procura o menor REMENDO que cobre o resíduo (pontos a distância > R da
 * base). O remendo mistura dois tipos de elemento:
 *   - palavra solta (custo 1);
 *   - "reta": classe lateral p + <g> de um subcódigo de dimensão 1 (custo q), com g numa
 *     das DIREÇÕES dadas (palavras do código da base, para a reta caber numa classe órfã).
 * Medido em K_7(9,4): retas rendem mais que palavras soltas ou planos.
 *
 * LISTAS INVERTIDAS: cada candidato guarda só os pontos do resíduo dentro da sua bola
 * (e cada ponto, os candidatos que o cobrem). Um movimento custa |lista|, não q^n — é o
 * que torna a busca ~1000x mais barata que reavaliar a cobertura inteira.
 *
 * BUSCA: recozimento simulado com reaquecimento. Composição fixa (L retas + W palavras);
 * movimento = escolher um ponto descoberto p, um candidato que cobre p (entra) e o de
 * menor perda entre alguns sorteados do mesmo tipo (sai). Quando zera o resíduo, grava a
 * solução e encolhe: W-1 (ou, com W=0, L-1 e W+q-1, completando gulosamente).
 *
 * USO
 *   patch_opt base.json [opções]
 *   base.json: {"q":7,"n":9,"R":4,"A":"652 132 ...","coset_syndromes":[0,98305,38951]}
 *     (aceita também "s1","s2" no lugar de coset_syndromes, como os p*.json da frente 2b).
 *     Com "frozen":"arquivo.txt" a base passa a ser essa lista de palavras.
 *   --dirs g1,g2,...     direções das retas (palavras do código); padrão: auto
 *   --ndirs D            no modo auto, quantas direções usar (padrão 1)
 *   --L n --W n          composição inicial (padrão: 36 retas, 8 palavras)
 *   --tauw x --taul y    corte de candidatos: palavras com >= x pontos; retas com cota >= y
 *   --init f.json        solução inicial no formato p*.json (gens/reps/words ou lines)
 *   --secs s --seed s --T0 t --T1 t --cyc n
 *   --out prefixo        grava prefixo_M<M>.txt e .json a cada recorde
 *
 * Compilar: gcc -O3 -march=native -o patch_opt patch_opt.c -lm
 * TODA solução deve passar por verificador independente (verify.py) antes de declarada.
 */
#include "kit.h"
#include <math.h>
#include <ctype.h>

typedef uint32_t W32;
static int q, n, R, t_cos;
static long NW;                 /* q^n */
static long pwn[20];
static int cd, nch; static long CH; static int *add3; /* soma por blocos de cd dígitos */

static inline W32 wadd(W32 a, W32 b){
  W32 r = 0; long p = 1;
  for (int i = 0; i < nch; i++){ r += (W32)(add3[(a % CH) * CH + (b % CH)] * p); a /= CH; b /= CH; p *= CH; }
  return r;
}
static W32 wscale(W32 a, int c){ W32 r = 0; for (int i = 0; i < n; i++){ r += (W32)((((a / pwn[i]) % q) * c) % q * pwn[i]); } return r; }
static W32 parse_word(const char *s){ W32 w = 0; for (int i = 0; i < n; i++) w += (W32)((s[i] - '0') * pwn[i]); return w; }
static void word_str(W32 w, char *s){ for (int i = 0; i < n; i++){ s[i] = '0' + (w % q); w /= q; } s[n] = 0; }

/* ---------- JSON mínimo ---------- */
static char *slurp(const char *f){ FILE *F = fopen(f, "r"); if (!F){ perror(f); exit(2); } fseek(F, 0, SEEK_END); long L = ftell(F); rewind(F); char *b = malloc(L + 1); if (fread(b, 1, L, F) != (size_t)L) exit(2); b[L] = 0; fclose(F); return b; }
static const char *jkey(const char *js, const char *k){ char pat[64]; snprintf(pat, sizeof pat, "\"%s\"", k); const char *p = strstr(js, pat); if (!p) return NULL; p += strlen(pat); while (*p && (*p == ' ' || *p == ':')) p++; return p; }
static long jint(const char *js, const char *k, long dflt){ const char *p = jkey(js, k); return p ? atol(p) : dflt; }
static int jstr(const char *js, const char *k, char *out, int max){ const char *p = jkey(js, k); if (!p || *p != '"') return 0; p++; int i = 0; while (*p && *p != '"' && i < max - 1) out[i++] = *p++; out[i] = 0; return 1; }
/* lista de strings ou números: devolve contagem; strs recebe cópias */
static int jlist(const char *js, const char *k, char out[][32], int max){
  const char *p = jkey(js, k); if (!p || *p != '[') return -1; p++; int c = 0;
  while (*p && *p != ']'){
    while (*p == ' ' || *p == ',' || *p == '\n') p++;
    if (*p == ']') break;
    if (*p == '"'){ p++; int i = 0; while (*p != '"' && i < 31) out[c][i++] = *p++; out[c][i] = 0; p++; }
    else if (*p == '['){ /* par [g,rep] */ p++; int i = 0; while (*p != ']' && i < 31){ if (*p != '"' && *p != ' ') out[c][i++] = *p; p++; } out[c][i] = 0; p++; }
    else { int i = 0; while ((isdigit((unsigned char)*p) || *p == '-') && i < 31) out[c][i++] = *p++; out[c][i] = 0; }
    if (++c >= max) break;
  }
  return c;
}

/* ---------- estado ---------- */
static uint8_t *frozen_cov;     /* 1 se coberto pela base */
static int32_t *pidx;           /* palavra -> índice no resíduo, ou -1 */
static W32 *resid; static long nres;
static uint16_t *cntw;          /* nº de pontos do resíduo na bola de cada palavra */
static int ndir; static W32 dirs[64];
static int32_t *lineid[64];     /* palavra -> candidato-reta (por direção) ou -1 */
static int32_t *wcand;          /* palavra -> candidato-palavra ou -1 */
static long ncand, capcand;
static uint8_t *ctype; static W32 *cword; static uint8_t *cdir; /* reta: rep = menor palavra */
static long *coff; static int32_t *clist; /* CSR candidato -> pontos */
static long *poff; static int32_t *plist; /* CSR ponto -> candidatos */

static long new_cand(int type, W32 w, int d){
  if (ncand == capcand){ capcand = capcand ? 2 * capcand : 1 << 16; ctype = realloc(ctype, capcand); cword = realloc(cword, capcand * sizeof(W32)); cdir = realloc(cdir, capcand); }
  ctype[ncand] = type; cword[ncand] = w; cdir[ncand] = d; return ncand++;
}

/* DFS na bola */
static int digs[20];
typedef void (*visit_fn)(W32 w, void *ctx);
static void ball_rec(int start, int left, W32 cur, visit_fn f, void *ctx){
  f(cur, ctx);
  if (!left) return;
  for (int j = start; j < n; j++){ int d = digs[j];
    for (int e = 1; e < q; e++){ int nd = (d + e) % q; ball_rec(j + 1, left - 1, (W32)((long)cur + (nd - d) * pwn[j]), f, ctx); } }
}
static void ball(W32 w, visit_fn f, void *ctx){ W32 x = w; for (int i = 0; i < n; i++){ digs[i] = x % q; x /= q; } ball_rec(0, R, w, f, ctx); }

static void v_mark(W32 w, void *c){ (void)c; frozen_cov[w] = 1; }
static void v_cnt(W32 w, void *c){ (void)c; if (cntw[w] < 65535) cntw[w]++; }
/* passada de listas: fase 0 conta, fase 1 preenche */
static int fill_phase; static int32_t cur_p;
static long *cfill;
static uint64_t *cbit;
static void v_list(W32 w, void *c){ (void)c;
  if (!((cbit[w >> 6] >> (w & 63)) & 1)) return;
  int32_t cw = wcand[w];
  if (cw >= 0){ if (fill_phase) clist[cfill[cw]++] = cur_p; else coff[cw + 1]++; }
  for (int d = 0; d < ndir; d++){ int32_t cl = lineid[d][w]; if (cl < 0) continue;
    if (fill_phase){ long pos = cfill[cl]; if (pos > coff[cl] && clist[pos - 1] == cur_p) continue; clist[cfill[cl]++] = cur_p; }
    else { /* conta com repetição (cota superior), corrigida na fase de preenchimento */ coff[cl + 1]++; } }
}

/* ---------- SA ---------- */
static uint16_t *cov; static int32_t *unc, *upos; static long nunc;
static uint8_t *sel; static int32_t *sl[2], *spos; static int nsel[2];
static inline void unc_add(int32_t p){ upos[p] = (int32_t)nunc; unc[nunc++] = p; }
static inline void unc_del(int32_t p){ int32_t i = upos[p]; int32_t last = unc[--nunc]; unc[i] = last; upos[last] = i; upos[p] = -1; }
static void add_c(long c){ sel[c] = 1; int ty = ctype[c]; spos[c] = nsel[ty]; sl[ty][nsel[ty]++] = (int32_t)c;
  for (long i = coff[c]; i < coff[c + 1]; i++){ int32_t p = clist[i]; if (cov[p]++ == 0) unc_del(p); } }
static void rem_c(long c){ sel[c] = 0; int ty = ctype[c]; int32_t i = spos[c]; int32_t last = sl[ty][--nsel[ty]]; sl[ty][i] = last; spos[last] = i;
  for (long k = coff[c]; k < coff[c + 1]; k++){ int32_t p = clist[k]; if (--cov[p] == 0) unc_add(p); } }
static int loss_c(long c){ int l = 0; for (long i = coff[c]; i < coff[c + 1]; i++) if (cov[clist[i]] == 1) l++; return l; }
static int gain_c(long c){ int g = 0; for (long i = coff[c]; i < coff[c + 1]; i++) if (cov[clist[i]] == 0) g++; return g; }

static const char *outp = "patch"; static char baseA[256]; static int csyn[16]; static int frozen_mode; static char frozen_file[512];
static int M_base;
static W32 *basew; static long nbasew;

static void save(void){
  int M = (int)nbasew + q * nsel[1] + nsel[0];
  char fn[600]; snprintf(fn, sizeof fn, "%s_M%d.txt", outp, M);
  FILE *F = fopen(fn, "w"); char s[32];
  for (long i = 0; i < nbasew; i++){ word_str(basew[i], s); fprintf(F, "%s\n", s); }
  for (int i = 0; i < nsel[1]; i++){ long c = sl[1][i]; W32 w = cword[c];
    for (int k = 0; k < q; k++){ word_str(w, s); fprintf(F, "%s\n", s); w = wadd(w, dirs[cdir[c]]); } }
  for (int i = 0; i < nsel[0]; i++){ word_str(cword[sl[0][i]], s); fprintf(F, "%s\n", s); }
  fclose(F);
  snprintf(fn, sizeof fn, "%s_M%d.json", outp, M);
  F = fopen(fn, "w");
  fprintf(F, "{\"q\":%d,\"n\":%d,\"R\":%d,\"M\":%d", q, n, R, M);
  if (!frozen_mode){ fprintf(F, ",\"A\":\"%s\",\"coset_syndromes\":[", baseA); for (int j = 0; j < t_cos; j++) fprintf(F, "%s%d", j ? "," : "", csyn[j]); fprintf(F, "]"); if (t_cos == 3) fprintf(F, ",\"s1\":%d,\"s2\":%d", csyn[1], csyn[2]); }
  else fprintf(F, ",\"frozen\":\"%s\"", frozen_file);
  fprintf(F, ",\"dirs\":["); for (int d = 0; d < ndir; d++){ word_str(dirs[d], s); fprintf(F, "%s\"%s\"", d ? "," : "", s); } fprintf(F, "]");
  if (ndir == 1){ word_str(dirs[0], s); fprintf(F, ",\"gens\":\"%s\"", s); }
  fprintf(F, ",\"lines\":["); for (int i = 0; i < nsel[1]; i++){ char g[32]; word_str(dirs[cdir[sl[1][i]]], g); word_str(cword[sl[1][i]], s); fprintf(F, "%s[\"%s\",\"%s\"]", i ? "," : "", g, s); } fprintf(F, "]");
  fprintf(F, ",\"reps\":["); for (int i = 0; i < nsel[1]; i++){ word_str(cword[sl[1][i]], s); fprintf(F, "%s\"%s\"", i ? "," : "", s); } fprintf(F, "]");
  fprintf(F, ",\"words\":["); for (int i = 0; i < nsel[0]; i++){ word_str(cword[sl[0][i]], s); fprintf(F, "%s\"%s\"", i ? "," : "", s); } fprintf(F, "]}\n");
  fclose(F);
  printf("SOLVED M=%d (base %ld + %d retas x %d + %d palavras) -> %s_M%d.txt\n", M, nbasew, nsel[1], q, nsel[0], outp, M); fflush(stdout);
}

static W32 line_rep(W32 w, int d){ W32 best = w, x = w; for (int k = 1; k < q; k++){ x = wadd(x, dirs[d]); if (x < best) best = x; } return best; }

int main(int argc, char **argv){
  if (argc < 2){ fprintf(stderr, "uso: patch_opt base.json [opções] (ver cabeçalho)\n"); return 2; }
  char *js = slurp(argv[1]);
  q = (int)jint(js, "q", 7); n = (int)jint(js, "n", 9); R = (int)jint(js, "R", 4);
  int L = 36, Wn = 8, tauw = 0, taul = 0, ndirs_auto = 1; double secs = 600, T0 = 1.2, T1 = 0.3; long cyc = 2000000; unsigned long long seed = 1;
  char dirarg[1024] = "", initf[512] = "";
  for (int i = 2; i < argc; i++){
    if (!strcmp(argv[i], "--dirs")) snprintf(dirarg, sizeof dirarg, "%s", argv[++i]);
    else if (!strcmp(argv[i], "--ndirs")) ndirs_auto = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--L")) L = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--W")) Wn = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--tauw")) tauw = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--taul")) taul = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--init")) snprintf(initf, sizeof initf, "%s", argv[++i]);
    else if (!strcmp(argv[i], "--secs")) secs = atof(argv[++i]);
    else if (!strcmp(argv[i], "--seed")) seed = strtoull(argv[++i], 0, 10);
    else if (!strcmp(argv[i], "--T0")) T0 = atof(argv[++i]);
    else if (!strcmp(argv[i], "--T1")) T1 = atof(argv[++i]);
    else if (!strcmp(argv[i], "--cyc")) cyc = atol(argv[++i]);
    else if (!strcmp(argv[i], "--out")) outp = argv[++i];
    else { fprintf(stderr, "opção desconhecida %s\n", argv[i]); return 2; }
  }
  kit_seed(seed);
  pwn[0] = 1; for (int i = 1; i < 20; i++) pwn[i] = pwn[i - 1] * q;
  NW = pwn[n];
  cd = 1; while (pwn[cd + 1] <= 2401 && cd + 1 <= n) cd++;
  CH = pwn[cd]; nch = (n + cd - 1) / cd;
  add3 = kit_mk_add(q, cd, CH);
  double t0 = kit_now();

  /* ---- base ---- */
  Kit K = {0}; K.q = q; K.n = n; K.R = R;
  if (jstr(js, "frozen", frozen_file, sizeof frozen_file)){
    frozen_mode = 1; FILE *F = fopen(frozen_file, "r"); if (!F){ perror(frozen_file); return 2; }
    char line[64]; basew = malloc(sizeof(W32) * 4000000); nbasew = 0;
    while (fgets(line, sizeof line, F)) if ((int)strlen(line) >= n && isdigit((unsigned char)line[0])) basew[nbasew++] = parse_word(line);
    fclose(F);
  } else {
    if (!jstr(js, "A", baseA, sizeof baseA)){ fprintf(stderr, "base sem A\n"); return 2; }
    int rows = 1; for (char *p = baseA; *p; p++) if (*p == ' ') rows++;
    K.r = rows; K.k = n - rows;
    kit_init_tables(&K); kit_set_A(&K, baseA);
    char tmp[16][32]; int c = jlist(js, "coset_syndromes", tmp, 16);
    if (c > 0){ t_cos = c; for (int j = 0; j < c; j++) csyn[j] = atoi(tmp[j]); }
    else { t_cos = 3; csyn[0] = 0; csyn[1] = (int)jint(js, "s1", 0); csyn[2] = (int)jint(js, "s2", 0); }
    /* palavras do código: c = (-A u, u) */
    long nc = pwn[K.k]; W32 *code = malloc(sizeof(W32) * nc);
    for (long u = 0; u < nc; u++){ int uv[16]; long x = u; for (int j = 0; j < K.k; j++){ uv[j] = x % q; x /= q; }
      W32 w = 0; for (int i = 0; i < K.r; i++){ int s = 0; for (int j = 0; j < K.k; j++) s += K.H[i][K.r + j] * uv[j]; w += (W32)(((q - s % q) % q) * pwn[i]); }
      for (int j = 0; j < K.k; j++) w += (W32)(uv[j] * pwn[K.r + j]);
      code[u] = w; }
    basew = malloc(sizeof(W32) * nc * t_cos); nbasew = 0;
    for (int j = 0; j < t_cos; j++){ W32 rep = 0; long s = csyn[j]; for (int i = 0; i < K.r; i++){ rep += (W32)((s % q) * pwn[i]); s /= q; }
      for (long u = 0; u < nc; u++) basew[nbasew++] = wadd(rep, code[u]); }
    /* direções automáticas: todas as palavras não nulas do código, uma por classe escalar */
    if (!dirarg[0]){
      ndir = 0;
      for (long u = 1; u < nc && ndir < 64; u++){ W32 w = code[u]; int canon = 1; for (int c2 = 2; c2 < q; c2++) if (wscale(w, c2) < w) canon = 0; if (canon) dirs[ndir++] = w; }
    }
  }
  if (dirarg[0]){ ndir = 0; char *p = dirarg; while (*p){ dirs[ndir++] = parse_word(p); p += n; if (*p == ',') p++; } }
  M_base = (int)nbasew;

  /* ---- resíduo ---- */
  frozen_cov = calloc(NW, 1);
  for (long i = 0; i < nbasew; i++) ball(basew[i], v_mark, NULL);
  pidx = malloc(sizeof(int32_t) * NW); nres = 0;
  for (long w = 0; w < NW; w++) if (!frozen_cov[w]) nres++;
  resid = malloc(sizeof(W32) * (nres + 1)); nres = 0;
  for (long w = 0; w < NW; w++){ if (!frozen_cov[w]){ pidx[w] = (int32_t)nres; resid[nres++] = (W32)w; } else pidx[w] = -1; }
  free(frozen_cov);
  printf("base: %ld palavras; resíduo: %ld pontos (%.1fs)\n", nbasew, nres, kit_now() - t0); fflush(stdout);
  cntw = calloc(NW, sizeof(uint16_t));
  for (long i = 0; i < nres; i++) ball(resid[i], v_cnt, NULL);
  int mx = 0; long hist[64] = {0}; for (long w = 0; w < NW; w++){ if (cntw[w] > mx) mx = cntw[w]; hist[cntw[w] < 63 ? cntw[w] : 63]++; }
  printf("cobertura máx de uma palavra: %d (%.1fs)\n", mx, kit_now() - t0);
  if (!tauw){ long acc = 0; tauw = mx; while (tauw > 1 && acc + hist[tauw - 1 < 63 ? tauw - 1 : 63] < 400000){ tauw--; acc += hist[tauw < 63 ? tauw : 63]; } }

  /* ---- retas: cota = soma de cnt nas q palavras; escolhe direções no modo auto ---- */
  uint8_t *vis = malloc(NW);
  long *dscore = calloc(ndir, sizeof(long)); int *dmax = calloc(ndir, sizeof(int));
  int keepdirs = (dirarg[0] || frozen_mode) ? ndir : ndirs_auto;
  if (ndir > keepdirs){
    for (int d = 0; d < ndir; d++){
      memset(vis, 0, NW); int top[64] = {0};
      for (long w = 0; w < NW; w++){ if (vis[w]) continue; W32 x = (W32)w; int s = 0; for (int k = 0; k < q; k++){ vis[x] = 1; s += cntw[x]; x = wadd(x, dirs[d]); }
        if (s > top[63]){ int i = 63; while (i > 0 && top[i - 1] < s){ top[i] = top[i - 1]; i--; } top[i] = s; } }
      for (int i = 0; i < 64; i++) dscore[d] += top[i]; dmax[d] = top[0];
    }
    for (int a = 0; a < keepdirs; a++){ int b = a; for (int d = a + 1; d < ndir; d++) if (dscore[d] > dscore[b]) b = d;
      W32 tw = dirs[a]; dirs[a] = dirs[b]; dirs[b] = tw; long ts = dscore[a]; dscore[a] = dscore[b]; dscore[b] = ts; int tm = dmax[a]; dmax[a] = dmax[b]; dmax[b] = tm; }
    ndir = keepdirs;
    for (int d = 0; d < ndir; d++){ char s[32]; word_str(dirs[d], s); printf("direção %s: cota máx %d, soma top64 %ld\n", s, dmax[d], dscore[d]); }
  }
  /* candidatos */
  wcand = malloc(sizeof(int32_t) * NW);
  for (long w = 0; w < NW; w++) wcand[w] = (cntw[w] >= tauw) ? (int32_t)new_cand(0, (W32)w, 0) : -1;
  long nwc = ncand;
  if (!taul){ /* corte das retas: as ~300k de maior cota */
    long lh[65536 / 8] = {0};
    for (int d = 0; d < ndir; d++){ memset(vis, 0, NW);
      for (long w = 0; w < NW; w++){ if (vis[w]) continue; W32 x = (W32)w; int s = 0; for (int k = 0; k < q; k++){ vis[x] = 1; s += cntw[x]; x = wadd(x, dirs[d]); } lh[s < 8191 ? s : 8191]++; } }
    long acc = 0; taul = 8191; while (taul > 1 && acc + lh[taul - 1] < 300000L * 1){ taul--; acc += lh[taul]; }
  }
  for (int d = 0; d < ndir; d++){
    lineid[d] = malloc(sizeof(int32_t) * NW); for (long w = 0; w < NW; w++) lineid[d][w] = -1;
    memset(vis, 0, NW);
    for (long w = 0; w < NW; w++){ if (vis[w]) continue; W32 x = (W32)w; int s = 0; for (int k = 0; k < q; k++){ vis[x] = 1; s += cntw[x]; x = wadd(x, dirs[d]); }
      if (s >= taul){ long c = new_cand(1, (W32)w, d); x = (W32)w; for (int k = 0; k < q; k++){ lineid[d][x] = (int32_t)c; x = wadd(x, dirs[d]); } } }
  }
  /* solução inicial: força seus elementos como candidatos */
  long *initc = malloc(sizeof(long) * 100000); int ninit = 0;
  if (initf[0]){
    char *ij = slurp(initf); static char tmp[20000][32];
    char g[32] = ""; jstr(ij, "gens", g, sizeof g);
    int c = jlist(ij, "lines", tmp, 20000);
    if (c <= 0 && g[0]){ int cr = jlist(ij, "reps", tmp, 20000); for (int i = 0; i < cr; i++){ char t2[64]; snprintf(t2, sizeof t2, "%s,%s", g, tmp[i]); strcpy(tmp[i], t2); } c = cr; }
    for (int i = 0; i < c; i++){ char *cm = strchr(tmp[i], ','); if (!cm) continue; W32 gw = parse_word(tmp[i]), rw = parse_word(cm + 1);
      int d = -1; for (int e = 0; e < ndir; e++){ for (int s2 = 1; s2 < q; s2++) if (wscale(dirs[e], s2) == gw) d = e; }
      if (d < 0){ if (strchr(g, ',')){ fprintf(stderr, "init: reta com subcódigo de dim>1 não suportada\n"); return 2; } dirs[ndir] = gw; lineid[ndir] = malloc(sizeof(int32_t) * NW); for (long w = 0; w < NW; w++) lineid[ndir][w] = -1; d = ndir++; }
      W32 x = rw; if (lineid[d][x] < 0){ long cc = new_cand(1, line_rep(rw, d), d); for (int k = 0; k < q; k++){ lineid[d][x] = (int32_t)cc; x = wadd(x, dirs[d]); } }
      initc[ninit++] = lineid[d][rw]; }
    int cw = jlist(ij, "words", tmp, 20000);
    for (int i = 0; i < cw; i++){ W32 w = parse_word(tmp[i]); if (wcand[w] < 0) wcand[w] = (int32_t)new_cand(0, w, 0); initc[ninit++] = wcand[w]; }
    free(ij);
  }
  free(vis);
  printf("candidatos: %ld palavras (tauw=%d), %ld retas (taul=%d) em %d direções (%.1fs)\n", nwc, tauw, ncand - nwc, taul, ndir, kit_now() - t0); fflush(stdout);

  /* ---- listas invertidas ---- */
  cbit = calloc(NW / 64 + 1, 8);
  for (long w = 0; w < NW; w++){ int any = wcand[w] >= 0; for (int d = 0; d < ndir && !any; d++) any = lineid[d][w] >= 0; if (any) cbit[w >> 6] |= 1ULL << (w & 63); }
  coff = calloc(ncand + 1, sizeof(long));
  fill_phase = 0; for (long i = 0; i < nres; i++){ cur_p = (int32_t)i; ball(resid[i], v_list, NULL); }
  for (long c = 0; c < ncand; c++) coff[c + 1] += coff[c];
  clist = malloc(sizeof(int32_t) * (coff[ncand] + 1)); cfill = malloc(sizeof(long) * (ncand + 1));
  for (long c = 0; c < ncand; c++) cfill[c] = coff[c];
  fill_phase = 1; for (long i = 0; i < nres; i++){ cur_p = (int32_t)i; ball(resid[i], v_list, NULL); }
  /* compacta (retas tinham contagem com repetição) */
  long wp = 0; for (long c = 0; c < ncand; c++){ long s = coff[c], e = cfill[c]; coff[c] = wp; for (long i = s; i < e; i++) clist[wp++] = clist[i]; } coff[ncand] = wp;
  poff = calloc(nres + 1, sizeof(long));
  for (long i = 0; i < wp; i++) poff[clist[i] + 1]++;
  for (long p = 0; p < nres; p++) poff[p + 1] += poff[p];
  plist = malloc(sizeof(int32_t) * (wp + 1)); long *pf = malloc(sizeof(long) * (nres + 1)); memcpy(pf, poff, sizeof(long) * (nres + 1));
  for (long c = 0; c < ncand; c++) for (long i = coff[c]; i < coff[c + 1]; i++) plist[pf[clist[i]]++] = (int32_t)c;
  free(pf); free(cfill); free(cntw);
  printf("listas: %ld entradas (%.1fs)\n", wp, kit_now() - t0); fflush(stdout);
  for (long p = 0; p < nres; p++) if (poff[p + 1] == poff[p]){ char s[32]; word_str(resid[p], s); fprintf(stderr, "ponto %s sem candidato: baixe tauw/taul\n", s); return 3; }

  /* ---- SA ---- */
  cov = calloc(nres, sizeof(uint16_t)); unc = malloc(sizeof(int32_t) * nres); upos = malloc(sizeof(int32_t) * nres);
  nunc = 0; for (long p = 0; p < nres; p++) unc_add((int32_t)p);
  sel = calloc(ncand, 1); spos = malloc(sizeof(int32_t) * ncand); sl[0] = malloc(sizeof(int32_t) * (ncand + 1)); sl[1] = malloc(sizeof(int32_t) * (ncand + 1));
  int tgt[2]; tgt[0] = Wn; tgt[1] = L;
  if (ninit){ tgt[0] = tgt[1] = 0; for (int i = 0; i < ninit; i++) if (!sel[initc[i]]){ add_c(initc[i]); tgt[ctype[initc[i]]]++; } printf("init: %d retas + %d palavras, descobertos %ld\n", tgt[1], tgt[0], nunc); }
  /* completa gulosamente */
  for (int ty = 1; ty >= 0; ty--) while (nsel[ty] < tgt[ty]){
    long best = -1; int bg = -1;
    if (nunc){ for (int s2 = 0; s2 < 64; s2++){ int32_t p = unc[kit_rnd() % nunc]; for (long i = poff[p]; i < poff[p + 1]; i++){ long c = plist[i]; if (ctype[c] != ty || sel[c]) continue; int g = gain_c(c); if (g > bg){ bg = g; best = c; } } } }
    if (best < 0){ do best = kit_rnd() % ncand; while (ctype[best] != ty || sel[best]); }
    add_c(best);
  }
  printf("inicial: %d retas + %d palavras, descobertos %ld\n", nsel[1], nsel[0], nunc); fflush(stdout);
  long it = 0; long bestU = nunc; double tl = t0 + secs;
  if (!nunc) save();
  while (kit_now() < tl){
    if (!nunc){
      /* encolhe */
      int ty = nsel[0] > 0 ? 0 : 1;
      if (nsel[ty] == 0) break;
      long worst = -1; int wl = 1 << 30; for (int i = 0; i < nsel[ty]; i++){ long c = sl[ty][i]; int l = loss_c(c); if (l < wl){ wl = l; worst = c; } }
      rem_c(worst);
      if (ty == 1){ for (int k = 0; k < q - 1 && nunc; k++){ long best = -1; int bg = -1; for (long ui = 0; ui < nunc; ui++){ int32_t p = unc[ui]; for (long i = poff[p]; i < poff[p + 1]; i++){ long c = plist[i]; if (ctype[c] || sel[c]) continue; int g = gain_c(c); if (g > bg){ bg = g; best = c; } } } if (best >= 0) add_c(best); }
        while (nsel[0] < q - 1){ long c; do c = kit_rnd() % ncand; while (ctype[c] || sel[c]); add_c(c); } }
      bestU = nunc;
      printf("encolheu para %d retas + %d palavras (M=%ld), descobertos %ld (%.0fs)\n", nsel[1], nsel[0], nbasew + q * nsel[1] + nsel[0], nunc, kit_now() - t0); fflush(stdout);
      if (!nunc){ save(); }
      continue;
    }
    double T = T0 - (T0 - T1) * (double)(it % cyc) / cyc;
    for (int rep = 0; rep < 4096 && nunc; rep++, it++){
      int32_t p = unc[kit_rnd() % nunc];
      long deg = poff[p + 1] - poff[p];
      long c = plist[poff[p] + kit_rnd() % deg];
      if (sel[c]) continue;
      int ty = ctype[c]; if (nsel[ty] == 0) continue;
      long r = -1; int rl = 1 << 30;
      for (int s2 = 0; s2 < 3; s2++){ long x = sl[ty][kit_rnd() % nsel[ty]]; int l = loss_c(x); if (l < rl){ rl = l; r = x; } }
      long U0 = nunc;
      add_c(c); rem_c(r);
      long dU = (long)nunc - U0;
      if (dU <= 0 || (double)(kit_rnd() >> 11) * (1.0 / 9007199254740992.0) < exp(-dU / T)){
        if ((long)nunc < bestU){ bestU = nunc; if (bestU <= 3 || it % 1 == 0) { /* progress */ } }
      } else { add_c(r); rem_c(c); }
      if (!nunc){ save(); break; }
    }
    if ((it & ((1 << 22) - 1)) < 4096){ printf("it=%ld T=%.2f descobertos=%ld melhor=%ld (%.0fs)\n", it, T, nunc, bestU, kit_now() - t0); fflush(stdout); }
  }
  printf("fim: it=%ld, melhor descobertos=%ld com %d retas + %d palavras\n", it, bestU, nsel[1], nsel[0]);
  return 0;
}
