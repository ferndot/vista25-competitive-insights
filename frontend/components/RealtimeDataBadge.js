'use client';

import { useState, useEffect } from 'react';

const RealtimeDataBadge = ({ 
  onRefresh, 
  lastUpdated, 
  tableName = 'signals',
  compact = false 
}) => {
  const [hasNewData, setHasNewData] = useState(false);
  const [newItemsCount, setNewItemsCount] = useState(0);

  useEffect(() => {
    // Listen for new data events from the global notification provider
    const handleNewData = (event) => {
      if (event.detail && lastUpdated) {
        const itemDate = new Date(event.detail.detected_at || event.detail.created_at);
        if (itemDate > lastUpdated) {
          setHasNewData(true);
          setNewItemsCount(prev => prev + 1);
        }
      }
    };

    window.addEventListener('newSignalDetected', handleNewData);
    
    return () => {
      window.removeEventListener('newSignalDetected', handleNewData);
    };
  }, [lastUpdated, tableName]);

  // Reset indicator when data is refreshed
  useEffect(() => {
    if (lastUpdated) {
      setHasNewData(false);
      setNewItemsCount(0);
    }
  }, [lastUpdated]);

  const handleRefresh = () => {
    setHasNewData(false);
    setNewItemsCount(0);
    onRefresh?.();
  };

  if (!hasNewData) return null;

  if (compact) {
    return (
      <div className="relative inline-flex items-center">
        {/* Pulsing dot indicator */}
        <div className="absolute -top-1 -right-1 flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
        </div>
        
        {/* Tooltip with refresh action */}
        <div className="tooltip tooltip-bottom" data-tip={`${newItemsCount} new item${newItemsCount !== 1 ? 's' : ''} - Click to refresh`}>
          <button
            onClick={handleRefresh}
            className="btn btn-ghost btn-xs p-1"
            aria-label="New data available"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1 bg-green-50 border border-green-200 rounded-full">
      {/* Pulsing indicator dot */}
      <div className="relative">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-ping absolute"></div>
        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
      </div>
      
      {/* New data message */}
      <span className="text-xs text-green-700 font-medium">
        {newItemsCount} new
      </span>
      
      <button
        onClick={handleRefresh}
        className="text-xs text-green-800 hover:text-green-900 underline font-medium"
      >
        Refresh
      </button>
    </div>
  );
};

export default RealtimeDataBadge; 