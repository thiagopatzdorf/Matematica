# Auxiliar C++ da captura de relações

`inercia.cpp` imprime a inércia "excepcional" dos ideais algébricos (`lado p r inércia`, `r = p` é o ponto no infinito),
exatamente como `renumber_t::inertia_from_p_r` do CADO-NFS. O `dup2` divide o expoente de `p` pela inércia antes de guardar só os
expoentes ímpares; sem esse número o purge reproduzido erra uma coluna quando `p^2 | lc(f)` ou há ideal ramificado.

Compilar dentro de uma árvore construída do CADO (`$CADO` = a árvore, `$BUILD` = o diretório de construção):

    INC=$(grep CXX_INCLUDES $BUILD/utils/CMakeFiles/numbertheory_tool.dir/flags.make | cut -d= -f2-)
    c++ -std=gnu++20 -O2 -fopenmp $INC inercia.cpp -o inercia $BUILD/utils/libutils.a -lgmp -lpthread -lm

Usar na captura: `CADO_INERCIA=<binário>` no ambiente de `medir_cado.py` / `captura_relacoes.py`. O `badidealinfo` vem da própria pasta de
trabalho do CADO (`<nome>.badidealinfo`); para uma captura antiga, `$BUILD/utils/numbertheory_tool -poly poly.txt -badideals x -badidealinfo y -ell 1000003`
(sai com código 1 por causa do `ell`, mas grava os arquivos) e `captura_relacoes.acrescentar_arquivo`.
