from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


STATUS_NOT_RESOLVED = "NOT RESOLVED"
STATUS_ACKNOWLEDGED = "ACKNOWLEDGED"
STATUS_RESOLVED = "RESOLVED"

ALLOWED_STATUSES = {
    STATUS_NOT_RESOLVED,
    STATUS_ACKNOWLEDGED,
    STATUS_RESOLVED,
}


class UpdateStatusRequest(BaseModel):
    status: Literal["NOT RESOLVED", "ACKNOWLEDGED", "RESOLVED"]
    ict_member_name: str | None = Field(default=None, max_length=128)
    resolution_remark: str | None = Field(default=None, max_length=1000)

    @field_validator("ict_member_name", "resolution_remark")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def validate_status_payload(self) -> "UpdateStatusRequest":
        if not self.ict_member_name:
            raise ValueError("ict_member_name is required.")
        if self.status == STATUS_ACKNOWLEDGED and not self.resolution_remark:
            raise ValueError("resolution_remark is required for ACKNOWLEDGED.")
        return self
