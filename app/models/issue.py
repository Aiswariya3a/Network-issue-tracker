from datetime import datetime

from pydantic import BaseModel


class Issue(BaseModel):
    row_index: int
    complaint_key: str | None = None
    timestamp: str
    email: str
    floor: str
    room: str
    ssid: str
    location: str
    issue_type: str
    description: str
    cluster_key: str
    status: str = "NOT RESOLVED"
    ict_member_name: str | None = None
    resolution_remark: str | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
