/**
 * VoiceERP Screen
 * Large, accessible microphone button for recording voice transactions
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import { Audio } from 'expo-av';
import SquadButton from '../components/SquadButton';
import AILoader from '../components/AILoader';
import { processVoice } from '../api/ai';

interface VoiceERPScreenProps {
  navigation: any;
}

interface ProcessedTransaction {
  type: string;
  amount: number;
  customer: string;
  items: string[];
  timestamp: string;
}

const VoiceERPScreen: React.FC<VoiceERPScreenProps> = ({ navigation }) => {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [processedData, setProcessedData] = useState<ProcessedTransaction | null>(null);

  useEffect(() => {
    initializeAudio();
    return () => {
      cleanupAudio();
    };
  }, []);

  useEffect(() => {
    if (!isRecording) return;

    const interval = setInterval(() => {
      setRecordingTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [isRecording]);

  const initializeAudio = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
    } catch (error) {
      console.error('Audio initialization error:', error);
    }
  };

  const cleanupAudio = async () => {
    if (recording) {
      try {
        await recording.stopAndUnloadAsync();
      } catch {
        // ignore
      }
    }
  };

  const startRecording = async () => {
    try {
      const newRecording = new Audio.Recording();
      await newRecording.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await newRecording.startAsync();
      setRecording(newRecording);
      setIsRecording(true);
      setRecordingTime(0);
    } catch (error) {
      Alert.alert('Error', 'Failed to start recording');
      console.error('Recording error:', error);
    }
  };

  const stopRecording = async () => {
    try {
      if (!recording) return;

      await recording.stopAndUnloadAsync();
      setIsRecording(false);

      const uri = recording.getURI();
      if (uri) {
        await processRecording(uri);
      }

      setRecording(null);
    } catch (error) {
      Alert.alert('Error', 'Failed to stop recording');
      console.error('Stop recording error:', error);
    }
  };

  const processRecording = async (uri: string) => {
    try {
      setProcessing(true);
      const response = await processVoice(uri);

      if (response.status === 'success') {
        setProcessedData(response.transaction_data as ProcessedTransaction);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to process voice recording');
      console.error('Processing error:', error);
    } finally {
      setProcessing(false);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSaveTransaction = () => {
    // TODO: Save processed transaction to database
    Alert.alert('Success', 'Transaction saved successfully');
    setProcessedData(null);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🎤 Voice Transaction Entry</Text>
        <Text style={styles.subtitle}>
          Record your transaction and let AI convert it to data
        </Text>
      </View>

      {/* Recording Interface */}
      <View style={styles.recordingCard}>
        <View style={styles.recordingDisplay}>
          {isRecording && (
            <View style={styles.recordingIndicator}>
              <View style={styles.recordingPulse} />
              <Text style={styles.recordingLabel}>Recording</Text>
            </View>
          )}
          <Text style={styles.recordingTime}>{formatTime(recordingTime)}</Text>
        </View>

        {/* Large Microphone Button */}
        <TouchableOpacity
          style={[
            styles.micButton,
            isRecording && styles.micButton_recording,
          ]}
          onPress={isRecording ? stopRecording : startRecording}
          disabled={processing}
        >
          <Text style={styles.micButtonText}>
            {isRecording ? '⏹️' : '🎤'}
          </Text>
        </TouchableOpacity>

        <Text style={styles.micButtonLabel}>
          {isRecording ? 'Tap to Stop' : 'Tap to Start Recording'}
        </Text>
      </View>

      {/* Processed Transaction Display */}
      {processedData && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>✓ Transaction Captured</Text>

          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>Transaction Type</Text>
            <Text style={styles.resultValue}>{processedData.type}</Text>
          </View>

          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>Amount</Text>
            <Text style={styles.resultValue}>₦{processedData.amount.toLocaleString()}</Text>
          </View>

          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>Customer</Text>
            <Text style={styles.resultValue}>{processedData.customer}</Text>
          </View>

          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>Items</Text>
            {processedData.items.map((item, index) => (
              <Text key={index} style={styles.resultList}>
                • {item}
              </Text>
            ))}
          </View>

          <View style={styles.resultActions}>
            <SquadButton
              title="Save Transaction"
              onPress={handleSaveTransaction}
              variant="primary"
            />
            <SquadButton
              title="Discard"
              onPress={() => setProcessedData(null)}
              variant="secondary"
            />
          </View>
        </View>
      )}

      {/* Tips Section */}
      <View style={styles.tipsCard}>
        <Text style={styles.tipsTitle}>💡 Tips for Best Results</Text>
        <Text style={styles.tipItem}>• Speak clearly and naturally</Text>
        <Text style={styles.tipItem}>• Include customer name and amount</Text>
        <Text style={styles.tipItem}>• List all items sold or purchased</Text>
        <Text style={styles.tipItem}>• Minimum 5 seconds per recording</Text>
      </View>

      <AILoader
        visible={processing}
        message="Processing your voice transaction"
        type="voice"
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
  },
  recordingCard: {
    marginHorizontal: 16,
    marginTop: 20,
    backgroundColor: '#FFFFFF',
    paddingVertical: 32,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
  },
  recordingDisplay: {
    marginBottom: 24,
    alignItems: 'center',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  recordingPulse: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#EF4444',
    marginRight: 8,
    animation: 'pulse' as any,
  },
  recordingLabel: {
    fontSize: 12,
    color: '#EF4444',
    fontWeight: '600',
  },
  recordingTime: {
    fontSize: 36,
    fontWeight: '700',
    color: '#1F2937',
    fontVariant: ['tabular-nums'],
  },
  micButton: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  micButton_recording: {
    backgroundColor: '#EF4444',
  },
  micButtonText: {
    fontSize: 60,
  },
  micButtonLabel: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '600',
  },
  resultCard: {
    marginHorizontal: 16,
    marginTop: 20,
    backgroundColor: '#F0FDF4',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#10B981',
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#047857',
    marginBottom: 12,
  },
  resultItem: {
    marginBottom: 12,
  },
  resultLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  resultValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  resultList: {
    fontSize: 13,
    color: '#1F2937',
    marginTop: 4,
  },
  resultActions: {
    marginTop: 16,
    gap: 8,
  },
  tipsCard: {
    marginHorizontal: 16,
    marginTop: 20,
    marginBottom: 20,
    backgroundColor: '#FEF3C7',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  tipsTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#92400E',
    marginBottom: 8,
  },
  tipItem: {
    fontSize: 12,
    color: '#92400E',
    marginBottom: 4,
  },
});

export default VoiceERPScreen;
