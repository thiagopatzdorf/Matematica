# Contexto: a RAIZ do repo (docker build -f infinito/Dockerfile .). A imagem leva o ledger, os códigos
# e o verificador compilado, então o módulo de matemática lê o mesmo que está no git.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 INF_REPO=/app/repo INF_VERIFY_BIN=/app/repo/tools/verify/verify
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY infinito/requirements.txt .
RUN pip install -r requirements.txt
COPY ledger ./repo/ledger
COPY data/codes ./repo/data/codes
COPY data/structured ./repo/data/structured
COPY tools/verify/verify.c ./repo/tools/verify/verify.c
COPY README.md ./repo/
COPY docs ./repo/docs
RUN gcc -O2 -o repo/tools/verify/verify repo/tools/verify/verify.c && apt-get purge -y gcc libc6-dev && apt-get autoremove -y
COPY infinito/infinito_mcp ./infinito_mcp
# Sem root: o processo só precisa do metadata server e da rede de saída.
RUN useradd --uid 10001 --no-create-home infinito
USER infinito
CMD ["python", "-m", "infinito_mcp.server"]
