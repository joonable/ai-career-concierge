from __future__ import annotations

import hashlib
import hmac


class SlackSignatureService:
    def __init__(self, signing_secret: str):
        self.signing_secret = signing_secret

    def verify(self, *, timestamp: str, signature: str, body: bytes) -> bool:
        basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        expected = "v0=" + hmac.new(
            self.signing_secret.encode("utf-8"),
            basestring.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
