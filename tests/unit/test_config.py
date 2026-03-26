import pytest

from common.config import Settings


def test_settings_reject_missing_production_secrets():
    with pytest.raises(ValueError):
        Settings(
            APP_ENV="production",
            DATABASE_URL="sqlite:///./.data/prod.db",
            SUPABASE_URL="",
            SUPABASE_SERVICE_ROLE_KEY="",
            GOOGLE_CLIENT_ID="",
            GOOGLE_CLIENT_SECRET="",
            SLACK_SIGNING_SECRET="",
            GEMINI_API_KEY="",
        )


def test_settings_reject_dev_schedule_without_explicit_override():
    with pytest.raises(ValueError):
        Settings(APP_ENV="development", PIPELINE_ENABLED=True, ALLOW_DEV_SCHEDULE=False)
