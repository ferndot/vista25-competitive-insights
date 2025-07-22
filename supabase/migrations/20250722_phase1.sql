-- 20250722_phase1.sql

-- Clean up old database structures
DROP TABLE IF EXISTS public.competitor_events CASCADE;
DROP TABLE IF EXISTS public.competitors CASCADE;
DROP TABLE IF EXISTS public.signals CASCADE;

-- Drop indexes if they exist
DROP INDEX IF EXISTS public.idx_company;
DROP INDEX IF EXISTS public.idx_detected;

create table public.competitors (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  ticker text,
  created_at timestamptz default now()
);

CREATE TABLE IF NOT EXISTS public.signals (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    impact TEXT NOT NULL,
    title TEXT NOT NULL,
    action TEXT NOT NULL,
    confidence TEXT,
    person TEXT,
    amount TEXT,
    source_url TEXT,
    detected_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_company ON public.signals(company_name);
CREATE INDEX IF NOT EXISTS idx_detected ON public.signals(detected_at DESC);

-- row‑level security OFF for hackathon speed
alter table public.competitors disable row level security;
alter table public.signals disable row level security;

insert into public.competitors (name,ticker) values
  ('Acme Corp','ACME'),
  ('Globex Inc','GLOB'); 