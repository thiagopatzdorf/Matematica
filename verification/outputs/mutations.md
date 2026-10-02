| mutação | o que mudou | formato | cobertura (BFS) | rejeitada? |
|---|---|---|---|---|
| remove_one_word | removida a palavra 201603513 | PASS | tamanho=1136 uncovered=423 max_d=5 -> FAIL | sim |
| remove_5_words | removidas 153362352,431250604,444363665,505555500,655502544 | PASS | tamanho=1132 uncovered=1817 max_d=5 -> FAIL | sim |
| duplicate_one_word_and_remove_another | 616666663 trocada por cópia de 111111163 | 1 duplicatas; não está em ordem canônica (lexicográfica estrita) | BFS recusa (saída 1: FAIL formato: palavra repetida na linha 1021) | sim |
| change_coordinate | 366365552 -> 366335552 | PASS | tamanho=1137 uncovered=6 max_d=5 -> FAIL | sim |
| replace_word | 544004531 -> 456466205 (aleatória) | PASS | tamanho=1137 uncovered=17 max_d=5 -> FAIL | sim |
| truncate_word | 242535315 -> 24253531 | linha 427: palavra inválida '24253531' | BFS recusa (saída 1: FAIL formato: linha 427 inválida) | sim |
| value_7 | 341314414 -> 341314714 | linha 586: palavra inválida '341314714' | BFS recusa (saída 1: FAIL formato: linha 586 inválida) | sim |
| negative_value | 634021561 -> -14021561 | linha 1059: palavra inválida '-14021561'; não está em ordem canônica (lexicográfica estrita) | BFS recusa (saída 1: FAIL formato: linha 1059 inválida) | sim |

PASS: todas as mutações foram rejeitadas
