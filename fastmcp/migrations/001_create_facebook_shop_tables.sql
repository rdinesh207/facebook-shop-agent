-- Migration: 001_create_facebook_shop_tables
-- Apply via: python setup_db.py
-- Or paste into Supabase SQL Editor at https://supabase.com/dashboard

-- ── Shops / Catalogs ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shops (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  fb_catalog_id TEXT        UNIQUE NOT NULL,
  fb_page_id    TEXT        NOT NULL,
  name          TEXT        NOT NULL,
  description   TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Products ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
  id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  fb_product_id TEXT         UNIQUE NOT NULL,
  catalog_id    TEXT         NOT NULL,
  name          TEXT         NOT NULL,
  description   TEXT,
  price         NUMERIC(12,2),
  currency      TEXT         DEFAULT 'USD',
  availability  TEXT,
  image_url     TEXT,
  product_url   TEXT,
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Orders ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  fb_order_id  TEXT        UNIQUE NOT NULL,
  page_id      TEXT        NOT NULL,
  status       TEXT        NOT NULL,
  buyer_name   TEXT,
  buyer_email  TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Order Items ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
  id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id       UUID         NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  fb_product_id  TEXT         NOT NULL,
  quantity       INTEGER      NOT NULL DEFAULT 1,
  price_per_unit NUMERIC(12,2),
  currency       TEXT         DEFAULT 'USD'
);

-- ── Indexes ────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_products_catalog_id    ON products(catalog_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(fb_product_id);
CREATE INDEX IF NOT EXISTS idx_orders_page_id         ON orders(page_id);
CREATE INDEX IF NOT EXISTS idx_orders_status          ON orders(status);

-- ── Auto-update trigger ────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS products_updated_at ON products;
CREATE TRIGGER products_updated_at
  BEFORE UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS orders_updated_at ON orders;
CREATE TRIGGER orders_updated_at
  BEFORE UPDATE ON orders
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
