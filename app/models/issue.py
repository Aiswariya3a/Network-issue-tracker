from pydantic import BaseModel


class Issue(BaseModel):
    row_index: int
    timestamp: str
    email: str
    floor: str
    room: str
    ssid: str
    location: str
    issue_type: str
    description: str
    cluster_key: str
    status: str = "Open"
