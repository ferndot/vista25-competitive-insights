'use client';

import { toast } from 'react-hot-toast';
import NotificationToast from './NotificationToast';

class NotificationManager {
  constructor() {
    this.settings = {
      enableCritical: true,
      enableImportant: true,
      enableNormal: true,
      soundEnabled: true,
      persistCritical: true,
    };
  }

  // Determine priority based on impact and signal type
  determinePriority(event) {
    const { impact, signal_type, is_important } = event;
    
    // Critical events - ONLY for high impact AND critical signal types
    const criticalTypes = ['leadership', 'acquisition', 'layoffs'];
    const isCriticalType = criticalTypes.includes(signal_type);
    const isHighImpact = impact === 'high';
    
    // Only show critical alerts for truly high-impact critical events
    if (isCriticalType && isHighImpact) {
      return 'critical';
    }
    
    // Important events (notable but not urgent)
    if (impact === 'high' || impact === 'medium' || is_important) {
      return 'important';
    }
    
    // Normal events
    return 'normal';
  }

  // Show notification with appropriate styling and duration
  showNotification(event, customPriority = null) {
    const priority = customPriority || this.determinePriority(event);
    
    // Only show pop-up notifications for critical events
    if (priority !== 'critical') {
      return null;
    }
    
    // Check if critical notifications are enabled
    if (!this.isNotificationEnabled(priority)) {
      return null;
    }

    console.log('🚨 Critical Alert:', event.company_name, '-', event.title, `(${event.signal_type}, ${event.impact} impact)`);

    // Play sound for critical events
    if (this.settings.soundEnabled) {
      this.playNotificationSound();
    }

    // Determine duration based on priority
    const duration = this.getNotificationDuration(priority);
    
    // Show the notification
    const toastId = toast.custom(
      (t) => (
        <NotificationToast
          event={event}
          priority={priority}
          onDismiss={() => toast.dismiss(t.id)}
        />
      ),
      {
        duration,
        position: this.getNotificationPosition(priority),
        id: `notification-${event.id || Date.now()}`,
      }
    );
    
    return toastId;
  }

  // Show critical alert (highest priority)
  showCriticalAlert(event) {
    return this.showNotification(event, 'critical');
  }

  // Show important notification
  showImportantNotification(event) {
    return this.showNotification(event, 'important');
  }

  // Show normal notification
  showNormalNotification(event) {
    return this.showNotification(event, 'normal');
  }

  // Batch notification for multiple events
  showBatchNotification(events) {
    if (!events || events.length === 0) return;

    // Group by priority
    const grouped = events.reduce((acc, event) => {
      const priority = this.determinePriority(event);
      if (!acc[priority]) acc[priority] = [];
      acc[priority].push(event);
      return acc;
    }, {});

    // Show critical events first
    if (grouped.critical) {
      grouped.critical.forEach(event => this.showCriticalAlert(event));
    }

    // Show important events with slight delay
    if (grouped.important) {
      setTimeout(() => {
        grouped.important.forEach(event => this.showImportantNotification(event));
      }, 500);
    }

    // Show normal events with more delay
    if (grouped.normal && grouped.normal.length <= 3) {
      setTimeout(() => {
        grouped.normal.forEach(event => this.showNormalNotification(event));
      }, 1000);
    } else if (grouped.normal) {
      // For many normal events, show a summary
      setTimeout(() => {
        this.showSummaryNotification(grouped.normal);
      }, 1000);
    }
  }

  // Show summary for multiple normal events
  showSummaryNotification(events) {
    const summaryEvent = {
      title: `${events.length} new updates available`,
      summary: `Updates from ${[...new Set(events.map(e => e.company_name))].join(', ')}`,
      impact: 'low',
      detected_at: new Date().toISOString(),
    };
    
    this.showNormalNotification(summaryEvent);
  }

  // Utility methods
  isNotificationEnabled(priority) {
    const settingMap = {
      critical: 'enableCritical',
      important: 'enableImportant',
      normal: 'enableNormal',
    };
    return this.settings[settingMap[priority]];
  }

  getNotificationDuration(priority) {
    const durationMap = {
      critical: this.settings.persistCritical ? 0 : 8000, // 0 = never auto-dismiss
      important: 6000,
      normal: 4000,
    };
    return durationMap[priority];
  }

  getNotificationPosition(priority) {
    // All notifications appear at top-right for consistency
    return 'top-right';
  }

  playNotificationSound() {
    try {
      // Safari-compatible notification sound
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      // Safari requires user interaction before playing audio
      if (audioContext.state === 'suspended') {
        return;
      }
      
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.3);
      

    } catch (error) {
      console.warn('Could not play notification sound:', error);
    }
  }

  // Update settings
  updateSettings(newSettings) {
    this.settings = { ...this.settings, ...newSettings };
  }

  // Dismiss all notifications
  dismissAll() {
    toast.dismiss();
  }

  // Dismiss notifications by priority
  dismissByPriority(priority) {
    // This would require tracking toast IDs by priority
    // For now, dismiss all as react-hot-toast doesn't support filtering
    console.log(`Would dismiss all ${priority} notifications`);
  }
}

// Create singleton instance
const notificationManager = new NotificationManager();

export default notificationManager; 