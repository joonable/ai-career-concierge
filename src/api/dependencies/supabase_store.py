from __future__ import annotations

from functools import lru_cache

from api.services.supabase_storage import (
    SupabaseEvaluationStore,
    SupabaseJobStore,
    SupabaseRestClient,
    SupabaseSystemLogStore,
    SupabaseUserStore,
)
from common.config import get_settings


@lru_cache(maxsize=1)
def get_supabase_rest_client() -> SupabaseRestClient:
    return SupabaseRestClient(get_settings())


def get_user_store() -> SupabaseUserStore:
    return SupabaseUserStore(get_supabase_rest_client())


def get_evaluation_store() -> SupabaseEvaluationStore:
    return SupabaseEvaluationStore(get_supabase_rest_client())


def get_job_store() -> SupabaseJobStore:
    return SupabaseJobStore(get_supabase_rest_client())


def get_system_log_store() -> SupabaseSystemLogStore:
    return SupabaseSystemLogStore(get_supabase_rest_client())
