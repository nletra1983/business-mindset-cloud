import hashlib
import json
import secrets
import uuid


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def new_secret() -> str:
    return secrets.token_urlsafe(32)


class MemorySessionStore:
    def __init__(self):
        self.by_hash: dict[str, dict] = {}
        self.operations: dict[tuple[str, str], dict] = {}

    def issue(self, person_id) -> str:
        secret = new_secret()
        self.by_hash[hash_secret(secret)] = {
            "person_id": str(person_id),
            "revoked": False,
        }
        return secret

    def person_id(self, secret: str):
        row = self.by_hash.get(hash_secret(secret or ""))
        if row is None or row["revoked"]:
            return None
        return row["person_id"]

    def revoke(self, secret: str) -> bool:
        row = self.by_hash.get(hash_secret(secret or ""))
        if row is None:
            return False
        row["revoked"] = True
        return True

    def get_operation(self, person_id, key: str):
        return self.operations.get((str(person_id), key))

    def save_operation(self, person_id, key: str, response: dict) -> None:
        self.operations[(str(person_id), key)] = response


class SqlSessionStore:
    def __init__(self, conn):
        self.conn = conn

    def issue(self, person_id) -> str:
        secret = new_secret()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO app_session (id, person_id, secret_hash)
                VALUES (%s, %s, %s)
                """,
                (uuid.uuid4(), person_id, hash_secret(secret)),
            )
        self.conn.commit()
        return secret

    def person_id(self, secret: str):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT person_id FROM app_session
                WHERE secret_hash = %s AND revoked_at IS NULL
                """,
                (hash_secret(secret or ""),),
            )
            row = cur.fetchone()
        return None if row is None else row[0]

    def revoke(self, secret: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE app_session
                SET revoked_at = now()
                WHERE secret_hash = %s AND revoked_at IS NULL
                """,
                (hash_secret(secret or ""),),
            )
            changed = cur.rowcount > 0
        self.conn.commit()
        return changed

    def get_operation(self, person_id, key: str):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT response_json FROM processed_app_operation
                WHERE person_id = %s AND operation_key = %s
                """,
                (person_id, key),
            )
            row = cur.fetchone()
        if row is None:
            return None
        payload = row[0]
        if isinstance(payload, str):
            return json.loads(payload)
        return payload

    def save_operation(self, person_id, key: str, response: dict) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO processed_app_operation (person_id, operation_key, response_json)
                VALUES (%s, %s, %s::jsonb)
                ON CONFLICT (person_id, operation_key) DO NOTHING
                """,
                (person_id, key, json.dumps(response, ensure_ascii=False)),
            )
        self.conn.commit()
