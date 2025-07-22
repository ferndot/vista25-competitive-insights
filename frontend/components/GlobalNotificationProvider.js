'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/libs/supabase/client';
import notificationManager from './NotificationManager';
import NotificationSettings from './NotificationSettings';

const GlobalNotificationProvider = ({ children }) => {
  const [showNotificationSettings, setShowNotificationSettings] = useState(false);

  useEffect(() => {
    // Set up global real-time subscription for notifications
    const supabase = createClient();
    const channel = supabase.channel('global:signals');
    
    channel.on(
      'postgres_changes',
      { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'signals'
      },
      (payload) => {
        const signal = payload.new;
        
        console.log('🔔 New signal:', signal.company_name, '-', signal.signal_type, `(${signal.impact} impact)`);
        
        // Show notification using enhanced manager (only for high-impact critical events)
        notificationManager.showNotification(signal);
        
        // Broadcast event for other components to listen to
        window.dispatchEvent(new CustomEvent('newSignalDetected', {
          detail: signal,
          bubbles: true
        }));
      }
    ).subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        console.log('✅ Real-time notifications active');
      } else if (status === 'CLOSED') {
        console.log('❌ Real-time disconnected');
      }
    });

    // Cleanup on unmount
    return () => {
      if (channel) {
        supabase.removeChannel(channel);
      }
    };
  }, []);



    return (
    <>
      {children}

      {/* Notification Settings Modal (accessible via keyboard shortcut or other means if needed) */}
      <NotificationSettings
        isOpen={showNotificationSettings}
        onClose={() => setShowNotificationSettings(false)}
      />
    </>
  );
};

export default GlobalNotificationProvider; 