# PoC: busca tabu de cotas superiores K_q(n,R) ≤ M em GPU (T4)

Pergunta: a GPU corta o custo da busca de cotas superiores (ou muda o método)? Isto mede, não opina.

* `tabu_gpu.cu`: a busca tabu de `tools/busca_direta/tabu.c` (mesmo movimento, mesma casca de raio exato R),
  uma cadeia por bloco de 128 threads. `-DEMU` (g++ -x c++) roda o mesmo código em CPU para teste de correção.
* `bench_cpu.py`: base de CPU, o próprio `tabu.c`, P processos em paralelo, tempo até o 1º ACHOU e it/s.
* `tests/test_busca_gpu_emu.py`: contagem incremental == recontagem do zero; código achado passa no verificador.

Compilar na GPU: `nvcc -O3 -arch=sm_75 -o tabu_gpu tools/busca_gpu/tabu_gpu.cu`.
Resultado de busca é hipótese até passar por `tools/verify/verify`.
