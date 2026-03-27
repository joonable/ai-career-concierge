from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from fastapi import HTTPException, status

from api.dependencies.auth import UserIdentity
from api.services.supabase_storage import SupabaseUserStore


class FakeSupabaseClient:
    def __init__(
        self,
        rows,
        *,
        fail_insert_with_duplicate=False,
        hide_existing_rows_until_after_failed_insert=False,
    ):
        self.rows = [deepcopy(row) for row in rows]
        self.insert_calls = []
        self.update_calls = []
        self.fail_insert_with_duplicate = fail_insert_with_duplicate
        self.hide_existing_rows_until_after_failed_insert = hide_existing_rows_until_after_failed_insert
        self.failed_insert = False

    def select(self, table, *, params=None, headers=None):
        del headers
        assert table == "users"
        params = params or {}
        field = None
        query = None
        for candidate in ("id", "oauth_id", "email"):
            if candidate in params:
                field = candidate
                query = params[candidate]
                break

        if field is None or query is None:
            return [deepcopy(row) for row in self.rows]

        if self.hide_existing_rows_until_after_failed_insert and not self.failed_insert:
            return []

        expected = query.split("eq.", 1)[1]
        matches = [deepcopy(row) for row in self.rows if str(row[field]) == expected]
        limit = params.get("limit")
        if limit == "1":
            return matches[:1]
        return matches

    def insert(self, table, payload, *, upsert=False):
        assert table == "users"
        self.insert_calls.append(deepcopy(payload))
        if self.fail_insert_with_duplicate:
            self.failed_insert = True
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    'Supabase data API request failed: {"code":"23505","details":"Key '
                    '(id) already exists.","hint":null,"message":"duplicate key value violates '
                    'unique constraint \\"users_pkey\\""}'
                ),
            )
        self.rows.extend(deepcopy(payload))
        return deepcopy(payload)

    def update(self, table, payload, *, params):
        assert table == "users"
        self.update_calls.append({"payload": deepcopy(payload), "params": deepcopy(params)})
        target_id = params["id"].split("eq.", 1)[1]
        for index, row in enumerate(self.rows):
            if str(row["id"]) == target_id:
                updated = {**row, **deepcopy(payload)}
                self.rows[index] = updated
                return [deepcopy(updated)]
        raise AssertionError("Expected a matching row to update.")


def test_supabase_user_store_prefers_existing_row_by_user_id():
    user_id = uuid4()
    client = FakeSupabaseClient(
        [
            {
                "id": str(user_id),
                "oauth_id": "legacy-oauth-id",
                "email": "legacy@example.com",
                "profile_data": {},
                "guidelines": {},
                "notification_settings": {},
                "created_at": "2026-03-27T00:00:00+00:00",
                "updated_at": "2026-03-27T00:00:00+00:00",
            }
        ]
    )
    store = SupabaseUserStore(client)

    profile = store.upsert_from_identity(
        UserIdentity(
            user_id=user_id,
            oauth_id=str(user_id),
            email="new@example.com",
        )
    )

    assert profile.user_id == user_id
    assert profile.email == "new@example.com"
    assert client.insert_calls == []
    assert len(client.update_calls) == 1
    assert client.update_calls[0]["params"] == {"id": f"eq.{user_id}"}


def test_supabase_user_store_inserts_when_no_existing_row_matches():
    user_id = uuid4()
    client = FakeSupabaseClient([])
    store = SupabaseUserStore(client)

    profile = store.upsert_from_identity(
        UserIdentity(
            user_id=user_id,
            oauth_id=str(user_id),
            email="new@example.com",
        )
    )

    assert profile.user_id == user_id
    assert profile.email == "new@example.com"
    assert len(client.insert_calls) == 1
    assert client.update_calls == []
    assert client.insert_calls[0][0]["id"] == str(user_id)


def test_supabase_user_store_recovers_when_insert_hits_duplicate_primary_key():
    user_id = uuid4()
    client = FakeSupabaseClient(
        [
            {
                "id": str(user_id),
                "oauth_id": "legacy-oauth-id",
                "email": "legacy@example.com",
                "profile_data": {},
                "guidelines": {},
                "notification_settings": {},
                "created_at": "2026-03-27T00:00:00+00:00",
                "updated_at": "2026-03-27T00:00:00+00:00",
            }
        ],
        fail_insert_with_duplicate=True,
        hide_existing_rows_until_after_failed_insert=True,
    )
    store = SupabaseUserStore(client)

    profile = store.upsert_from_identity(
        UserIdentity(
            user_id=user_id,
            oauth_id=str(user_id),
            email="new@example.com",
        )
    )

    assert profile.user_id == user_id
    assert profile.email == "new@example.com"
    assert len(client.insert_calls) == 1
    assert len(client.update_calls) == 1
