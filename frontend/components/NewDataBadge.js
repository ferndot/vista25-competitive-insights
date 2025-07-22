'use client';

import { useState, useEffect } from 'react';

const NewDataBadge = ({ onRefresh, lastUpdated }) => {
  const [hasNewData, setHasNewData] = useState(false);
  const [newItemsCount, setNewItemsCount] = useState(0);

  useEffect(() => {
    // Listen for new data events from the global notification provider
    const handleNewData = (event) => {
      if (event.detail && lastUpdated && new Date(event.detail.detected_at) > lastUpdated) {
        setHasNewData(true);
        setNewItemsCount(prev => prev + 1);
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
      setNewItemsCount(0);
    }
  }, [lastUpdated]);

  const handleRefresh = () => {
    setHasNewData(false);
    setNewItemsCount(0);
    onRefresh?.();
  };

  if (!hasNewData) return null;

  return (
    <button
      onClick={handleRefresh}
      className="badge badge-success badge-sm ml-2 animate-pulse cursor-pointer hover:badge-warning"
      title={`${newItemsCount} new signal${newItemsCount !== 1 ? 's' : ''} available - Click to refresh`}
    >
      NEW DATA
    </button>
  );
};

export default NewDataBadge; 