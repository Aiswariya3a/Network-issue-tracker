import re


LOCATION_PATTERN = re.compile(
    r"^\s*(?P<floor>[^-]+?)\s*-\s*(?P<room>[^()]+?)\s*(?:\((?P<ssid>[^)]+)\))?\s*$"
)


def parse_location(location: str) -> dict[str, str]:
    if not location:
        return {"floor": "", "room": "", "ssid": ""}

    match = LOCATION_PATTERN.match(location)
    if not match:
        return {"floor": "", "room": "", "ssid": ""}

    return {
        "floor": match.group("floor").strip(),
        "room": match.group("room").strip(),
        "ssid": (match.group("ssid") or "").strip(),
    }
