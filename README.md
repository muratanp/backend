# Xandeum pNode Analytics Platform

**Production-ready analytics API for the Xandeum PNode.**

[![API Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-repo)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **The PNode Explorer for Xandeum Storage Performance**  
> Track pnodes, analyze performance, make informed staking decisions.

---

## 🎯 What is This?

A comprehensive analytics platform that enables **stakers**, **operators**, and **developers** to monitor the Xandeum pNode network in real-time.

### Key Features

- **🔍 Node Discovery** - Track all all pNodes across the network
- **📊 Performance Scoring** - 3-score system (Trust, Capacity, Stake Confidence)
- **📈 Historical Analytics** - 30 days of network trends and growth metrics
- **🚨 Alert System** - Automatic detection of problematic nodes
- **🔗 Network Topology** - Visualize gossip protocol connections
- **⚡ Real-Time Updates** - Data refreshes every 60 seconds

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB Atlas account (free tier works)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/your-repo/xandeum-pnode-analytics.git
cd xandeum-pnode-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your MongoDB URI
```

### Configuration

Edit `.env`:

```bash
# Required
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=xandeum-monitor

# Optional
CACHE_TTL=60  # Refresh interval in seconds
IP_NODES=173.212.203.145,173.212.220.65,...  # Comma-separated
```

### Run Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Visit: http://localhost:8000/docs

---

## 📚 Documentation

- **[API Reference](API_REFERENCE.md)** - Complete endpoint documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[Architecture](ARCHITECTURE.md)** - System design and data flow
- **[Contributing](CONTRIBUTION.md)** - How to contribute

---

## 🎨 Example Usage

### Get Top Staking Nodes

```bash
curl "http://localhost:8000/recommendations?limit=5" | jq '.recommendations[] | {address, score, tier}'
```

### Check Network Health

```bash
curl "http://localhost:8000/network/health" | jq '.health'
```

### Compare Nodes

```bash
curl "http://localhost:8000/pnodes/compare?addresses=node1:9001,node2:9001" | jq '.winners'
```

### Get Alerts

```bash
curl "http://localhost:8000/alerts/critical" | jq '.critical_nodes'
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │ ← HTTP Requests
└────────┬────────┘
         │
    ┌────▼────┐
    │ MongoDB │ ← Snapshot Storage
    └────▲────┘
         │
┌────────┴────────┐
│ Background      │ ← RPC Polling (60s)
│ Worker          │
└────────┬────────┘
         │
    ┌────▼────┐
    │ 9 IP    │ ← Gossip Protocol
    │ Nodes   │
    └─────────┘
```

### Data Flow

1. **Background Worker** polls 9 IP nodes every 60 seconds
2. Aggregates gossip data, deduplicates by address
3. Calculates performance scores
4. Saves snapshot to MongoDB
5. **API Endpoints** serve from latest snapshot (fast!)

---

## 📊 API Endpoints

### Core

- `GET /health` - API health check
- `GET /pnodes` - Unified node data (MAIN ENDPOINT)
- `GET /recommendations` - Top nodes for staking
- `GET /network/topology` - Network graph data
- `GET /network/health` - Network health metrics
- `GET /operators` - Operator distribution

### Historical

- `GET /network/history` - Time-series data
- `GET /network/growth` - Growth metrics
- `GET /network/analytics` - Comprehensive analytics

### Advanced

- `GET /pnodes/{address}/alerts` - Node-specific alerts
- `GET /alerts` - Network-wide alerts
- `GET /pnodes/compare` - Compare multiple nodes
- `GET /network/consistency` - Gossip consistency tracking

**Full documentation:** http://localhost:8000/docs

---

## 🧪 Testing

### Run All Tests

```bash
# Comprehensive test suite
python test_comprehensive.py

# Phase-specific tests
python test_phase4.py
python test_phase5.py

# Quick API test
./test_api.sh
```

### Manual Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed test procedures.

---

## 🚢 Deployment

### Quick Deploy Options

**Railway:**
```bash
railway init
railway variables set MONGO_URI="mongodb+srv://..."
railway up
```

**Self-Hosted:**
```bash
# See DEPLOYMENT.md for complete guide
sudo systemctl enable xandeum-api
sudo systemctl start xandeum-api
```

**Estimated cost:** Start with free trial on Railway and then $5-25/month depending on platform

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 📈 Performance

### Benchmarks (Local Testing)

| Endpoint | Response Time | Notes |
|----------|---------------|-------|
| `/health` | ~30ms | System check |
| `/pnodes` (100 nodes) | ~250ms | With scoring |
| `/recommendations` | ~300ms | Pre-sorted |
| `/network/topology` | ~150ms | Graph data |
| `/network/health` | ~400ms | Full analysis |
| `/network/analytics` | ~450ms | Comprehensive |

**Database:** MongoDB Atlas M0 (free tier)  
**Server:** Railway Basic Dyno

---

## 🎯 Use Cases

### For Token Stakers

**Find reliable nodes to stake on:**

```python
import requests

# Get top 5 nodes
response = requests.get("http://localhost:8000/recommendations?limit=5")
nodes = response.json()["recommendations"]

for node in nodes:
    print(f"{node['address']}")
    print(f"  Score: {node['score']}/100")
    print(f"  Risk: {node['tier']}")
    print(f"  Uptime: {node['uptime_days']} days")
```

### For Node Operators

**Monitor your nodes:**

```bash
# Check for alerts
curl "http://localhost:8000/pnodes/pnode-address/alerts"

# Check gossip consistency
curl "http://localhost:8000/node/pnode-address/consistency"
```

### For Developers

**Build dashboards:**

```javascript
// Real-time network stats
const response = await fetch('http://localhost:8000/network/health');
const health = await response.json();

console.log(`Network: ${health.health.status}`);
console.log(`Nodes: ${health.summary.online_pnodes}/${health.summary.total_pnodes}`);
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTION.md](CONTRIBUTION.md) for guidelines.

### Adding IP Nodes

1. Verify node: `python verify_pnode.py <IP>`
2. Add to `.env`: `IP_NODES=existing,new_ip`
3. Test locally
4. Submit pull request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests before committing
python test_comprehensive.py

# Format code
black app/
```

---

## 📦 Project Structure

```
xandeum-pnode-analytics/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & endpoints
│   ├── db.py            # MongoDB operations
│   ├── fetcher.py       # Background worker
|   ├── helpers.py       # Helpers function
│   ├── scoring.py       # Performance scoring
│   ├── alerts.py        # Alert system
│   ├── config.py        # Configuration
│   └── utils/
│       └── jsonrpc.py   # RPC helpers
├── docs/
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   └── ...
├── tests/
│   ├── test_comprehensive.py
│   ├── test_phase4.py
│   └── test_phase5.py
├── requirements.txt
├── .env.example        # Copy this in .env
├── Procfile            # Railway deployment
└── README.md
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue:** "Snapshot not available"  
**Solution:** Wait 60 seconds for background worker to run

**Issue:** "MongoDB connection failed"  
**Solution:** Check MONGO_URI in .env, verify IP whitelist

**Issue:** Slow response times  
**Solution:** Increase CACHE_TTL, upgrade server, check MongoDB region

See [DEPLOYMENT.md#troubleshooting](docs/DEPLOYMENT.md#troubleshooting) for more.

---

## 📊 Scoring Methodology

### Trust Score (0-100)

- **40%** - Uptime consistency (30+ days = full points)
- **30%** - Gossip presence (seen by 3+ IP nodes)
- **20%** - Version compliance (latest version)
- **10%** - Gossip consistency (stable presence)

### Capacity Score (0-100)

- **30%** - Storage committed (normalized to 100GB)
- **40%** - Usage balance (optimal 20-80%)
- **30%** - Growth trend (requires historical data)

### Stake Confidence

Composite: 60% trust + 40% capacity

- **80-100** - Low risk 🟢
- **60-79** - Medium risk 🟡
- **0-59** - High risk 🔴

---

## 🗺️ Roadmap

### ✅ Completed (Phases 1-6)

- Core API infrastructure
- Performance scoring system
- Historical tracking (30 days)
- Alert system
- Gossip consistency tracking
- Network analytics
- Comprehensive testing
- Production deployment
- Documentation finalization


### 🚧 In Progress 
- **Phase 7:** Frontend dashboard (Next.js)

### 📅 Planned (Future)

- **Phase 8:** Real-time WebSocket updates
- **Phase 9:** Email/webhook notifications
- **Phase 10:** ML-based anomaly detection

---

## 📜 License

MIT License.

---

## 🙏 Acknowledgments

- **Xandeum Team** - For building the storage network
- **Community Contributors** - For testing and feedback
- **Open Source Projects** - FastAPI, MongoDB, Python ecosystem

---

## 📞 Support

- **Documentation:** [GitHub Wiki](https://github.com/muratanp/backend/wiki)
- **Issues:** [GitHub Issues](https://github.com/muratanp/backend/issues)
- **Discord:** [Community Server](https://discord.gg/uqRSmmM5m)
- **X:** [@Xandeum](https://twitter.com/Xandeum)

---

## 🎉 Production Ready!

This API is production-ready and powering analytics for the Xandeum network.

**Live demo:** https://web-production-b4440.up.railway.app/  
**API docs:** https://web-production-b4440.up.railway.app/docs

---

**Built with ❤️ for the Xandeum Community**

*Last updated: December 2025*
