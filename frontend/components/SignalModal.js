'use client';

const SignalModal = ({ signal, isOpen, onClose }) => {
  if (!isOpen || !signal) return null;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
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

  const getSignalTypeIcon = (signalType) => {
    const iconMap = {
      'leadership': '👤',
      'funding': '💰',
      'acquisition': '🤝',
      'layoffs': '📉',
      'expansion': '📈',
      'partnership': '🤝',
      'default': '📰'
    };
    return iconMap[signalType] || iconMap.default;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-base-100 rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-base-100 border-b border-base-300 p-6 pb-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{getSignalTypeIcon(signal.signal_type)}</span>
                <div>
                  <h2 className="text-xl font-bold">{signal.company_name}</h2>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="badge badge-outline">
                      {signal.signal_type}
                    </div>
                    <div className={`badge ${getImpactColor(signal.impact)}`}>
                      {signal.impact} impact
                    </div>
                    {signal.confidence && (
                      <div className={`badge badge-sm ${getConfidenceColor(signal.confidence)}`}>
                        {signal.confidence} confidence
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <button
              onClick={onClose}
              className="btn btn-ghost btn-sm btn-circle"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Title */}
          <div className="mb-6">
            <h3 className="font-semibold text-lg mb-2">Signal Details</h3>
            <p className="text-base-content font-medium">
              {signal.title}
            </p>
          </div>

          {/* Action Required */}
          <div className="mb-6">
            <h3 className="font-semibold text-lg mb-2">Recommended Action</h3>
            <p className="text-base-content">
              {signal.action}
            </p>
          </div>

          {/* Metadata */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="font-semibold mb-3">Event Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="opacity-70">Detected:</span>
                  <span>{formatDate(signal.detected_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-70">Source:</span>
                  <span>{signal.source || 'Unknown'}</span>
                </div>
                {signal.person && (
                  <div className="flex justify-between">
                    <span className="opacity-70">Key Person:</span>
                    <span>👤 {signal.person}</span>
                  </div>
                )}
                {signal.amount && (
                  <div className="flex justify-between">
                    <span className="opacity-70">Amount:</span>
                    <span>💰 {signal.amount}</span>
                  </div>
                )}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-3">Assessment</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="opacity-70">Impact Level:</span>
                  <div className={`badge badge-sm ${getImpactColor(signal.impact)}`}>
                    {signal.impact}
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-70">Confidence:</span>
                  <div className={`badge badge-sm ${getConfidenceColor(signal.confidence)}`}>
                    {signal.confidence || 'Not assessed'}
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="opacity-70">Signal Type:</span>
                  <span>{signal.signal_type}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Source Link */}
          {signal.source_url && (
            <div className="mb-6">
              <h4 className="font-semibold mb-2">Source</h4>
              <a
                href={signal.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline btn-sm gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Read Full Article
              </a>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-base-100 border-t border-base-300 p-6 pt-4">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="btn btn-primary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignalModal; 