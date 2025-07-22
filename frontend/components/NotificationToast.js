const NotificationToast = ({ event, priority = 'normal', onDismiss }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text, maxLength = 120) => {
    if (!text) return 'No summary available';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const getNotificationStyle = (priority, impact) => {
    // Critical notifications (high impact + urgent events)
    if (priority === 'critical' || impact === 'high') {
      return {
        alertClass: 'alert alert-error border-2 border-red-500 bg-red-50 text-red-900 shadow-xl',
        iconClass: 'text-red-600',
        icon: '🚨',
        titlePrefix: 'CRITICAL ALERT'
      };
    }
    
    // Important notifications (medium impact)
    if (priority === 'important' || impact === 'medium') {
      return {
        alertClass: 'alert alert-warning border-2 border-yellow-500 bg-yellow-50 text-yellow-900 shadow-lg',
        iconClass: 'text-yellow-600',
        icon: '⚠️',
        titlePrefix: 'Important Update'
      };
    }
    
    // Normal notifications (low impact or general updates)
    return {
      alertClass: 'alert alert-info border-2 border-blue-500 bg-blue-50 text-blue-900 shadow-md',
      iconClass: 'text-blue-600',
      icon: 'ℹ️',
      titlePrefix: 'New Update'
    };
  };

  const style = getNotificationStyle(priority, event.impact);

  const getEventTypeIcon = (signalType) => {
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
    <div className={`${style.alertClass} max-w-md relative overflow-hidden`}>
      {/* Animated border for critical events */}
      {priority === 'critical' && (
        <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-red-600 to-red-500 opacity-20 animate-pulse"></div>
      )}
      
      <div className="flex-1 relative z-10">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            {/* Header with priority and time */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-lg">{style.icon}</span>
                <div className="font-bold text-sm">{style.titlePrefix}</div>
                {event.signal_type && (
                  <span className="text-xs opacity-75">
                    {getEventTypeIcon(event.signal_type)} {event.signal_type}
                  </span>
                )}
              </div>
              <div className="text-xs opacity-75">
                {formatDate(event.detected_at || event.published_at)}
              </div>
            </div>

            {/* Company name */}
            <div className="text-xs font-semibold opacity-90 mb-1">
              {event.company_name}
            </div>

            {/* Event title/headline */}
            <div className="font-medium text-sm mb-2">
              {event.title || event.headline}
            </div>

            {/* Summary/Action */}
            <div className="text-xs opacity-80 mb-2">
              {truncateText(event.action || event.summary)}
            </div>

            {/* Impact badge and confidence */}
            <div className="flex items-center gap-2 mb-2">
              {event.impact && (
                <div className={`badge badge-sm ${getImpactBadgeClass(event.impact)}`}>
                  {event.impact} impact
                </div>
              )}
              {event.confidence && (
                <div className="badge badge-sm badge-outline">
                  {event.confidence} confidence
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2 mt-3">
              {event.source_url && (
                <a
                  href={event.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs underline opacity-90 hover:opacity-100"
                >
                  Read more →
                </a>
              )}
              {priority === 'critical' && (
                <button className="btn btn-xs btn-outline">
                  Take Action
                </button>
              )}
            </div>
          </div>

          {/* Close button */}
          <button
            onClick={onDismiss}
            className="btn btn-ghost btn-sm btn-circle ml-3 opacity-70 hover:opacity-100"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
};

const getImpactBadgeClass = (impact) => {
  switch(impact?.toLowerCase()) {
    case 'high': return 'badge-error';
    case 'medium': return 'badge-warning';
    case 'low': return 'badge-success';
    default: return 'badge-ghost';
  }
};

export default NotificationToast; 