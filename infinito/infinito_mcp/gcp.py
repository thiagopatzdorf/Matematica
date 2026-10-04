"""Token da service account do serviço, pelo metadata server do Cloud Run. Sem chave em lugar nenhum."""
from __future__ import annotations

import json
import urllib.request

METADATA = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"


def token_metadata() -> str:
    req = urllib.request.Request(METADATA, headers={"Metadata-Flavor": "Google"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["access_token"]
