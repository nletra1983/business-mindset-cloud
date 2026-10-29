"""Протокол сессии на устройстве. Реальный secure store подключит Flutter-клиент."""


class MemoryDeviceSessionStore:
    def __init__(self):
        self._secret: str | None = None

    def put(self, session_secret: str) -> None:
        if not session_secret:
            raise ValueError("empty secret")
        self._secret = session_secret

    def get(self) -> str | None:
        return self._secret

    def clear(self) -> None:
        self._secret = None


def stay_signed_in(vault: MemoryDeviceSessionStore, sessions, book) -> dict:
    secret = vault.get()
    if not secret:
        return {"inside": False, "runs": []}
    person_id = sessions.person_id(secret)
    if person_id is None:
        return {"inside": False, "runs": []}
    return {"inside": True, "runs": list(book.runs_of(person_id)), "session_secret": secret}


def logout(vault: MemoryDeviceSessionStore, sessions, secret: str | None = None) -> dict:
    token = secret if secret is not None else vault.get()
    revoked = False
    if token:
        revoked = sessions.revoke(token)
    vault.clear()
    return {"signed_out": True, "revoked": revoked}
