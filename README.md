# Facebook Shop MCP Agent

An AI agent built with **FastMCP** and **LangChain** that manages Facebook Shops via the Meta Business SDK and persists all data to **Supabase**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Chat Client  (agent.py  or  Cursor / Claude via MCP)       │
└────────────────────────┬────────────────────────────────────┘
                         │  LangChain ReAct Agent (GPT-4o)
                         │  langchain-mcp-adapters
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FastMCP Server  (server.py)                                │
│                                                             │
│  Tools exposed:                                             │
│   create_shop          get_shop_info                        │
│   create_product_listing  list_products  get_product        │
│   list_orders          get_order        is_product_sold     │
└──────────────┬───────────────────────────┬──────────────────┘
               │                           │
               ▼                           ▼
   Meta Business SDK               Supabase (iymskhtltqfyshbfrlyc)
   (facebook_business)             Tables: shops · products
   Graph API v25.0                         orders · order_items
```

---

## Prerequisites

- Python 3.11+
- A [Meta for Developers](https://developers.facebook.com) app with the following permissions:
  - `catalog_management`
  - `pages_read_engagement`
  - `commerce` (for orders)
- A Facebook Page linked to a Commerce Account
- A [Supabase](https://supabase.com) project (ID: `iymskhtltqfyshbfrlyc`)
- An OpenAI API key

---

## Installation

```bash
git clone https://github.com/rdinesh207/facebook-shop-agent
cd facebook-shop-agent
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

cd fastmcp
pip install -r requirements.txt
```

---

## Configuration

Copy the example env file and fill in your credentials:

```bash
# From inside the fastmcp/ folder:
cp .env.example .env
```

Open `fastmcp/.env` and set:

| Variable | Description |
|---|---|
| `FACEBOOK_ACCESS_TOKEN` | Long-lived user / system-user token |
| `FACEBOOK_APP_ID` | Your Meta App ID |
| `FACEBOOK_APP_SECRET` | Your Meta App Secret |
| `FACEBOOK_PAGE_ID` | Facebook Page ID linked to your Shop |
| `FACEBOOK_BUSINESS_ID` | Meta Business Manager ID |
| `FACEBOOK_CATALOG_ID` | (Optional) Pre-existing catalog ID |
| `SUPABASE_URL` | `https://iymskhtltqfyshbfrlyc.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (for server-side writes) |
| `SUPABASE_DB_PASSWORD` | Database password (used by `setup_db.py`) |
| `OPENAI_API_KEY` | OpenAI API key |

All keys are available in your [Supabase Dashboard → Project Settings → API](https://supabase.com/dashboard/project/iymskhtltqfyshbfrlyc/settings/api).

---

## Database Setup

From the `fastmcp/` folder, run the migration script to create all required tables:

```bash
cd fastmcp
python setup_db.py
```

If `SUPABASE_DB_PASSWORD` is set, the script connects directly and applies the migration. Otherwise, it prints instructions for applying the SQL manually in the Supabase Dashboard.

Alternatively, open the [Supabase SQL Editor](https://supabase.com/dashboard/project/iymskhtltqfyshbfrlyc/sql/new) and paste the contents of `fastmcp/migrations/001_create_facebook_shop_tables.sql`.

---

## Running

All commands below are run from the `fastmcp/` folder.

### Option A — Interactive Chat Agent (inline, single process)

The agent spawns the MCP server automatically:

```bash
cd fastmcp
python agent.py --inline
```

### Option B — MCP Server + Agent (two processes)

Start the MCP server in HTTP mode:

```bash
cd fastmcp
python server.py --transport streamable-http
```

In a separate terminal, start the agent:

```bash
cd fastmcp
python agent.py
```

### Option C — Use as an MCP Server in Cursor / Claude Desktop

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "facebook-shop": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/facebook-shop-agent/fastmcp",
      "env": {
        "PYTHONPATH": "/path/to/facebook-shop-agent/fastmcp"
      }
    }
  }
}
```

---

## Available MCP Tools

| Tool | Description |
|---|---|
| `create_shop` | Create a new Facebook Shop (product catalog) and save to DB |
| `get_shop_info` | Get metadata and product count for a catalog |
| `create_product_listing` | Add a product to a catalog, persist to DB |
| `list_products` | List products in a catalog, optionally sync to DB |
| `get_product` | Fetch a single product's details |
| `list_orders` | List Facebook Commerce orders, optionally sync to DB |
| `get_order` | Fetch a single order with line items |
| `is_product_sold` | Check if a product has been purchased (live API or DB cache) |

---

## Project Structure

```
facebook-shop-agent/
├── .gitignore
├── README.md
├── backend/                          Future backend service
├── frontend/                         Future frontend
└── fastmcp/                          ← All MCP server code lives here
    ├── .env.example                  Template for environment variables
    ├── requirements.txt
    ├── server.py                     FastMCP server — defines all 8 tools
    ├── agent.py                      LangChain chat agent (GPT-4o + MCP tools)
    ├── setup_db.py                   One-time database migration script
    ├── migrations/
    │   └── 001_create_facebook_shop_tables.sql
    └── src/
        ├── config.py                 Loads and validates all env vars
        ├── facebook/
        │   ├── client.py             Meta Business SDK initialisation
        │   ├── shops.py              Catalog (shop) create / fetch
        │   ├── products.py           Product CRUD via SDK
        │   └── orders.py             Orders and sale status via Graph API
        └── database/
            ├── supabase_client.py    Supabase singleton client
            ├── shops_db.py           shops table CRUD
            ├── products_db.py        products table CRUD
            └── orders_db.py          orders + order_items CRUD
```

---

## Notes

- **Facebook User Token**: `FACEBOOK_ACCESS_TOKEN` is currently read from `.env`. A future frontend integration will supply it dynamically per user session.
- **Order API permissions**: Listing orders requires the `commerce` permission on the page token and a connected Commerce Account.
- **Rate limits**: Facebook Graph API enforces rate limits. Use `sync_to_db=True` on `list_products` and `list_orders` to cache data locally and reduce API calls.

---

## License

MIT
