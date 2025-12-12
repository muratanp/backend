import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "xandeum-monitor")
CACHE_TTL = int(os.getenv("CACHE_TTL", 60))
