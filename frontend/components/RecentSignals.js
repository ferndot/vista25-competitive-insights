'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/libs/supabase/client';
import Link from 'next/link';

const RecentSignals = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecentSignals = async () => {
      try {
        const supabase = createClient();
        
        const { data, error } = await supabase
          .from('signals')
          .select('*')
          .order('detected_at', { ascending: false })
          .limit(6);

        if (!error && data) {
          setSignals(data);
        }
      } catch (error) {
        console.error('Error fetching recent signals:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentSignals();
  }, []);

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
      case 'high': return 'border-red-500 bg-red-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  const getImpactIcon = (impact) => {
    switch(impact?.toLowerCase()) {
      case 'high': return '🚨';
      case 'medium': return '⚠️';
      case 'low': return 'ℹ️';
      default: return '📰';
    }
  };

  if (loading) {
    return (
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-base-100 p-6 rounded-lg border border-base-300 animate-pulse">
            <div className="h-4 bg-base-300 rounded mb-4"></div>
            <div className="h-6 bg-base-300 rounded mb-2"></div>
            <div className="h-4 bg-base-300 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (signals.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">👀</div>
        <h3 className="text-xl font-semibold mb-2">No signals detected yet</h3>
        <p className="text-base-content/70 mb-6">
          Waiting for competitive intelligence data...
        </p>
        <Link href="/competitors" className="btn btn-primary">
          View Dashboard
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {signals.map((signal) => (
          <div 
            key={signal.id} 
            className={`bg-base-100 p-6 rounded-lg border-2 ${getImpactColor(signal.impact)} hover:shadow-lg transition-shadow`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-lg">{getImpactIcon(signal.impact)}</span>
                <span className="text-xs font-medium opacity-75">
                  {signal.signal_type}
                </span>
              </div>
              <div className="text-xs opacity-60">
                {formatDate(signal.detected_at)}
              </div>
            </div>
            
            <h3 className="font-semibold text-sm mb-2 line-clamp-2">
              {signal.company_name}
            </h3>
            
            <p className="text-sm font-medium mb-3 line-clamp-2">
              {signal.title}
            </p>
            
            <p className="text-xs opacity-70 line-clamp-3 mb-4">
              {signal.action}
            </p>
            
            <div className="flex items-center justify-between">
              <div className={`badge badge-sm ${
                signal.impact === 'high' ? 'badge-error' : 
                signal.impact === 'medium' ? 'badge-warning' : 'badge-info'
              }`}>
                {signal.impact} impact
              </div>
              
              {signal.source_url && (
                <a
                  href={signal.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary hover:underline"
                >
                  Source →
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="text-center">
        <Link 
          href="/competitors" 
          className="btn btn-outline"
        >
          View All Signals
        </Link>
      </div>
    </>
  );
};

export default RecentSignals; 