# Contributing to Xandeum PNode Aggregation API

Thank you for your interest in contributing to the Xandeum PNode Aggregation API! This guide will help you safely add new IP nodes, improve the API, or suggest features.

---

## 1. Getting Started

1. **Fork the repository** and clone it locally:

   ```bash
   git clone https://github.com/your-username/pnode-aggregation-api.git
   cd pnode-aggregation-api
   ```
2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** by copying `.env.example` and filling in your MongoDB URI and optional configuration:

   ```bash
   cp .env.example .env
   ```

---

## 2. Adding a New IP Node

To add a new pNode IP:

1. **Verify the node first**:

   * **Recommended (automated) method**: Use the `verify_pnode.py` script included in the repository:

     ```bash
     python verify_pnode.py <NEW_NODE_IP>
     ```

     * The script tests `get-version`, `get-stats`, and `get-pods`.
     * Only nodes that **pass all tests** should be added.

   * **Manual `curl` method**:

     ```bash
     curl -X POST http://<NEW_IP>:6000/rpc \
       -H "Content-Type: application/json" \
       -d '{"jsonrpc":"2.0","method":"get-version","id":1}'
     ```

     Repeat for `get-stats` and `get-pods`.

2. **Add the node** to `.env` under `IP_NODES`:

   ```
   IP_NODES=existing_ip_1,existing_ip_2,new_ip_here
   ```

3. **Test the node locally** by running the API:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   * Check `/all-nodes` to ensure the new node appears and responds correctly.

---

## 3. Running the API Locally

1. Start FastAPI:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. Open `http://127.0.0.1:8000/docs` to explore the endpoints.
3. `/all-nodes` endpoint shows aggregated data from all IP nodes listed in `.env`.

---

## 4. Making Changes

* Always create a **feature branch**:

  ```bash
  git checkout -b feature/add-new-node
  ```
* Make your changes and **test locally**.
* Commit your changes with a **clear message**:

  ```bash
  git add .
  git commit -m "Add new IP node 123.45.67.89"
  ```
* Push and create a **Pull Request** against the main branch.

---

## 5. Testing Contributions

* Verify all new nodes respond to `get-version`, `get-stats`, and `get-pods`.
* Run FastAPI locally and check `/all-nodes` correctly aggregates the new node.
* Check MongoDB to ensure the background fetcher is storing snapshots correctly.

---

## 6. Guidelines

* Only add nodes that are **active and publicly accessible**.
* Avoid committing `.env` or sensitive credentials.
* Use **descriptive commit messages**.
* Follow Python best practices for code clarity.

---

## 7. Support

For questions or issues:

* Open a GitHub issue in the repository.
* Contact the Xandeum dev team via [support channel/contact info].

---

**Thank you for contributing!**
Your contributions keep the Xandeum PNode network analytics accurate and up to date.
