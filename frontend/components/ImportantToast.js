const ImportantToast = ({ event, onDismiss }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text) return 'No summary available';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="alert alert-error max-w-md shadow-lg">
      <div className="flex-1">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="font-bold text-sm">🚨 Important Update</div>
            <div className="text-xs opacity-90 mb-2">
              {formatDate(event.published_at)}
            </div>
            <div className="font-medium text-sm mb-1">
              {event.headline}
            </div>
            <div className="text-xs opacity-80">
              {truncateText(event.summary)}
            </div>
            {event.url && (
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs underline opacity-90 hover:opacity-100 mt-1 inline-block"
              >
                Read more →
              </a>
            )}
          </div>
          <button
            onClick={onDismiss}
            className="btn btn-ghost btn-sm btn-circle ml-2"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImportantToast; 