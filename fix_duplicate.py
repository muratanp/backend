#!/usr/bin/env python3
"""
Fix duplicate addresses in pnodes_registry before creating unique index.

This script:
1. Finds duplicate addresses
2. Keeps the most recent entry
3. Deletes older duplicates
4. Creates unique index

Run this ONCE before starting the API.
"""

import os
import sys
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv

# Load environment
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "xandeum-monitor")

if not MONGO_URI:
    print("❌ Error: MONGO_URI not found in .env")
    sys.exit(1)

print(f"Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
pnodes_registry = db["pnodes_registry"]

print(f"Connected to database: {MONGO_DB}")
print(f"Collection: pnodes_registry")
print()

# Step 1: Find duplicate addresses
print("Step 1: Finding duplicate addresses...")
pipeline = [
    {
        "$group": {
            "_id": "$address",
            "count": {"$sum": 1},
            "ids": {"$push": "$_id"}
        }
    },
    {
        "$match": {
            "count": {"$gt": 1}
        }
    }
]

duplicates = list(pnodes_registry.aggregate(pipeline))
print(f"Found {len(duplicates)} addresses with duplicates")

if not duplicates:
    print("✅ No duplicates found!")
    print()
    print("Creating unique index on address...")
    try:
        pnodes_registry.create_index([("address", 1)], unique=True)
        print("✅ Unique index created successfully!")
    except Exception as e:
        print(f"❌ Error creating index: {e}")
    sys.exit(0)

# Step 2: Remove duplicates (keep most recent)
print()
print("Step 2: Removing duplicates (keeping most recent)...")
deleted_count = 0

for dup in duplicates:
    address = dup["_id"]
    ids = dup["ids"]
    count = dup["count"]
    
    print(f"\n  Address: {address} ({count} duplicates)")
    
    # Get all documents for this address, sorted by last_seen (most recent first)
    docs = list(pnodes_registry.find(
        {"address": address}
    ).sort("last_seen", DESCENDING))
    
    if not docs:
        continue
    
    # Keep the most recent one
    keep_id = docs[0]["_id"]
    keep_last_seen = docs[0].get("last_seen", 0)
    
    print(f"    Keeping: {keep_id} (last_seen: {keep_last_seen})")
    
    # Delete all others
    for doc in docs[1:]:
        doc_id = doc["_id"]
        doc_last_seen = doc.get("last_seen", 0)
        
        try:
            pnodes_registry.delete_one({"_id": doc_id})
            deleted_count += 1
            print(f"    Deleted: {doc_id} (last_seen: {doc_last_seen})")
        except Exception as e:
            print(f"    ❌ Error deleting {doc_id}: {e}")

print()
print(f"✅ Removed {deleted_count} duplicate entries")

# Step 3: Verify no duplicates remain
print()
print("Step 3: Verifying cleanup...")
remaining_dups = list(pnodes_registry.aggregate(pipeline))

if remaining_dups:
    print(f"⚠️  Warning: Still have {len(remaining_dups)} duplicates!")
    print("Run this script again or manually clean them up.")
    sys.exit(1)
else:
    print("✅ No duplicates remaining")

# Step 4: Create unique index
print()
print("Step 4: Creating unique index on address...")
try:
    # Drop existing index if it exists (but isn't unique)
    try:
        pnodes_registry.drop_index("address_1")
        print("  Dropped existing non-unique index")
    except:
        pass
    
    # Create unique index
    pnodes_registry.create_index([("address", 1)], unique=True)
    print("✅ Unique index created successfully!")
except Exception as e:
    print(f"❌ Error creating index: {e}")
    sys.exit(1)

# Step 5: Show summary
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
total_docs = pnodes_registry.count_documents({})
print(f"Total documents in registry: {total_docs}")
print(f"Duplicates removed: {deleted_count}")
print(f"Unique addresses: {total_docs}")
print()
print("✅ Database is ready!")
print("You can now start the API:")
print("  uvicorn app.main:app --reload --port 8000")
print("=" * 60)