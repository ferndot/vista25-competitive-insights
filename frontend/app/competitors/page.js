'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/libs/supabase/client';
import toast from 'react-hot-toast';
import ImportantToast from '@/components/ImportantToast';

export default function CompetitorsPage() {
  const [competitors, setCompetitors] = useState([]);
  const [events, setEvents] = useState([]);
  const [signals, setSignals] = useState([]);
  const [activeTab, setActiveTab] = useState('');
  const [viewMode, setViewMode] = useState('events'); // 'events' or 'signals'
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      console.log('Fetching data from Supabase...');
      
      // Create Supabase client inside function to avoid build-time errors
      const supabase = createClient();
      
      // Fetch competitors
      console.log('Fetching competitors...');
      const { data: competitorsData, error: competitorsError } = await supabase
        .from('competitors')
        .select('*')
        .order('name');

      if (competitorsError) {
        console.error('Error fetching competitors:', competitorsError);
        setError('Failed to fetch competitors: ' + competitorsError.message);
        setLoading(false);
        return;
      }

      console.log('Competitors fetched:', competitorsData);

      // Fetch all events
      console.log('Fetching events...');
      const { data: eventsData, error: eventsError } = await supabase
        .from('competitor_events')
        .select('*')
        .order('published_at', { ascending: false });

      if (eventsError) {
        console.error('Error fetching events:', eventsError);
        setError('Failed to fetch events: ' + eventsError.message);
        setLoading(false);
        return;
      }

      console.log('Events fetched:', eventsData);

      // Fetch all signals
      console.log('Fetching signals...');
      const { data: signalsData, error: signalsError } = await supabase
        .from('signals')
        .select('*')
        .order('detected_at', { ascending: false });

      if (signalsError) {
        console.error('Error fetching signals:', signalsError);
        // Don't fail if signals table doesn't exist yet
        if (!signalsError.message.includes('does not exist')) {
          setError('Failed to fetch signals: ' + signalsError.message);
          setLoading(false);
          return;
        }
      }

      console.log('Signals fetched:', signalsData);

      setCompetitors(competitorsData || []);
      setEvents(eventsData || []);
      setSignals(signalsData || []);
      
      // Set first competitor as active tab if none selected
      if (!activeTab && competitorsData && competitorsData.length > 0) {
        setActiveTab(competitorsData[0].id);
      }
      
      setLastUpdated(new Date());
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Unexpected error: ' + error.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Set up polling every 60 seconds
    const interval = setInterval(fetchData, 60000);
    
    // Set up realtime subscription for important events
    const supabase = createClient();
    const channel = supabase.channel('public:competitor_events');
    
    channel.on(
      'postgres_changes',
      { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'competitor_events', 
        filter: 'is_important=eq.true' 
      },
      (payload) => {
        const event = payload.new;
        
        // Show custom toast for important events
        toast.custom((t) => (
          <ImportantToast 
            event={event} 
            onDismiss={() => toast.dismiss(t.id)} 
          />
        ), {
          duration: 10000, // Show for 10 seconds
          position: 'top-right',
        });
        
        // Refresh data to show the new event
        fetchData();
      }
    ).subscribe();
    
    return () => {
      clearInterval(interval);
      if (channel) {
        supabase.removeChannel(channel);
      }
    };
  }, []);

  const getEventsForCompetitor = (competitorId) => {
    return events.filter(event => event.competitor_id === competitorId);
  };

  const getSignalsForCompetitor = (competitorName) => {
    return signals.filter(signal => 
      signal.company_name.toLowerCase().includes(competitorName.toLowerCase()) ||
      competitorName.toLowerCase().includes(signal.company_name.toLowerCase())
    );
  };

  const getActiveCompetitorName = () => {
    const competitor = competitors.find(c => c.id === activeTab);
    return competitor ? competitor.name : '';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getImpactColor = (impact) => {
    switch(impact?.toLowerCase()) {
      case 'high': return 'badge-error';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-success';
      default: return 'badge-ghost';
    }
  };

  const getConfidenceColor = (confidence) => {
    switch(confidence?.toLowerCase()) {
      case 'high': return 'badge-success';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-error';
      default: return 'badge-ghost';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-100 flex items-center justify-center">
        <div className="text-center">
          <div className="loading loading-spinner loading-lg mb-4"></div>
          <p className="text-base-content/70">Loading competitor data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-base-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-error text-xl mb-4">⚠️ Error Loading Data</div>
          <p className="text-base-content/70 mb-4">{error}</p>
          <button 
            onClick={() => {
              setError(null);
              setLoading(true);
              fetchData();
            }}
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-100">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-base-content mb-4">
            Competitor Intelligence
          </h1>
          <p className="text-base-content/70">
            Monitor competitor activities, events, and signals in real-time.
          </p>
          {lastUpdated && (
            <p className="text-sm text-base-content/50 mt-2">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>

        {/* View Mode Toggle */}
        <div className="flex gap-2 mb-6">
          <button
            className={`btn ${viewMode === 'events' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setViewMode('events')}
          >
            Events ({events.length})
          </button>
          <button
            className={`btn ${viewMode === 'signals' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setViewMode('signals')}
          >
            Signals ({signals.length})
          </button>
        </div>

        {competitors.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-base-content/50 mb-4">No competitors found</div>
            <div className="text-sm text-base-content/40 mb-4">
              It looks like the database tables might not be set up yet.
            </div>
            <div className="flex gap-4 justify-center">
              <button 
                onClick={() => {
                  setLoading(true);
                  fetchData();
                }}
                className="btn btn-primary"
              >
                Refresh Data
              </button>
              <a 
                href="/api/scrape" 
                target="_blank"
                className="btn btn-secondary"
              >
                Run Scraper
              </a>
            </div>
          </div>
        ) : (
          <div className="tabs tabs-lifted tabs-lg mb-6">
            {competitors.map((competitor) => (
              <button
                key={competitor.id}
                className={`tab ${activeTab === competitor.id ? 'tab-active' : ''}`}
                onClick={() => setActiveTab(competitor.id)}
              >
                {competitor.name}
                {competitor.ticker && (
                  <span className="ml-2 opacity-60">({competitor.ticker})</span>
                )}
                <span className="badge badge-sm badge-neutral ml-2">
                  {viewMode === 'events' 
                    ? getEventsForCompetitor(competitor.id).length
                    : getSignalsForCompetitor(competitor.name).length
                  }
                </span>
              </button>
            ))}
          </div>
        )}

        {activeTab && (
          <div className="bg-base-200 rounded-lg p-6">
            <div className="overflow-x-auto">
              {viewMode === 'events' ? (
                // Events Table
                <table className="table table-zebra w-full">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Headline</th>
                      <th>Summary</th>
                      <th>Importance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getEventsForCompetitor(activeTab).map((event) => (
                      <tr key={event.id} className="hover">
                        <td className="whitespace-nowrap text-sm">
                          {formatDate(event.published_at)}
                        </td>
                        <td>
                          <a
                            href={event.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="link link-primary font-medium hover:link-accent"
                          >
                            {event.headline}
                          </a>
                        </td>
                        <td className="max-w-md">
                          <div className="line-clamp-2 text-sm text-base-content/80">
                            {event.summary || 'No summary available'}
                          </div>
                        </td>
                        <td>
                          {event.is_important ? (
                            <div className="badge badge-error text-white">
                              Important
                            </div>
                          ) : (
                            <div className="badge badge-ghost">Normal</div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                // Signals Table
                <table className="table table-zebra w-full">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Signal Type</th>
                      <th>Title</th>
                      <th>Impact</th>
                      <th>Action</th>
                      <th>Confidence</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getSignalsForCompetitor(getActiveCompetitorName()).map((signal) => (
                      <tr key={signal.id} className="hover">
                        <td className="whitespace-nowrap text-sm">
                          {formatDate(signal.detected_at)}
                        </td>
                        <td>
                          <div className="badge badge-outline">
                            {signal.signal_type}
                          </div>
                        </td>
                        <td>
                          {signal.source_url ? (
                            <a
                              href={signal.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="link link-primary font-medium hover:link-accent"
                            >
                              {signal.title}
                            </a>
                          ) : (
                            <span className="font-medium">{signal.title}</span>
                          )}
                        </td>
                        <td>
                          <div className={`badge ${getImpactColor(signal.impact)}`}>
                            {signal.impact}
                          </div>
                        </td>
                        <td className="max-w-xs">
                          <div className="line-clamp-2 text-sm">
                            {signal.action}
                          </div>
                        </td>
                        <td>
                          {signal.confidence && (
                            <div className={`badge badge-sm ${getConfidenceColor(signal.confidence)}`}>
                              {signal.confidence}
                            </div>
                          )}
                        </td>
                        <td className="text-sm text-base-content/70">
                          {signal.person && (
                            <div>👤 {signal.person}</div>
                          )}
                          {signal.amount && (
                            <div>💰 {signal.amount}</div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              
              {/* Empty State */}
              {((viewMode === 'events' && getEventsForCompetitor(activeTab).length === 0) ||
                (viewMode === 'signals' && getSignalsForCompetitor(getActiveCompetitorName()).length === 0)) && (
                <div className="text-center py-8">
                  <div className="text-base-content/50 mb-4">
                    No {viewMode} found for {competitors.find(c => c.id === activeTab)?.name}
                  </div>
                  <div className="text-sm text-base-content/40 mb-4">
                    {viewMode === 'events' 
                      ? 'Run the scraper to fetch news articles for this competitor.'
                      : 'Run the signal detector to analyze competitor signals.'
                    }
                  </div>
                  <a 
                    href="/api/scrape" 
                    target="_blank"
                    className="btn btn-primary btn-sm"
                  >
                    Run Scraper
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 