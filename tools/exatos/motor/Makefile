# motor de busca exaustiva com rejeição de isomorfos (precisa de libnauty-dev)
NAUTY_INC ?= $(firstword $(wildcard /usr/include/x86_64-linux-gnu /usr/include/aarch64-linux-gnu) /usr/include)
NAUTY_LIB ?= $(firstword $(wildcard /usr/lib/x86_64-linux-gnu/libnautyL1.a /usr/lib/aarch64-linux-gnu/libnautyL1.a) -lnautyL1)
CFLAGS ?= -O3 -march=native -Wall

motor: motor.c
	$(CC) $(CFLAGS) -I$(NAUTY_INC) -o $@ $< $(NAUTY_LIB)

clean:
	rm -f motor
