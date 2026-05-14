/**
 * Dashboard Screen
 * Shows user profile, trust score, recent transactions, voice recorder
 */
import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, FlatList, Modal, TextInput, Alert, Platform } from 'react-native';
import { Dimensions } from 'react-native';
import { Audio } from 'expo-av';
import * as SecureStore from 'expo-secure-store';
import client from '../api/client';
import AILoader from '../components/AILoader';
import { useIsFocused } from '@react-navigation/native';

const { width } = Dimensions.get('window');

interface TransactionItem {
  id: string;
  item: string;
  amount: number;
  verified?: boolean;
  timestamp?: string;
}

const DashboardScreen: React.FC<any> = ({ navigation }) => {
  const [profile, setProfile] = useState<any>(null);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [processing, setProcessing] = useState(false);
  const [confirmVisible, setConfirmVisible] = useState(false);
  const [confirmedJson, setConfirmedJson] = useState('');
  const [jobStatusLoading, setJobStatusLoading] = useState(false);
  const isFocused = useIsFocused();

  useEffect(() => {
    if (isFocused) loadData();
  }, [isFocused]);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : undefined;

      const profileRes = await client.get('/auth/profile', { headers });
      setProfile(profileRes.data);

      // Try fetching transactions for this user
      const uid = profileRes.data?.id;
      let txRes;
      try {
        txRes = await client.get(`/transactions/user/${uid}`, { headers });
      } catch (e) {
        // fallback
        txRes = await client.get('/transactions', { headers });
      }
      setTransactions(txRes.data || []);
    } catch (err) {
      console.warn('Load data error', err);
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') return Alert.alert('Permission required', 'Microphone permission is required');

      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const rec = new Audio.Recording();
      await rec.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
      await rec.startAsync();
      setRecording(rec);
    } catch (err) {
      console.warn('Record start failed', err);
    }
  };

  const stopRecordingAndUpload = async () => {
    if (!recording) return;
    setProcessing(true);
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);

      if (!uri) throw new Error('No recording URI');

      const token = await SecureStore.getItemAsync('auth_token');
      const profileStr = await SecureStore.getItemAsync('user_profile');
      const user = profileStr ? JSON.parse(profileStr) : null;

      const form = new FormData();
      const filename = uri.split('/').pop() || 'audio.mp3';
      form.append('file', { uri, name: filename, type: 'audio/mpeg' } as any);

      const res = await client.post(`/ai/process-voice?user_id=${user?.id || ''}`, form, {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      // response contains structured transaction data
      const tx = res.data?.transaction || res.data;
      setConfirmedJson(JSON.stringify(tx, null, 2));
      setConfirmVisible(true);
    } catch (err: any) {
      Alert.alert('Processing failed', err?.response?.data?.detail || err.message || 'Unknown');
    } finally {
      setProcessing(false);
    }
  };

  const saveConfirmedTransaction = async () => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const payload = JSON.parse(confirmedJson);
      await client.post('/ai/confirm-transaction', payload, { headers: token ? { Authorization: `Bearer ${token}` } : undefined });
      setConfirmVisible(false);
      Alert.alert('Saved', 'Transaction saved successfully');
      loadData();
    } catch (err: any) {
      Alert.alert('Save failed', err?.response?.data?.detail || err.message || 'Unknown');
    }
  };

  const generatePaymentLink = async (amount?: number) => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
      const payload = { merchant_id: profile?.id, amount: amount || 1000, transaction_id: Date.now().toString(), description: 'Customer payment' };
      const res = await client.post('/squad/generate-payment-link', payload, { headers });
      const link = res.data?.payment_link || res.data?.link || res.data;
      Alert.alert('Payment Link', link?.toString() || JSON.stringify(res.data));
    } catch (err: any) {
      Alert.alert('Payment link failed', err?.response?.data?.detail || err.message || 'Unknown');
    }
  };

  if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#2196F3" /></View>;

  const tierColor = (tier: string) => {
    switch ((tier || '').toLowerCase()) {
      case 'elite': return '#FFD700';
      case 'trusted': return '#4CAF50';
      default: return '#2196F3';
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.welcome}>Welcome, {profile?.name || 'Trader'}</Text>
          <Text style={styles.sub}>Trust Score: {profile?.trust_score ?? 0}</Text>
        </View>

        <View style={[styles.tierBadge, { backgroundColor: tierColor(profile?.tier) }]}>
          <Text style={styles.tierText}>{(profile?.tier || 'New').toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Virtual Account</Text>
        <Text style={styles.mono}>{profile?.virtual_account?.account_number || '—'}</Text>
        <Text style={styles.sub}>{profile?.virtual_account?.bank_name || 'No bank linked'}</Text>
        <TouchableOpacity style={styles.linkBtn} onPress={() => generatePaymentLink()}>
          <Text style={styles.linkBtnText}>Generate Payment Link</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.actionsRow}>
        <TouchableOpacity style={styles.recordBtn} onPress={recording ? stopRecordingAndUpload : startRecording}>
          <Text style={styles.recordText}>{recording ? 'Stop & Upload' : 'Record Sales'}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.ocrBtn} onPress={() => navigation.navigate('CaptureOCRScreen')}>
          <Text style={styles.ocrText}>Scan Ledger</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>Recent Transactions</Text>
      <FlatList data={transactions} keyExtractor={(i: any) => i.id || i.tx_id || Math.random().toString()} renderItem={({ item }: any) => (
        <View style={styles.txRow}>
          <View>
            <Text style={styles.txTitle}>{item.item}</Text>
            <Text style={styles.txMeta}>{item.timestamp || ''}</Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={{ color: item.verified ? '#4CAF50' : '#6B7280' }}>₦{item.amount}</Text>
            <View style={[styles.statusBadge, { backgroundColor: item.verified ? '#E6F4EA' : '#F3F4F6' }]}>
              <Text style={{ color: item.verified ? '#064E3B' : '#374151' }}>{item.verified ? 'Verified' : 'Logged'}</Text>
            </View>
          </View>
        </View>
      )} />

      <Modal visible={confirmVisible} animationType="slide" onRequestClose={() => setConfirmVisible(false)}>
        <View style={{ flex: 1, padding: 16 }}>
          <Text style={{ fontWeight: '700', fontSize: 18 }}>Confirm Transaction</Text>
          <TextInput multiline value={confirmedJson} onChangeText={setConfirmedJson} style={{ flex: 1, marginTop: 12, borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 8, padding: 12, textAlignVertical: 'top' }} />
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 12 }}>
            <TouchableOpacity style={[styles.primaryBtn, { flex: 1, marginRight: 8 }]} onPress={saveConfirmedTransaction}><Text style={{ color: '#fff' }}>Save</Text></TouchableOpacity>
            <TouchableOpacity style={[styles.secondaryBtn, { flex: 1 }]} onPress={() => setConfirmVisible(false)}><Text>Cancel</Text></TouchableOpacity>
          </View>
        </View>
      </Modal>

      <AILoader visible={processing || jobStatusLoading} message={processing ? 'Processing audio...' : 'Waiting for OCR...'} type={processing ? 'voice' : 'ocr'} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#FFFFFF' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  welcome: { fontSize: 18, fontWeight: '700' },
  sub: { color: '#6B7280' },
  tierBadge: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20 },
  tierText: { color: '#111827', fontWeight: '700' },
  card: { padding: 12, borderRadius: 8, backgroundColor: '#F9FAFB', marginBottom: 12 },
  cardTitle: { fontWeight: '700' },
  mono: { fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', marginTop: 8 },
  linkBtn: { marginTop: 10, backgroundColor: '#2196F3', padding: 10, borderRadius: 8, alignItems: 'center' },
  linkBtnText: { color: '#fff', fontWeight: '600' },
  actionsRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  recordBtn: { flex: 1, backgroundColor: '#2196F3', padding: 14, borderRadius: 8, alignItems: 'center', marginRight: 8 },
  recordText: { color: '#fff', fontWeight: '700' },
  ocrBtn: { flex: 1, backgroundColor: '#F59E0B', padding: 14, borderRadius: 8, alignItems: 'center' },
  ocrText: { color: '#111827', fontWeight: '700' },
  sectionTitle: { marginTop: 12, marginBottom: 8, fontWeight: '700' },
  txRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 1, borderColor: '#F3F4F6' },
  txTitle: { fontWeight: '600' },
  txMeta: { color: '#6B7280', fontSize: 12 },
  statusBadge: { marginTop: 6, paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  primaryBtn: { backgroundColor: '#2196F3', padding: 12, borderRadius: 8, alignItems: 'center' },
  secondaryBtn: { backgroundColor: '#fff', padding: 12, borderRadius: 8, alignItems: 'center', borderWidth: 1, borderColor: '#E5E7EB' },
});

export default DashboardScreen;
