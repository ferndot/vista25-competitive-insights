'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/libs/supabase/client';
import NewDataBadge from '@/components/NewDataBadge';
import SignalModal from '@/components/SignalModal';

export default function CompetitorsPage() {
  const [signals, setSignals] = useState([]);
  const [filteredSignals, setFilteredSignals] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState('all');
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [showModal, setShowModal] = useState(false);

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
    
    // Note: Real-time notifications are now handled globally by GlobalNotificationProvider
    
    return () => {
      clearInterval(interval);
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
          <div className="flex gap-4 items-center mt-4 flex-wrap">
            <div className="flex items-center gap-4">
              {lastUpdated && (
                <p className="text-sm text-base-content/50">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </p>
              )}
              <div className="badge badge-info">
                {filteredSignals.length} Signals
              </div>
              
              {/* Simple new data indicator */}
              <NewDataBadge 
                onRefresh={fetchData} 
                lastUpdated={lastUpdated} 
              />
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
                    <th>Company</th>
                    <th>Source</th>
                    <th>Signal Type</th>
                    <th>Title</th>
                    <th>Impact</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSignals.map((signal) => (
                    <tr 
                      key={signal.id} 
                      className="hover cursor-pointer"
                      onClick={() => {
                        setSelectedSignal(signal);
                        setShowModal(true);
                      }}
                    >
                      <td className="font-medium">
                        {signal.company_name}
                      </td>
                      <td>
                        <div className="badge badge-ghost text-xs">
                          {signal.source || 'Unknown'}
                        </div>
                      </td>
                      <td>
                        <div className="badge badge-outline">
                          {signal.signal_type}
                        </div>
                      </td>
                      <td className="max-w-md">
                        <div className="font-medium truncate">
                          {signal.title}
                        </div>
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

      {/* Signal Details Modal */}
      <SignalModal
        signal={selectedSignal}
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedSignal(null);
        }}
      />
    </div>
  );
} 