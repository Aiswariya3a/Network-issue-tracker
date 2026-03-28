from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    google_sheet_csv_url: str = ""
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 8
    email_sender: str = ""
    email_password: str = ""
    email_receiver: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    report_hour: int = 18
    report_minute: int = 0
    scheduler_timezone: str = "Asia/Kolkata"
    report_test_interval_minutes: int = 0
    attach_raw_csv_report: bool = False
    frontend_origin: str = "http://localhost:5173"
    retention_days: int = 30
    retention_cleanup_hour: int = 1
    retention_cleanup_minute: int = 30
    archive_before_delete: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
