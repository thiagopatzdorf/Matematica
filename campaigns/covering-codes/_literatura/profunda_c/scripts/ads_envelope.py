#!/usr/bin/env python3
"""Envelope ADS K1*K2/q com as cotas SUPERIORES q=7 do Kéri (6-21_tables.pdf, 2009-10-15, lidas por pdftotext; n<=8).
Nao afirma validade: exige normalidade/aceitabilidade (ver sec. 1.3). Lista todas as divisoes (n1,R1)+(n2,R2), n=n1+n2-1, R=R1+R2."""
U={ # U[(n,R)] = melhor UB tabelada q=7 (so as usadas; R<n)
(2,1):7,(3,1):25,(4,1):123,(5,1):769,(6,1):4435,(7,1):31045,(8,1):117649,
(3,2):7,(4,2):19,(5,2):97,(6,2):343,(7,2):2401,(8,2):15129,
(4,3):7,(5,3):17,(6,3):77,(7,3):343,(8,3):2337,
(5,4):7,(6,4):15,(7,4):49,(8,4):343,
(6,5):7,(7,5):11,(8,5):49,(7,6):7,(8,6):71 }
import itertools
def env(n,R):
    out=[]
    for (n1,R1),K1 in U.items():
        n2=n+1-n1; R2=R-R1
        if (n2,R2) in U and (n1,R1)<=(n2,R2):
            out.append((K1*U[(n2,R2)]/7,(n1,R1,K1),(n2,R2,U[(n2,R2)])))
    return sorted(out)
for (n,R,ref) in [(9,4,1475),(8,3,2337)]:
    print('alvo K_7(%d,%d), melhor publicada/Kéri %d'%(n,R,ref))
    for e,a,b in env(n,R)[:8]: print('   %9.1f  (n,R,K)=%s + %s'%(e,a,b))
