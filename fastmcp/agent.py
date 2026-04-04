"""
Facebook Shop LangChain Chat Agent
===================================
An interactive ReAct agent that connects to the FastMCP server and uses
OpenAI GPT-4o to converse with the user about their Facebook Shop.

Usage:
    # In one terminal, start the MCP server in HTTP mode:
    python server.py --transport streamable-http

    # In another terminal, start the chat agent:
    python agent.py

Or run everything in a single process (stdio mode):
    python agent.py --inline
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# ── Inline single-process mode ─────────────────────────────────────────────────

async def run_inline_agent() -> None:
    """
    Spawn the MCP server as a subprocess (stdio transport) and connect
    the LangChain agent to it. Ideal for development / single-machine use.
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    from src import config  # validates env vars early

    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    )

    server_path = str(Path(__file__).parent / "server.py")

    async with MultiServerMCPClient(
        {
            "facebook-shop": {
                "command": sys.executable,
                "args": [server_path],
                "transport": "stdio",
            }
        }
    ) as mcp_client:
        tools = mcp_client.get_tools()
        agent = create_react_agent(llm, tools)
        await _chat_loop(agent)


# ── Remote HTTP mode ───────────────────────────────────────────────────────────

async def run_http_agent(host: str = "127.0.0.1", port: int = 8000) -> None:
    """
    Connect to an already-running FastMCP server over HTTP.
    Start the server first with: python server.py --transport streamable-http
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    from src import config

    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    )

    server_url = f"http://{host}:{port}/mcp"

    async with MultiServerMCPClient(
        {
            "facebook-shop": {
                "url": server_url,
                "transport": "streamable_http",
            }
        }
    ) as mcp_client:
        tools = mcp_client.get_tools()
        agent = create_react_agent(llm, tools)
        await _chat_loop(agent)


# ── Shared chat loop ───────────────────────────────────────────────────────────

async def _chat_loop(agent: Any) -> None:
    """Interactive REPL that sends user messages to the LangChain agent."""
    print("\n" + "=" * 60)
    print("  Facebook Shop Agent  (type 'exit' or Ctrl+C to quit)")
    print("=" * 60 + "\n")

    history: list[dict[str, str]] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        try:
            response = await agent.ainvoke({"messages": history})
            messages = response.get("messages", [])
            # Extract the last AI message
            ai_text = ""
            for msg in reversed(messages):
                role = getattr(msg, "type", None) or getattr(msg, "role", None)
                if role in ("ai", "assistant"):
                    ai_text = msg.content if hasattr(msg, "content") else str(msg)
                    break

            print(f"\nAgent: {ai_text}\n")
            history.append({"role": "assistant", "content": ai_text})

        except Exception as exc:
            print(f"\n[Error] {exc}\n")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    inline = "--inline" in sys.argv

    if inline:
        asyncio.run(run_inline_agent())
    else:
        from src import config
        asyncio.run(run_http_agent(host=config.MCP_HOST, port=config.MCP_PORT))


if __name__ == "__main__":
    main()
