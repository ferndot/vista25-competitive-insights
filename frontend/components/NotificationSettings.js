'use client';

import { useState, useEffect } from 'react';
import notificationManager from './NotificationManager';

const NotificationSettings = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState(notificationManager.settings);

  useEffect(() => {
    setSettings(notificationManager.settings);
  }, [isOpen]);

  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    notificationManager.updateSettings(newSettings);
  };

  const testNotification = (priority) => {
    const testEvent = {
      id: Date.now(),
      company_name: 'Test Company',
      title: `Test ${priority} notification`,
      action: 'This is a test notification to preview the styling and behavior.',
      impact: priority === 'critical' ? 'high' : priority === 'important' ? 'medium' : 'low',
      signal_type: priority === 'critical' ? 'leadership' : 'funding',
      confidence: 'high',
      detected_at: new Date().toISOString(),
    };
    
    notificationManager.showNotification(testEvent, priority);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-screen overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Notification Settings</h2>
          <button
            onClick={onClose}
            className="btn btn-ghost btn-sm btn-circle"
          >
            ✕
          </button>
        </div>

        {/* Notification Types */}
        <div className="space-y-4 mb-6">
          <h3 className="font-semibold text-lg">Notification Types</h3>
          
          {/* Critical Notifications */}
          <div className="form-control">
            <label className="label cursor-pointer">
              <div>
                <span className="label-text font-medium">🚨 Critical Alert Pop-ups</span>
                <p className="text-sm opacity-70">Show pop-ups ONLY for HIGH IMPACT leadership changes, acquisitions, and layoffs</p>
              </div>
              <input
                type="checkbox"
                className="checkbox checkbox-error"
                checked={settings.enableCritical}
                onChange={(e) => handleSettingChange('enableCritical', e.target.checked)}
              />
            </label>
          </div>

          {/* Info about other updates */}
          <div className="p-4 bg-base-200 rounded-lg">
            <p className="text-sm opacity-70 mb-2">
              <strong>Non-critical updates</strong> (funding, partnerships, general news) don't show pop-ups but appear as "NEW DATA" badges in the dashboard.
            </p>
            <div className="flex items-center gap-2">
              <span className="badge badge-success badge-sm animate-pulse">NEW DATA</span>
              <span className="text-xs opacity-60">← Like this when new data is available</span>
            </div>
          </div>
        </div>

        {/* Sound Settings */}
        <div className="space-y-4 mb-6">
          <h3 className="font-semibold text-lg">Sound & Behavior</h3>
          
          <div className="form-control">
            <label className="label cursor-pointer">
              <span className="label-text">🔊 Sound for critical alerts</span>
              <input
                type="checkbox"
                className="checkbox"
                checked={settings.soundEnabled}
                onChange={(e) => handleSettingChange('soundEnabled', e.target.checked)}
              />
            </label>
          </div>

          <div className="form-control">
            <label className="label cursor-pointer">
              <div>
                <span className="label-text">📌 Persist critical notifications</span>
                <p className="text-sm opacity-70">Critical alerts won't auto-dismiss</p>
              </div>
              <input
                type="checkbox"
                className="checkbox"
                checked={settings.persistCritical}
                onChange={(e) => handleSettingChange('persistCritical', e.target.checked)}
              />
            </label>
          </div>
        </div>

        {/* Test Notifications */}
        <div className="space-y-4 mb-6">
          <h3 className="font-semibold text-lg">Test Notifications</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => testNotification('critical')}
              className="btn btn-error btn-sm"
            >
              Test Critical
            </button>
            <button
              onClick={() => testNotification('important')}
              className="btn btn-warning btn-sm"
            >
              Test Important
            </button>
            <button
              onClick={() => testNotification('normal')}
              className="btn btn-info btn-sm"
            >
              Test Normal
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => notificationManager.dismissAll()}
            className="btn btn-outline btn-sm flex-1"
          >
            Clear All Notifications
          </button>
          <button
            onClick={onClose}
            className="btn btn-primary btn-sm flex-1"
          >
            Done
          </button>
        </div>

        {/* Info */}
        <div className="mt-4 p-3 bg-base-200 rounded-lg">
          <p className="text-xs opacity-70">
            💡 Only critical alerts show as pop-up notifications at the top-right. 
            All other updates appear as "NEW DATA" badges in the dashboard.
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettings; 