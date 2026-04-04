"""
Applies the database migration to your Supabase project.

Usage:
    pip install -r requirements.txt
    python setup_db.py

Requires SUPABASE_DB_PASSWORD in .env (find it in Supabase Dashboard →
Project Settings → Database → Connection string).
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MIGRATION_FILE = Path(__file__).parent / "migrations" / "001_create_facebook_shop_tables.sql"
PROJECT_ID = "iymskhtltqfyshbfrlyc"


def _get_dsn() -> str:
    password = os.getenv("SUPABASE_DB_PASSWORD")
    if not password:
        return ""
    return (
        f"postgresql://postgres:{password}"
        f"@db.{PROJECT_ID}.supabase.co:5432/postgres"
    )


def apply_via_psycopg2(dsn: str, sql: str) -> None:
    try:
        import psycopg2  # type: ignore
    except ImportError:
        sys.exit(
            "psycopg2 is not installed.\n"
            "Install it with: pip install psycopg2-binary\n"
            "Or apply the migration manually (see below)."
        )

    print(f"Connecting to Supabase PostgreSQL …")
    with psycopg2.connect(dsn) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql)
    print("Migration applied successfully.")


def print_manual_instructions(sql: str) -> None:
    print("\n" + "=" * 60)
    print("MANUAL MIGRATION INSTRUCTIONS")
    print("=" * 60)
    print(
        f"Open the Supabase SQL Editor:\n"
        f"  https://supabase.com/dashboard/project/{PROJECT_ID}/sql/new\n"
        f"Then paste the contents of:\n"
        f"  {MIGRATION_FILE}\n"
        f"and click Run.\n"
    )


def main() -> None:
    sql = MIGRATION_FILE.read_text(encoding="utf-8")
    dsn = _get_dsn()

    if dsn:
        apply_via_psycopg2(dsn, sql)
    else:
        print(
            "SUPABASE_DB_PASSWORD not set — cannot connect directly.\n"
            "You can either:\n"
            "  1. Add SUPABASE_DB_PASSWORD to your .env and re-run this script.\n"
            "  2. Apply the migration manually."
        )
        print_manual_instructions(sql)


if __name__ == "__main__":
    main()
