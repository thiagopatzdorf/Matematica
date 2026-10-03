// Verificador clean-room de codigos de cobertura sobre Z_q^n.
//
// Algoritmo: BFS multi-fonte no grafo de Hamming H(n,q). As M palavras do
// codigo entram na fila com distancia 0; cada vertice expandido empurra seus
// n*(q-1) vizinhos ainda nao visitados com distancia+1. Pela propriedade do
// BFS, o primeiro nivel em que um vertice aparece e exatamente
// min_c d_H(x,c). Expande-se ate o nivel R; todo vertice nao visitado ao fim
// tem distancia > R, logo nao e coberto.
package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

const maxPoints = 1_500_000_000 // teto: 5 bytes/ponto (dist + fila)

func usage(msg string) {
	fmt.Fprintln(os.Stderr, "erro: "+msg)
	fmt.Fprintln(os.Stderr, "uso: verify-cleanroom --q Q --n N --R R --M M <arquivo>")
	os.Exit(3)
}

func main() {
	args := os.Args[1:]
	vals := map[string]int{}
	have := map[string]bool{}
	var file string
	nfile := 0
	for i := 0; i < len(args); i++ {
		a := args[i]
		switch a {
		case "--q", "--n", "--R", "--M":
			if i+1 >= len(args) {
				usage("falta valor de " + a)
			}
			v, err := strconv.Atoi(args[i+1])
			if err != nil {
				usage("valor invalido para " + a + ": " + args[i+1])
			}
			if have[a] {
				usage("parametro repetido " + a)
			}
			vals[a], have[a] = v, true
			i++
		default:
			if len(a) > 1 && a[0] == '-' {
				usage("opcao desconhecida " + a)
			}
			file = a
			nfile++
		}
	}
	for _, k := range []string{"--q", "--n", "--R", "--M"} {
		if !have[k] {
			usage("parametro obrigatorio ausente: " + k)
		}
	}
	if nfile != 1 {
		usage("informe exatamente um arquivo")
	}
	q, n, R, M := vals["--q"], vals["--n"], vals["--R"], vals["--M"]
	if q < 2 || q > 10 || n < 1 || R < 0 || M < 1 {
		usage("parametros fora do dominio (2<=q<=10, n>=1, R>=0, M>=1)")
	}
	total := 1
	pw := make([]int, n)
	for i := 0; i < n; i++ {
		pw[i] = total
		total *= q
		if total > maxPoints {
			usage("q^n grande demais para este verificador")
		}
	}

	f, err := os.Open(file)
	if err != nil {
		usage("arquivo ilegivel: " + err.Error())
	}
	defer f.Close()
	sc := bufio.NewReaderSize(f, 1<<20)

	dist := make([]uint8, total)
	const unseen = 255
	for i := range dist {
		dist[i] = unseen
	}
	queue := make([]uint32, 0, total) // capacidade fixa: sem copias de crescimento (pico de RSS)
	bad := ""
	count := 0
	lineNo := 0
	for {
		line, rerr := sc.ReadString('\n')
		if len(line) == 0 && rerr != nil {
			if rerr.Error() != "EOF" {
				usage("erro de leitura: " + rerr.Error())
			}
			break
		}
		lineNo++
		if line[len(line)-1] == '\n' {
			line = line[:len(line)-1]
		}
		if len(line) > 0 && line[len(line)-1] == '\r' {
			line = line[:len(line)-1]
		}
		if len(line) != n {
			bad = fmt.Sprintf("linha %d: comprimento %d != n=%d", lineNo, len(line), n)
			break
		}
		idx := 0
		ok := true
		for k := 0; k < n; k++ {
			c := line[k]
			if c < '0' || c > '9' || int(c-'0') >= q {
				bad = fmt.Sprintf("linha %d: digito invalido %q para q=%d", lineNo, c, q)
				ok = false
				break
			}
			idx += int(c-'0') * pw[k]
		}
		if !ok {
			break
		}
		if dist[idx] == 0 {
			bad = fmt.Sprintf("linha %d: palavra duplicada %s", lineNo, line)
			break
		}
		dist[idx] = 0
		queue = append(queue, uint32(idx))
		count++
		if rerr != nil {
			break
		}
	}
	if bad == "" && count != M {
		bad = fmt.Sprintf("numero de palavras distintas %d != M=%d", count, M)
	}
	if bad != "" {
		fmt.Printf("INVALIDO q=%d n=%d R=%d M=%d: %s\n", q, n, R, M, bad)
		os.Exit(2)
	}

	// BFS por niveis; queue[lo:hi] e o nivel atual.
	lo := 0
	for lvl := 0; lvl < R && lo < len(queue); lvl++ {
		hi := len(queue)
		nd := uint8(lvl + 1)
		for ; lo < hi; lo++ {
			x := int(queue[lo])
			for p := 0; p < n; p++ {
				d := (x / pw[p]) % q
				base := x - d*pw[p]
				for a := 0; a < q; a++ {
					if a == d {
						continue
					}
					y := base + a*pw[p]
					if dist[y] == unseen {
						dist[y] = nd
						queue = append(queue, uint32(y))
					}
				}
			}
		}
	}
	covered := len(queue)
	if covered == total {
		fmt.Printf("COBRE q=%d n=%d R=%d M=%d points=%d uncovered=0\n", q, n, R, M, total)
		os.Exit(0)
	}
	first := 0
	for first < total && dist[first] != unseen {
		first++
	}
	w := make([]byte, n)
	for k, x := 0, first; k < n; k++ {
		w[k] = byte('0' + x%q)
		x /= q
	}
	fmt.Printf("NAO COBRE q=%d n=%d R=%d M=%d points=%d uncovered=%d first_uncovered=%s\n",
		q, n, R, M, total, total-covered, string(w))
	os.Exit(1)
}
