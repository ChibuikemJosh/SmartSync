/**
 * AILoader Component
 * Loading indicator with animated status messages for AI processing
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  ActivityIndicator,
  Text,
  StyleSheet,
  Animated,
  ViewStyle,
} from 'react-native';

export interface AILoaderProps {
  visible: boolean;
  message?: string;
  type?: 'voice' | 'ocr' | 'payment';
  progress?: number;
  style?: ViewStyle;
}

const AILoader: React.FC<AILoaderProps> = ({
  visible,
  message = 'Processing...',
  type = 'voice',
  progress,
  style,
}) => {
  const [dotAnimation] = useState(new Animated.Value(0));
  const [displayedDots, setDisplayedDots] = useState('');

  useEffect(() => {
    if (!visible) return;

    const interval = setInterval(() => {
      setDisplayedDots((prev) => (prev.length < 3 ? prev + '.' : ''));
    }, 500);

    return () => clearInterval(interval);
  }, [visible]);

  if (!visible) return null;

  const getTypeColor = () => {
    switch (type) {
      case 'voice':
        return '#3B82F6';
      case 'ocr':
        return '#10B981';
      case 'payment':
        return '#F59E0B';
      default:
        return '#6366F1';
    }
  };

  const getTypeMessage = () => {
    switch (type) {
      case 'voice':
        return 'Processing voice transaction';
      case 'ocr':
        return 'Reading ledger image';
      case 'payment':
        return 'Processing payment';
      default:
        return 'Processing';
    }
  };

  const typeColor = getTypeColor();
  const displayMessage = message || getTypeMessage();

  return (
    <View style={[styles.container, style]}>
      <View style={styles.loaderCard}>
        <View style={[styles.loaderIcon, { borderColor: typeColor }]}>
          <ActivityIndicator size="large" color={typeColor} />
        </View>

        <Text style={styles.message}>
          {displayMessage}
          {displayedDots}
        </Text>

        {progress !== undefined && (
          <View style={styles.progressContainer}>
            <View
              style={[
                styles.progressBar,
                { width: `${Math.min(progress, 100)}%`, backgroundColor: typeColor },
              ]}
            />
          </View>
        )}

        <Text style={styles.subMessage}>
          {type === 'voice' && 'Converting speech to transaction data...'}
          {type === 'ocr' && 'Extracting data from image...'}
          {type === 'payment' && 'Initiating payment link...'}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    zIndex: 1000,
  },
  loaderCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingVertical: 32,
    paddingHorizontal: 24,
    alignItems: 'center',
    width: '80%',
    maxWidth: 320,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
  loaderIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    marginBottom: 20,
  },
  message: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 12,
  },
  progressContainer: {
    width: '100%',
    height: 4,
    backgroundColor: '#E5E7EB',
    borderRadius: 2,
    marginVertical: 12,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    borderRadius: 2,
  },
  subMessage: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
  },
});

export default AILoader;
