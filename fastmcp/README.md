# fastmcp — Facebook Shop MCP Server

This directory contains the FastMCP server, LangChain chat agent, and all supporting code for the Facebook Shop MCP Agent.

For full setup and usage instructions see the [project README](../README.md).

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and fill in your credentials

# 3. Apply database migration
python setup_db.py

# 4. Start the agent (spawns MCP server automatically)
python agent.py --inline
```

## Running the MCP server standalone

```bash
# stdio  (for Cursor / Claude Desktop)
python server.py

# HTTP  (for agent.py in a separate terminal)
python server.py --transport streamable-http
```
