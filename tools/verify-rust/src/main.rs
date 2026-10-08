//! verify-rust: verificador independente de codigos de cobertura.
//!
//! Algoritmo: dilatacao por camadas. S0 = codigo; S_{k+1} = D(S_k), onde
//! D(S) = uniao, sobre posicoes p, de L_p(S) e L_p(S) = {x : alguma palavra de
//! S coincide com x fora da posicao p}. Apos R passos, S_R = bola de raio R do
//! codigo. Custo: R * n * q^n operacoes de byte, memoria 2 * q^n bytes.
//! Nao varre palavra-do-espaco x palavra-do-codigo.

use std::process::exit;

const EXIT_OK: i32 = 0;
const EXIT_UNCOVERED: i32 = 1;
const EXIT_CONTRADICTS: i32 = 2;
const EXIT_USAGE: i32 = 3;
const MAX_POINTS: u64 = 1 << 33; // 8 GiB por camada: acima disso, recusa.

fn usage(msg: &str) -> ! {
    eprintln!("erro de uso: {msg}");
    eprintln!("uso: verify-rust --q Q --n N --R R --M M <arquivo>");
    exit(EXIT_USAGE);
}

struct Params {
    q: u64,
    n: usize,
    r: usize,
    m: usize,
    file: String,
}

fn parse_args() -> Params {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let (mut q, mut n, mut r, mut m): (Option<u64>, Option<u64>, Option<u64>, Option<u64>) =
        (None, None, None, None);
    let mut file: Option<String> = None;
    let mut i = 0;
    while i < args.len() {
        let a = args[i].as_str();
        match a {
            "--q" | "--n" | "--R" | "--M" => {
                i += 1;
                let v = args.get(i).unwrap_or_else(|| usage(&format!("{a} sem valor")));
                let v: u64 = v
                    .parse()
                    .unwrap_or_else(|_| usage(&format!("{a}: valor nao inteiro: {v}")));
                let slot = match a {
                    "--q" => &mut q,
                    "--n" => &mut n,
                    "--R" => &mut r,
                    _ => &mut m,
                };
                if slot.is_some() {
                    usage(&format!("{a} repetido"));
                }
                *slot = Some(v);
            }
            _ if a.starts_with("--") => usage(&format!("opcao desconhecida {a}")),
            _ => {
                if file.is_some() {
                    usage("mais de um arquivo");
                }
                file = Some(a.to_string());
            }
        }
        i += 1;
    }
    let q = q.unwrap_or_else(|| usage("--q obrigatorio"));
    let n = n.unwrap_or_else(|| usage("--n obrigatorio"));
    let r = r.unwrap_or_else(|| usage("--R obrigatorio"));
    let m = m.unwrap_or_else(|| usage("--M obrigatorio"));
    let file = file.unwrap_or_else(|| usage("arquivo obrigatorio"));
    if !(2..=10).contains(&q) {
        usage("q deve estar em 2..10");
    }
    if n < 1 || n > 40 {
        usage("n deve estar em 1..40");
    }
    if m < 1 {
        usage("M deve ser >= 1");
    }
    if r > n {
        usage("R deve ser <= n");
    }
    let mut pts: u64 = 1;
    for _ in 0..n {
        pts = pts.saturating_mul(q);
        if pts > MAX_POINTS {
            usage("q^n grande demais para esta ferramenta");
        }
    }
    Params { q, n: n as usize, r: r as usize, m: m as usize, file }
}

/// Le o arquivo e devolve os indices (w = sum s[k] q^k) ou o motivo da contradicao.
fn load(p: &Params) -> Result<Vec<u64>, String> {
    let data = std::fs::read(&p.file).unwrap_or_else(|e| usage(&format!("{}: {e}", p.file)));
    let mut body: &[u8] = &data;
    if body.last() == Some(&b'\n') {
        body = &body[..body.len() - 1];
    }
    let mut words: Vec<u64> = Vec::new();
    if !data.is_empty() {
        for (ln, raw) in body.split(|&b| b == b'\n').enumerate() {
            let line = if raw.last() == Some(&b'\r') { &raw[..raw.len() - 1] } else { raw };
            if line.len() != p.n {
                return Err(format!("linha {}: comprimento {} != n={}", ln + 1, line.len(), p.n));
            }
            let mut w: u64 = 0;
            let mut pw: u64 = 1;
            for &c in line {
                if !c.is_ascii_digit() || (c - b'0') as u64 >= p.q {
                    return Err(format!("linha {}: digito invalido (>= q ou nao decimal)", ln + 1));
                }
                w += (c - b'0') as u64 * pw;
                pw *= p.q;
            }
            words.push(w);
        }
    }
    let total = words.len();
    words.sort_unstable();
    for i in 1..words.len() {
        if words[i] == words[i - 1] {
            return Err(format!("palavra duplicada: {}", fmt_word(words[i], p.q, p.n)));
        }
    }
    if total != p.m {
        return Err(format!("{total} palavras distintas != M={}", p.m));
    }
    Ok(words)
}

fn fmt_word(mut w: u64, q: u64, n: usize) -> String {
    let mut s = String::with_capacity(n);
    for _ in 0..n {
        s.push((b'0' + (w % q) as u8) as char);
        w /= q;
    }
    s
}

/// dst[x] = OR sobre a reta de x na posicao p (stride = q^p) de src.
fn line_or(src: &[u8], dst: &mut [u8], q: usize, stride: usize) {
    let block = stride * q;
    for (sb, db) in src.chunks_exact(block).zip(dst.chunks_exact_mut(block)) {
        // acumula em db[0..stride] o OR dos q segmentos, depois replica.
        let (first, rest) = db.split_at_mut(stride);
        first.copy_from_slice(&sb[..stride]);
        for v in 1..q {
            let seg = &sb[v * stride..(v + 1) * stride];
            for (a, b) in first.iter_mut().zip(seg) {
                *a |= *b;
            }
        }
        for v in 0..q - 1 {
            rest[v * stride..(v + 1) * stride].copy_from_slice(first);
        }
    }
}

/// next = D(cur): uniao dos line_or por posicao.
fn dilate(cur: &[u8], next: &mut [u8], tmp: &mut [u8], q: usize, n: usize) {
    next.fill(0);
    let mut stride = 1usize;
    for _ in 0..n {
        line_or(cur, tmp, q, stride);
        for (a, b) in next.iter_mut().zip(tmp.iter()) {
            *a |= *b;
        }
        stride *= q;
    }
}

fn main() {
    let p = parse_args();
    let words = match load(&p) {
        Ok(w) => w,
        Err(e) => {
            eprintln!("CONTRADIZ PARAMETROS: {e}");
            exit(EXIT_CONTRADICTS);
        }
    };
    let total = (p.q as usize).pow(p.n as u32);
    let mut cur = vec![0u8; total];
    for &w in &words {
        cur[w as usize] = 1;
    }
    drop(words);
    let mut next = vec![0u8; total];
    let mut tmp = vec![0u8; total];
    for _ in 0..p.r {
        dilate(&cur, &mut next, &mut tmp, p.q as usize, p.n);
        std::mem::swap(&mut cur, &mut next);
    }
    let uncovered = cur.iter().filter(|&&b| b == 0).count();
    if uncovered > 0 {
        let first = cur.iter().position(|&b| b == 0).unwrap();
        println!(
            "UNCOVERED q={} n={} R={} M={} points={} uncovered={} first_uncovered={}",
            p.q, p.n, p.r, p.m, total, uncovered, fmt_word(first as u64, p.q, p.n)
        );
        exit(EXIT_UNCOVERED);
    }
    println!("COVERS q={} n={} R={} M={} points={} uncovered=0", p.q, p.n, p.r, p.m, total);
    exit(EXIT_OK);
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cover_count(q: usize, n: usize, r: usize, words: &[usize]) -> usize {
        let total = q.pow(n as u32);
        let mut cur = vec![0u8; total];
        for &w in words {
            cur[w] = 1;
        }
        let mut next = vec![0u8; total];
        let mut tmp = vec![0u8; total];
        for _ in 0..r {
            dilate(&cur, &mut next, &mut tmp, q, n);
            std::mem::swap(&mut cur, &mut next);
        }
        cur.iter().filter(|&&b| b == 1).count()
    }

    #[test]
    fn repeticao_binaria_n3_cobre_tudo_com_raio_1() {
        assert_eq!(cover_count(2, 3, 1, &[0, 7]), 8);
    }

    #[test]
    fn uma_palavra_cobre_exatamente_a_bola_hamming() {
        // q=3,n=3,R=1: bola = 1 + 3*2 = 7
        assert_eq!(cover_count(3, 3, 1, &[0]), 7);
        // R=2: 1 + 6 + 3*4 = 19
        assert_eq!(cover_count(3, 3, 2, &[0]), 19);
    }
}
