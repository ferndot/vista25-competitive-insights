'use client';

import { useState, useEffect } from 'react';

const DataUpdateIndicator = ({ onRefresh, lastUpdated }) => {
  const [hasNewData, setHasNewData] = useState(false);
  const [newSignalsCount, setNewSignalsCount] = useState(0);

  useEffect(() => {
    // Listen for new data events from the global notification provider
    const handleNewData = (event) => {
      if (event.detail && lastUpdated && new Date(event.detail.detected_at) > lastUpdated) {
        setHasNewData(true);
        setNewSignalsCount(prev => prev + 1);
      }
    };

    window.addEventListener('newSignalDetected', handleNewData);
    
    return () => {
      window.removeEventListener('newSignalDetected', handleNewData);
    };
  }, [lastUpdated]);

  // Reset indicator when data is refreshed
  useEffect(() => {
    if (lastUpdated) {
      setHasNewData(false);
      setNewSignalsCount(0);
    }
  }, [lastUpdated]);

  const handleRefresh = () => {
    setHasNewData(false);
    setNewSignalsCount(0);
    onRefresh?.();
  };

  if (!hasNewData) return null;

  return (
    <div className="flex items-center gap-2 ml-4">
      {/* Pulsing indicator dot */}
      <div className="relative">
        <div className="w-3 h-3 bg-green-500 rounded-full animate-ping absolute"></div>
        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
      </div>
      
      {/* New data message */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-green-600 font-medium">
          {newSignalsCount} new signal{newSignalsCount !== 1 ? 's' : ''} available
        </span>
        
        <button
          onClick={handleRefresh}
          className="btn btn-xs btn-success gap-1 animate-pulse"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Update Now
        </button>
      </div>
    </div>
  );
};

export default DataUpdateIndicator; 