/**
 * Dashboard Screen
 * Main screen showing balance, recent transactions, and quick actions
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
} from 'react-native';
import SquadButton from '../components/SquadButton';
import { getTransactions } from '../api/squad';

const { width } = Dimensions.get('window');

interface Transaction {
  id: string;
  description: string;
  amount: number;
  date: string;
  type: 'credit' | 'debit';
}

interface DashboardScreenProps {
  navigation: any;
}

const DashboardScreen: React.FC<DashboardScreenProps> = ({ navigation }) => {
  const [balance, setBalance] = useState(25500.0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      // TODO: Get merchant ID from auth context
      const merchantId = 'merchant_001';
      const data = await getTransactions(merchantId);
      if (data.transactions) {
        setTransactions(data.transactions);
      }
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTransactions();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Balance Card */}
      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>Account Balance</Text>
        <Text style={styles.balanceAmount}>₦{balance.toLocaleString()}</Text>
        <Text style={styles.lastUpdated}>Last updated: Today</Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionGrid}>
          <View style={styles.actionButton}>
            <SquadButton
              title="💳 View Account"
              onPress={() => navigation.navigate('SquadPay')}
              variant="secondary"
              size="small"
            />
          </View>
          <View style={styles.actionButton}>
            <SquadButton
              title="🎤 Voice Entry"
              onPress={() => navigation.navigate('VoiceERP')}
              variant="primary"
              size="small"
            />
          </View>
          <View style={styles.actionButton}>
            <SquadButton
              title="📸 Capture Ledger"
              onPress={() => navigation.navigate('CaptureOCR')}
              variant="primary"
              size="small"
            />
          </View>
          <View style={styles.actionButton}>
            <SquadButton
              title="💰 Payment Link"
              onPress={() => navigation.navigate('SquadPay')}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </View>

      {/* Recent Transactions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Transactions</Text>
        {transactions.length > 0 ? (
          transactions.slice(0, 5).map((transaction) => (
            <View key={transaction.id} style={styles.transactionItem}>
              <View style={styles.transactionInfo}>
                <Text style={styles.transactionDescription}>
                  {transaction.description}
                </Text>
                <Text style={styles.transactionDate}>{transaction.date}</Text>
              </View>
              <Text
                style={[
                  styles.transactionAmount,
                  {
                    color: transaction.type === 'credit' ? '#10B981' : '#EF4444',
                  },
                ]}
              >
                {transaction.type === 'credit' ? '+' : '-'}₦
                {transaction.amount.toLocaleString()}
              </Text>
            </View>
          ))
        ) : (
          <Text style={styles.noTransactions}>No transactions yet</Text>
        )}
      </View>

      {/* Intelligent Economy Banner */}
      <View style={styles.bannerCard}>
        <Text style={styles.bannerTitle}>🚀 Intelligent Economy</Text>
        <Text style={styles.bannerText}>
          Digitize your informal business with SmartSync. Voice-ERP, OCR ledger reading,
          and Squad payments in one app.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  balanceCard: {
    backgroundColor: '#1F2937',
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 20,
    paddingVertical: 24,
    paddingHorizontal: 20,
    borderRadius: 12,
  },
  balanceLabel: {
    fontSize: 14,
    color: '#D1D5DB',
    marginBottom: 8,
  },
  balanceAmount: {
    fontSize: 32,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  lastUpdated: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  section: {
    paddingHorizontal: 16,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  actionButton: {
    width: (width - 48) / 2,
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  transactionInfo: {
    flex: 1,
  },
  transactionDescription: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1F2937',
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 12,
    color: '#6B7280',
  },
  transactionAmount: {
    fontSize: 14,
    fontWeight: '600',
  },
  noTransactions: {
    textAlign: 'center',
    color: '#9CA3AF',
    paddingVertical: 20,
  },
  bannerCard: {
    backgroundColor: '#DBEAFE',
    marginHorizontal: 16,
    marginBottom: 24,
    paddingVertical: 16,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
  },
  bannerTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E40AF',
    marginBottom: 8,
  },
  bannerText: {
    fontSize: 12,
    color: '#1E40AF',
    lineHeight: 18,
  },
});

export default DashboardScreen;
