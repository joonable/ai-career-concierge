import pytest

from common.config import Settings, get_settings, resolve_default_env_file


def test_settings_reject_missing_production_secrets():
    with pytest.raises(ValueError):
        Settings(
            APP_ENV="production",
            DATABASE_URL="postgresql+psycopg://postgres:test@db.example.supabase.co:5432/postgres",
            SUPABASE_URL="",
            SUPABASE_SERVICE_ROLE_KEY="",
            GOOGLE_CLIENT_ID="",
            GOOGLE_CLIENT_SECRET="",
            SLACK_SIGNING_SECRET="",
            GEMINI_API_KEY="",
        )


def test_settings_reject_dev_schedule_without_explicit_override():
    with pytest.raises(ValueError):
        Settings(
            APP_ENV="development",
            DATABASE_URL="postgresql+psycopg://postgres:test@db.example.supabase.co:5432/postgres",
            PIPELINE_ENABLED=True,
            ALLOW_DEV_SCHEDULE=False,
        )


def test_settings_allow_empty_database_url():
    settings = Settings(APP_ENV="development", DATABASE_URL="")
    assert settings.database_url == ""


def test_langsmith_prompt_identifiers_default_to_tagged_references():
    settings = Settings(APP_ENV="development", DATABASE_URL="")

    assert settings.langsmith_eval_prompt_identifier == "job-evaluation:staging"
    assert settings.langsmith_memory_prompt_identifier == "memory-summary:staging"


def test_settings_preserve_placeholder_database_url():
    settings = Settings(
        APP_ENV="development",
        DATABASE_URL=(
            "postgresql+psycopg://postgres:<SUPABASE_DB_PASSWORD>@"
            "db.example.supabase.co:5432/postgres"
        ),
    )
    assert "<SUPABASE_DB_PASSWORD>" in settings.database_url


def test_resolve_default_env_file_prefers_app_env_specific_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_ENV", "development")
    (tmp_path / ".env.development").write_text("SUPABASE_URL=https://example.supabase.co\n")
    (tmp_path / ".env").write_text("SUPABASE_URL=https://fallback.supabase.co\n")

    assert resolve_default_env_file() == ".env.development"


def test_get_settings_loads_default_env_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_ENV", "development")
    (tmp_path / ".env.development").write_text(
        "\n".join(
            [
                "DATABASE_URL=postgresql+psycopg://postgres:test@db.loaded.supabase.co:5432/postgres",
                "SUPABASE_URL=https://loaded-from-env-file.supabase.co",
                "INTERNAL_API_KEY=test-key",
                "ALLOW_DEV_SCHEDULE=true",
            ]
        )
        + "\n"
    )

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.supabase_url == "https://loaded-from-env-file.supabase.co"

    get_settings.cache_clear()
