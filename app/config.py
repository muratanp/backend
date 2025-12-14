import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "xandeum-monitor")
CACHE_TTL = int(os.getenv("CACHE_TTL", 60))

# FIXED: Parse IP_NODES from environment variable
IP_NODES_ENV = os.getenv("IP_NODES", "")
if IP_NODES_ENV:
    # Split by comma, strip whitespace, filter empty strings
    IP_NODES = [ip.strip() for ip in IP_NODES_ENV.split(",") if ip.strip()]
else:
    # Default fallback nodes (if IP_NODES not set in .env)
    IP_NODES = [
        "173.212.203.145",
        "173.212.220.65",
        "161.97.97.41",
        "192.190.136.36",
        "192.190.136.37",
        "192.190.136.38",
        "192.190.136.28",
        "192.190.136.29",
        "207.244.255.1"
    ]

# Validation: Ensure we have at least one IP node
if not IP_NODES:
    raise ValueError("No IP nodes configured. Set IP_NODES in .env or use defaults.")

print(f"✅ Loaded {len(IP_NODES)} IP nodes from configuration")