"""
Lightweight client for the InsForge-specific API structure.
InsForge uses functional semantic paths like /api/database/records/{table}.
"""
from __future__ import annotations
import os
import httpx
from typing import Any
from dotenv import load_dotenv

load_dotenv()

class InsForgeClient:
    def __init__(self, base_url: str, api_key: str):
        # Ensure base URL doesn't have a trailing slash
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def table(self, table_name: str) -> TableQuery:
        return TableQuery(self, table_name)

class TableQuery:
    def __init__(self, client: InsForgeClient, table_name: str):
        self.client = client
        self.table_name = table_name

    def upsert(self, data: dict[str, Any], on_conflict: str | None = None) -> TableExecutor:
        # InsForge typically handles upsert via a specific endpoint or POST with params
        # For our wrapper, we'll hit the functional record endpoint
        return TableExecutor(self.client, "UPSERT", self.table_name, data, on_conflict=on_conflict)

    def delete(self) -> TableExecutor:
        return TableExecutor(self.client, "DELETE", self.table_name)

    def select(self, columns: str = "*") -> TableExecutor:
        return TableExecutor(self.client, "SELECT", self.table_name, columns=columns)

    def insert(self, data: dict[str, Any]) -> TableExecutor:
        return TableExecutor(self.client, "INSERT", self.table_name, data)

class TableExecutor:
    def __init__(self, client: InsForgeClient, method: str, table: str, data: Any = None, 
                 on_conflict: str | None = None, columns: str = "*"):
        self.client = client
        self.method = method
        self.table = table
        self.data = data
        self.on_conflict = on_conflict
        self.columns = columns
        self._filters = {}

    def eq(self, column: str, value: Any) -> TableExecutor:
        self._filters[column] = value
        return self

    def limit(self, count: int) -> TableExecutor:
        # Not implemented for this simple wrapper yet, but can be added
        return self
    
    def order(self, column: str) -> TableExecutor:
        # Not implemented for this simple wrapper yet
        return self

    def execute(self) -> Any:
        url = f"{self.client.base_url}/api/database/records/{self.table}"
        
        with httpx.Client(headers=self.client.headers, timeout=10.0) as client:
            if self.method == "UPSERT":
                # For Upsert in PostgREST-compatible APIs, we need the Prefer header
                headers = {**self.client.headers, "Prefer": "resolution=merge-duplicates"}
                payload = self.data
                params = {"on_conflict": self.on_conflict} if self.on_conflict else {}
                resp = client.post(url, json=payload, params=params, headers=headers)
            elif self.method == "INSERT":
                resp = client.post(url, json=self.data)
            elif self.method == "DELETE":
                # Most agentic backends use DELETE with filters as query params
                resp = client.delete(url, params=self._filters)
            elif self.method == "SELECT":
                # Standard GET with filters as query params
                resp = client.get(url, params=self._filters)
            else:
                raise ValueError(f"Unsupported method: {self.method}")

            if resp.status_code >= 400:
                raise Exception(f"InsForge API Error ({resp.status_code}): {resp.text}")
            
            # Wrap response to match supabase-py result.data structure
            return type("Result", (), {"data": resp.json()})

_client: InsForgeClient | None = None

def get_client() -> InsForgeClient:
    global _client
    if _client is None:
        from src import config
        _client = InsForgeClient(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
    return _client
