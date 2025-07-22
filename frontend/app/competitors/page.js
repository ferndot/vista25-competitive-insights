'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/libs/supabase/client';
import toast from 'react-hot-toast';

export default function CompetitorsPage() {
  const [signals, setSignals] = useState([]);
  const [filteredSignals, setFilteredSignals] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState('all');
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      console.log('Fetching signals from Supabase...');
      
      // Create Supabase client inside function to avoid build-time errors
      const supabase = createClient();
      
      // Fetch all signals
      const { data: signalsData, error: signalsError } = await supabase
        .from('signals')
        .select('*')
        .order('detected_at', { ascending: false });

      if (signalsError) {
        console.error('Error fetching signals:', signalsError);
        setError('Failed to fetch signals: ' + signalsError.message);
        setLoading(false);
        return;
      }

      console.log('Signals fetched:', signalsData);

      setSignals(signalsData || []);
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
    
    // Set up realtime subscription for new signals
    const supabase = createClient();
    const channel = supabase.channel('public:signals');
    
    channel.on(
      'postgres_changes',
      { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'signals'
      },
      (payload) => {
        const signal = payload.new;
        
        // Show toast for new signals
        toast.success(`New signal detected: ${signal.title}`, {
          duration: 5000,
          position: 'top-right',
        });
        
        // Refresh data to show the new signal
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

  // Filter signals based on selected company
  useEffect(() => {
    if (selectedCompany === 'all') {
      setFilteredSignals(signals);
    } else {
      setFilteredSignals(signals.filter(signal => 
        signal.company_name === selectedCompany
      ));
    }
  }, [signals, selectedCompany]);

  // Get unique company names from signals
  const getUniqueCompanies = () => {
    const companies = [...new Set(signals.map(signal => signal.company_name))];
    return companies.sort();
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
          <p className="text-base-content/70">Loading competitive signals...</p>
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
            Competitive Signals Dashboard
          </h1>
          <p className="text-base-content/70">
            Real-time competitive intelligence and market signals.
          </p>
          <div className="flex gap-4 items-center mt-4">
            {lastUpdated && (
              <p className="text-sm text-base-content/50">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            )}
            <div className="badge badge-info">
              {filteredSignals.length} Signals
            </div>
          </div>
        </div>

        {/* Company Filter */}
        {signals.length > 0 && (
          <div className="mb-6">
            <div className="flex gap-2 flex-wrap">
              <button
                className={`btn btn-sm ${selectedCompany === 'all' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setSelectedCompany('all')}
              >
                All Companies ({signals.length})
              </button>
              {getUniqueCompanies().map((company) => (
                <button
                  key={company}
                  className={`btn btn-sm ${selectedCompany === company ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setSelectedCompany(company)}
                >
                  {company} ({signals.filter(s => s.company_name === company).length})
                </button>
              ))}
            </div>
          </div>
        )}

        {signals.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-base-content/50 mb-4">No signals found</div>
            <div className="text-sm text-base-content/40 mb-4">
              Start pushing competitive intelligence data to see signals here.
            </div>
            <button 
              onClick={() => {
                setLoading(true);
                fetchData();
              }}
              className="btn btn-primary"
            >
              Refresh Data
            </button>
          </div>
        ) : (
          <div className="bg-base-200 rounded-lg p-6">
            <div className="overflow-x-auto">
              <table className="table table-zebra w-full">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Company</th>
                    <th>Signal Type</th>
                    <th>Title</th>
                    <th>Impact</th>
                    <th>Action</th>
                    <th>Confidence</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSignals.map((signal) => (
                    <tr key={signal.id} className="hover">
                      <td className="whitespace-nowrap text-sm">
                        {formatDate(signal.detected_at)}
                      </td>
                      <td className="font-medium">
                        {signal.company_name}
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
              
              {filteredSignals.length === 0 && signals.length > 0 && (
                <div className="text-center py-8">
                  <div className="text-base-content/50 mb-4">
                    No signals found for {selectedCompany}
                  </div>
                  <button 
                    onClick={() => setSelectedCompany('all')}
                    className="btn btn-outline btn-sm"
                  >
                    Show All Signals
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 