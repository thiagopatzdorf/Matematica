# Formato do witness de K_7(9,4) ≤ 1137

- `code_1137.txt`: 1137 linhas, uma palavra por linha, terminadas em `\n`.
- Cada palavra são 9 caracteres em `0123456`. O caractere j (j = 0..8) é a coordenada j, um elemento
  de Z/7 = {0,…,6}.
- As linhas estão em ordem lexicográfica estrita (forma canônica), sem repetição.
- O sha256 do arquivo é o "sha256 canônico" usado no repositório:
  `df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102`.
- `code_1137.json` traz as mesmas palavras, na mesma ordem, com metadados (q, n, raio, tamanho).
- Indexação usada pelos verificadores: `i(x) = Σ_j x_j · 7^j`, em [0, 7^9) = [0, 40 353 607).
- A distância é a de Hamming (número de coordenadas diferentes). "Cobre com raio 4" significa que todo
  x de (Z/7)^9 tem uma palavra c com d_H(x, c) ≤ 4.

Nenhum verificador modifica estes arquivos. Confira com `sha256sum -c SHA256SUMS`.
