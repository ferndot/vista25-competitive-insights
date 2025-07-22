# External Signals MVP - Phase 1

A competitor intelligence platform built with Next.js 14, Supabase, and DaisyUI that monitors competitor activities and provides real-time notifications for important events.

## 🚀 Features

- **Competitor Monitoring**: Track multiple competitors with automated news scraping
- **Smart Classification**: Automatically identify important events (layoffs, acquisitions, funding, executive changes, partnerships)
- **Real-time Notifications**: Toast notifications for important competitor events
- **Modern UI**: Clean interface with DaisyUI tabs and responsive tables
- **NewsAPI Integration**: Automated news fetching and deduplication

## 🛠 Tech Stack

- **Frontend**: Next.js 14 (App Router), React, Tailwind CSS, DaisyUI
- **Backend**: Supabase (PostgreSQL, Realtime)
- **Data Source**: NewsAPI
- **Notifications**: react-hot-toast with custom components

## 📋 Prerequisites

- Node.js 18+
- Supabase account
- NewsAPI account (free tier: 100 requests/day)

## 🚀 Local Development Setup

### 1. Environment Setup

Create a `.env.local` file in the root directory:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# NewsAPI Configuration
NEWSAPI_KEY=your_newsapi_key
```

### 2. Database Setup

1. Create a new Supabase project
2. Run the migration SQL in your Supabase SQL editor:

```sql
-- Copy and paste contents of supabase/migrations/20250722_phase1.sql
-- This creates competitors and competitor_events tables with seed data
```

Alternatively, if you have Supabase CLI installed:

```bash
supabase start
supabase db reset
```

### 3. Install Dependencies & Start Development

```bash
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

## 📊 Usage

### 1. Seed Competitor Data

Visit `http://localhost:3000/api/scrape` to fetch initial news data for the seeded competitors (Acme Corp, Globex Inc).

The scraper will:
- Fetch up to 20 articles per competitor
- Classify events as "important" using keyword detection
- Deduplicate articles by URL
- Return processing statistics

### 2. View Competitor Intelligence

Navigate to `http://localhost:3000/competitors` to:
- Browse competitor events in tabbed interface
- View article headlines, summaries, and publication dates
- See importance classification with badges
- Click headlines to read full articles

### 3. Real-time Notifications

Important events automatically trigger toast notifications when new data is scraped or inserted directly into the database.

## 🔧 API Endpoints

### GET /api/scrape

Fetches news for all competitors and stores events in the database.

**Response:**
```json
{
  "ok": true,
  "processed": 40,
  "inserted": 15,
  "companies": 2
}
```

## 📁 Project Structure

```
/app
  /api/scrape/route.ts          # News scraping endpoint
  /competitors/page.js          # Main competitor intelligence UI
  layout.js                    # App layout with Toaster
/components
  ImportantToast.js             # Custom toast for important events
  LayoutClient.js               # Client-side layout wrapper
/supabase/migrations
  20250722_phase1.sql          # Database schema and seed data
/libs
  /supabase                    # Supabase client configuration
```

## 🎯 Key Implementation Details

### Important Event Detection

Events are classified as important using regex pattern matching:
```javascript
const IMPORTANT_RX = /(layoff|acquired|funding|CEO resigns?|CFO resigns?|partners? with)/i;
```

### Realtime Updates

Supabase realtime subscription listens for new important events:
```javascript
channel.on('postgres_changes', {
  event: 'INSERT',
  schema: 'public',
  table: 'competitor_events',
  filter: 'is_important=eq.true'
}, handleImportantEvent);
```

### Data Deduplication

Articles are deduplicated using a unique constraint on the `url` column, preventing duplicate entries from multiple scraping runs.

## ⚡ Performance Notes

- **NewsAPI Limits**: Free tier allows 100 requests/day with 24-hour article delay
- **Polling**: UI polls for updates every 60 seconds
- **Realtime**: Important events trigger immediate notifications
- **No Authentication**: All data is public (RLS disabled for hackathon speed)

## 🔮 Future Enhancements (Phase 2+)

- User authentication and personalized dashboards
- Custom competitor addition/management
- Advanced filtering and search
- Email/Slack notification integrations
- Sentiment analysis and trend detection
- Export capabilities (PDF, CSV)

## 🐛 Troubleshooting

### No events showing up?
1. Verify Supabase connection in browser console
2. Check that migration was applied successfully
3. Test the scraper endpoint directly

### Realtime notifications not working?
1. Ensure Supabase realtime is enabled in your project
2. Check browser console for websocket connection errors
3. Verify the realtime subscription code is running

### Scraper failing?
1. Verify NewsAPI key is valid and not rate-limited
2. Check network connectivity
3. Review API endpoint logs in browser dev tools

---

Built for the 24-hour External Signals MVP hackathon. Phase 1 completed in ~6 hours with full competitor monitoring, real-time notifications, and modern UI.

