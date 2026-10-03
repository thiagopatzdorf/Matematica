//! verify_bfs -- verificador C: BFS multifonte no grafo de Hamming H(9,7).
//!
//! Vértices = (Z/7)^9 (7^9); arestas = trocar UMA coordenada (54 vizinhos). A distância de Hamming
//! a C é a distância no grafo a partir do conjunto-fonte C. O BFS parte de todas as palavras com
//! distância 0 e expande por camadas; nenhuma comparação palavra a palavra é feita.
//! Uso: verify_bfs code.txt [N_esperado=1137]   Compilar: rustc -O -o verify_bfs main.rs
use std::{env, fs, process, time::Instant};

const Q: u32 = 7;
const N: usize = 9;
const SPACE: usize = 40_353_607;

fn main() {
    let a: Vec<String> = env::args().collect();
    if a.len() < 2 { eprintln!("uso: verify_bfs code.txt [N]"); process::exit(2); }
    let esperado: usize = a.get(2).map(|s| s.parse().unwrap()).unwrap_or(1137);
    let t0 = Instant::now();
    let text = fs::read(&a[1]).expect("ler arquivo");
    if text.last() != Some(&b'\n') { eprintln!("FAIL formato: falta newline final"); process::exit(1); }
    let mut pw = [1u32; N];
    for j in 1..N { pw[j] = pw[j - 1] * Q; }
    let mut dist = vec![u8::MAX; SPACE];
    let mut frontier: Vec<u32> = Vec::new();
    for (k, line) in text[..text.len() - 1].split(|&b| b == b'\n').enumerate() {
        if line.len() != N || line.iter().any(|&b| !(b'0'..=b'6').contains(&b)) {
            eprintln!("FAIL formato: linha {} inválida", k + 1); process::exit(1);
        }
        let idx: u32 = line.iter().enumerate().map(|(j, &b)| (b - b'0') as u32 * pw[j]).sum();
        if dist[idx as usize] == 0 { eprintln!("FAIL formato: palavra repetida na linha {}", k + 1); process::exit(1); }
        dist[idx as usize] = 0;
        frontier.push(idx);
    }
    let words = frontier.len();
    let mut cnt = vec![frontier.len() as u64];
    let mut d: u8 = 0;
    while !frontier.is_empty() {
        let mut next = Vec::new();
        for &x in &frontier {
            for j in 0..N {
                let digit = (x / pw[j]) % Q;
                let base = x - digit * pw[j];
                for v in 0..Q {
                    if v == digit { continue; }
                    let y = (base + v * pw[j]) as usize;
                    if dist[y] == u8::MAX { dist[y] = d + 1; next.push(y as u32); }
                }
            }
        }
        d += 1;
        if !next.is_empty() { cnt.push(next.len() as u64); }
        frontier = next;
    }
    let total: u64 = cnt.iter().sum();
    let uncovered = dist.iter().filter(|&&x| x == u8::MAX).count() as u64;   // inalcançável (não deve ocorrer)
    let maxd = cnt.len() - 1;
    let beyond: u64 = cnt.iter().skip(5).sum::<u64>() + uncovered;
    println!("verificador C (BFS multifonte no grafo de Hamming, Rust)");
    println!("q = {}\nn = {}\nR = 4\n|C| = {}", Q, N, words);
    for r in 0..cnt.len().max(5) { println!("N_{} = {}", r, cnt.get(r).copied().unwrap_or(0)); }
    println!("total = {} (esperado {})", total + uncovered, SPACE);
    println!("covered = {}\nuncovered = {}", total + uncovered - beyond, beyond);
    println!("max_distance = {}\nfarthest_points = {}", maxd, cnt[maxd]);
    let mut shown = 0;
    for i in 0..SPACE {
        if dist[i] as usize == maxd && shown < 3 {
            let s: String = (0..N).map(|j| char::from(b'0' + ((i as u32 / pw[j]) % Q) as u8)).collect();
            println!("example_farthest = {}", s); shown += 1;
        }
    }
    println!("runtime_internal_s = {:.1}", t0.elapsed().as_secs_f64());
    let ok = words == esperado && beyond == 0 && maxd <= 4 && total as usize == SPACE;
    println!("{}", if ok { "PASS" } else { "FAIL" });
    process::exit(if ok { 0 } else { 1 });
}
