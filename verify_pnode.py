import httpx
import sys
import asyncio

# List of methods to test
PRPC_METHODS = ["get-version", "get-stats", "get-pods"]

async def test_node(ip: str):
    url = f"http://{ip}:6000/rpc"
    async with httpx.AsyncClient(timeout=3.0) as client:
        results = {}
        for method in PRPC_METHODS:
            payload = {"jsonrpc": "2.0", "method": method, "id": 1}
            try:
                r = await client.post(url, json=payload)
                if r.status_code == 200 and "result" in r.json():
                    results[method] = "✅ Success"
                else:
                    results[method] = f"❌ Failed: {r.text}"
            except Exception as e:
                results[method] = f"❌ Error: {e}"
        return results

async def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_node.py <IP_ADDRESS>")
        sys.exit(1)

    ip = sys.argv[1]
    print(f"Testing pNode at {ip}...\n")
    results = await test_node(ip)

    for method, status in results.items():
        print(f"{method}: {status}")

    if all("✅" in status for status in results.values()):
        print("\nAll tests passed! Node is ready to add to IP_NODES.")
    else:
        print("\nSome tests failed. Node should not be added yet.")

if __name__ == "__main__":
    asyncio.run(main())
