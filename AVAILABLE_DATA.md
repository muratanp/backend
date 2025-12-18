# Available Data Fields

## From get-version
- version: string
- build_date: string (if available)

## From get-stats
- cpu_percent: float
- ram_used: int
- ram_total: int
- uptime: int
- packets_received: int
- packets_sent: int
- active_streams: int
- total_bytes: int
- total_pages: int
- file_size: int

## From get-pods / get-pods-with-stats
- address: string (IP:port)
- pubkey: string
- is_public: bool
- rpc_port: int
- storage_committed: int
- storage_used: int
- storage_usage_percent: float
- uptime: int
- version: string
- last_seen: string
- last_seen_timestamp: int

### PAGING METRICS (if available from get-pods-with-stats)
- page_hit_rate: float (?)
- page_miss_rate: float (?)
- total_page_accesses: int (?)
- page_errors: int (?)
- avg_page_latency_ms: float (?)
- replication_coverage: float (?)
- throughput_pages_per_sec: float (?)
