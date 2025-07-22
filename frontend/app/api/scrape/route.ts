// GET /api/scrape?run=1
import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

const NEWS_ENDPOINT = 'https://newsapi.org/v2/everything';
const IMPORTANT_RX = /(layoff|acquired|funding|CEO resigns?|CFO resigns?|partners? with)/i;

export async function GET() {
  try {
    // Validate environment variables
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
      return new Response(
        JSON.stringify({ error: 'Missing Supabase configuration' }), 
        { status: 500 }
      );
    }

    // Create Supabase client inside the handler to avoid build-time errors
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    );

    // Fetch all competitors from database
    const { data: companies, error: companiesError } = await supabase
      .from('competitors')
      .select('*');
    
    if (companiesError) {
      console.error('Error fetching companies:', companiesError);
      return new Response(
        JSON.stringify({ error: 'Failed to fetch companies' }), 
        { status: 500 }
      );
    }

    let totalProcessed = 0;
    let totalInserted = 0;

    // Process each competitor
    for (const company of companies ?? []) {
      try {
        // Fetch news for this company
        const response = await axios.get(NEWS_ENDPOINT, {
          params: {
            q: `"${company.name}"`,
            pageSize: 20,
            apiKey: process.env.NEWSAPI_KEY,
            sortBy: 'publishedAt',
          },
        });

        const articles = response.data.articles ?? [];
        totalProcessed += articles.length;

        // Process each article
        for (const article of articles) {
          const { title, description, url, publishedAt } = article;
          
          if (!title || !url) continue; // Skip invalid articles
          
          const isImportant = IMPORTANT_RX.test(title + ' ' + (description || ''));
          
          // Try to insert the event (will be ignored if URL already exists due to unique constraint)
          const { data, error } = await supabase
            .from('competitor_events')
            .insert({
              competitor_id: company.id,
              headline: title,
              summary: description,
              url,
              published_at: publishedAt,
              is_important: isImportant,
            })
            .select();

          if (!error && data) {
            totalInserted++;
          }
        }
      } catch (articleError) {
        console.error(`Error processing articles for ${company.name}:`, articleError);
        // Continue with next company
      }
    }

    return new Response(
      JSON.stringify({ 
        ok: true, 
        processed: totalProcessed,
        inserted: totalInserted,
        companies: companies?.length ?? 0
      }), 
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );

  } catch (error) {
    console.error('Scraper error:', error);
    return new Response(
      JSON.stringify({ error: 'Scraping failed' }), 
      { status: 500 }
    );
  }
} 