# Helper function to safely get values with defaults
def safe_get(data: dict, key: str, default=0):
    """Safely get value from dict, handling None."""
    value = data.get(key, default)
    return default if value is None else value


def safe_get_list(data: dict, key: str):
    """Safely get list from dict, handling None."""
    value = data.get(key, [])
    return [] if value is None else value