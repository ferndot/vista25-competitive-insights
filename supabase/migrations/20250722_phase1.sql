-- 20250722_phase1.sql

-- ===============================================
-- COMPREHENSIVE DATABASE CLEANUP
-- ===============================================
-- This section removes all old database structures
-- to ensure a clean state for the signals table

-- Drop any existing views first
DROP VIEW IF EXISTS public.competitor_view CASCADE;
DROP VIEW IF EXISTS public.events_view CASCADE;
DROP VIEW IF EXISTS public.signals_view CASCADE;

-- Drop any existing functions
DROP FUNCTION IF EXISTS public.get_competitor_events CASCADE;
DROP FUNCTION IF EXISTS public.get_signals CASCADE;

-- Drop existing tables with CASCADE to handle dependencies
DROP TABLE IF EXISTS public.competitor_events CASCADE;
DROP TABLE IF EXISTS public.competitors CASCADE;
DROP TABLE IF EXISTS public.signals CASCADE;
DROP TABLE IF EXISTS public.companies CASCADE;
DROP TABLE IF EXISTS public.news_events CASCADE;
DROP TABLE IF EXISTS public.market_signals CASCADE;
DROP TABLE IF EXISTS public.intelligence CASCADE;

-- Drop any existing indexes
DROP INDEX IF EXISTS public.idx_company;
DROP INDEX IF EXISTS public.idx_detected;
DROP INDEX IF EXISTS public.idx_competitor_id;
DROP INDEX IF EXISTS public.idx_published_at;
DROP INDEX IF EXISTS public.idx_events_date;
DROP INDEX IF EXISTS public.idx_signals_date;
DROP INDEX IF EXISTS public.idx_company_name;

-- Drop any existing sequences
DROP SEQUENCE IF EXISTS public.competitors_id_seq CASCADE;
DROP SEQUENCE IF EXISTS public.signals_id_seq CASCADE;

-- ===============================================
-- CREATE SIGNALS TABLE
-- ===============================================
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

-- Create optimized indexes
CREATE INDEX IF NOT EXISTS idx_company ON public.signals(company_name);
CREATE INDEX IF NOT EXISTS idx_detected ON public.signals(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_impact ON public.signals(impact);
CREATE INDEX IF NOT EXISTS idx_signal_type ON public.signals(signal_type);

-- ===============================================
-- SECURITY SETTINGS
-- ===============================================
-- Disable row‑level security for hackathon speed
ALTER TABLE public.signals DISABLE ROW LEVEL SECURITY; 