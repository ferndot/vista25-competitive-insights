// GET /api/seed - Add sample data for testing
import { createClient } from '@supabase/supabase-js';

export async function GET() {
  try {
    // Validate environment variables
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
      return new Response(
        JSON.stringify({ error: 'Missing Supabase configuration' }), 
        { status: 500 }
      );
    }

    // Create Supabase client
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    );

    // Get competitors
    const { data: competitors, error: competitorsError } = await supabase
      .from('competitors')
      .select('*');

    if (competitorsError) {
      console.error('Error fetching competitors:', competitorsError);
      return new Response(
        JSON.stringify({ error: 'Failed to fetch competitors' }), 
        { status: 500 }
      );
    }

    if (!competitors || competitors.length === 0) {
      return new Response(
        JSON.stringify({ error: 'No competitors found. Run the migration first.' }), 
        { status: 400 }
      );
    }

    // Sample events data
    const sampleEvents = [
      {
        competitor_id: competitors[0].id, // Acme Corp
        headline: 'Acme Corp Announces Major Layoffs Affecting 500 Employees',
        summary: 'In a cost-cutting measure, Acme Corp has announced significant workforce reductions across multiple departments, affecting approximately 500 employees worldwide.',
        url: 'https://example.com/acme-layoffs',
        published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        is_important: true
      },
      {
        competitor_id: competitors[0].id, // Acme Corp
        headline: 'Acme Corp Reports Q4 Earnings Beat Expectations',
        summary: 'Acme Corp exceeded Wall Street expectations in Q4, reporting revenue of $2.1B vs expected $1.9B, driven by strong demand in their core products.',
        url: 'https://example.com/acme-earnings',
        published_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
        is_important: false
      },
      {
        competitor_id: competitors[0].id, // Acme Corp
        headline: 'Acme Corp Partners with TechGiant for AI Initiative',
        summary: 'Strategic partnership announced to develop next-generation AI solutions, combining Acme Corp\'s industry expertise with TechGiant\'s AI capabilities.',
        url: 'https://example.com/acme-partnership',
        published_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
        is_important: true
      },
      {
        competitor_id: competitors[1].id, // Globex Inc
        headline: 'Globex Inc Acquired by Private Equity Firm for $5.2B',
        summary: 'Global investment firm announces acquisition of Globex Inc in a deal valued at $5.2 billion, marking one of the largest tech acquisitions this year.',
        url: 'https://example.com/globex-acquisition',
        published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
        is_important: true
      },
      {
        competitor_id: competitors[1].id, // Globex Inc
        headline: 'Globex Inc Launches New Product Line',
        summary: 'Innovation continues at Globex Inc with the launch of their next-generation product suite targeting enterprise customers in the financial services sector.',
        url: 'https://example.com/globex-products',
        published_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
        is_important: false
      },
      {
        competitor_id: competitors[1].id, // Globex Inc
        headline: 'Globex Inc CEO Announces Resignation After 8 Years',
        summary: 'Long-time CEO steps down to pursue new opportunities. Board of Directors has initiated search for replacement while CFO takes interim role.',
        url: 'https://example.com/globex-ceo-resignation',
        published_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), // 12 hours ago
        is_important: true
      }
    ];

    let insertedCount = 0;

    // Insert sample events
    for (const event of sampleEvents) {
      const { data, error } = await supabase
        .from('competitor_events')
        .insert(event)
        .select();

      if (!error && data) {
        insertedCount++;
      } else if (error && !error.message.includes('duplicate key')) {
        // Ignore duplicate key errors, but log other errors
        console.error('Error inserting event:', error);
      }
    }

    return new Response(
      JSON.stringify({ 
        success: true,
        message: `Successfully seeded ${insertedCount} sample events`,
        competitors: competitors.length,
        inserted: insertedCount
      }), 
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );

  } catch (error) {
    console.error('Seed error:', error);
    return new Response(
      JSON.stringify({ error: 'Seeding failed: ' + error.message }), 
      { status: 500 }
    );
  }
} 