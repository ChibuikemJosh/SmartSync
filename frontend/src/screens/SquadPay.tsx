/**
 * SquadPay Screen
 * Interface to generate payment links and view virtual account details
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  TextInput,
  TabItem,
} from 'react-native';
import SquadButton from '../components/SquadButton';
import AILoader from '../components/AILoader';
import { createVirtualAccount, generatePaymentLink } from '../api/squad';

interface SquadPayScreenProps {
  navigation: any;
}

const SquadPayScreen: React.FC<SquadPayScreenProps> = ({ navigation }) => {
  const [activeTab, setActiveTab] = useState<'account' | 'payment'>('account');
  const [loading, setLoading] = useState(false);

  // Virtual Account State
  const [accountCreated, setAccountCreated] = useState(false);
  const [virtualAccount, setVirtualAccount] = useState({
    accountNumber: '0123456789',
    bankName: 'Providus Bank',
    businessName: 'SmartSync Business',
    merchantId: 'merchant_001',
  });

  // Payment Link State
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [paymentLink, setPaymentLink] = useState<string | null>(null);

  const handleCreateVirtualAccount = async () => {
    try {
      setLoading(true);
      const response = await createVirtualAccount({
        merchant_id: 'merchant_001',
        business_name: 'SmartSync Business',
        email: 'business@smartsync.com',
        phone: '+234XX0000000',
      });

      if (response.status === 'success') {
        setVirtualAccount({
          accountNumber: response.account_number,
          bankName: response.bank_name,
          businessName: response.business_name,
          merchantId: response.merchant_id,
        });
        setAccountCreated(true);
        Alert.alert('Success', 'Virtual account created successfully');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to create virtual account');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePaymentLink = async () => {
    if (!amount || !description) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      const response = await generatePaymentLink({
        merchant_id: 'merchant_001',
        amount: parseFloat(amount),
        transaction_id: `txn_${Date.now()}`,
        description,
        customer_email: customerEmail,
      });

      if (response.status === 'success') {
        setPaymentLink(response.payment_link);
        Alert.alert('Success', 'Payment link generated');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to generate payment link');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    // TODO: Implement clipboard functionality
    Alert.alert('Copied', text);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>💳 Squad Payment</Text>
        <Text style={styles.subtitle}>
          Manage your virtual account and payment links
        </Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabs}>
        <View
          style={[
            styles.tab,
            activeTab === 'account' && styles.tab_active,
          ]}
        >
          <Text
            style={styles.tabText}
            onPress={() => setActiveTab('account')}
          >
            Virtual Account
          </Text>
        </View>
        <View
          style={[
            styles.tab,
            activeTab === 'payment' && styles.tab_active,
          ]}
        >
          <Text
            style={styles.tabText}
            onPress={() => setActiveTab('payment')}
          >
            Create Link
          </Text>
        </View>
      </View>

      {/* Virtual Account Tab */}
      {activeTab === 'account' && (
        <View style={styles.tabContent}>
          {accountCreated ? (
            <View style={styles.accountCard}>
              <Text style={styles.accountTitle}>✓ Account Details</Text>

              <View style={styles.accountInfo}>
                <Text style={styles.infoLabel}>Account Number</Text>
                <View style={styles.copyField}>
                  <Text style={styles.infoValue}>{virtualAccount.accountNumber}</Text>
                  <SquadButton
                    title="Copy"
                    onPress={() => copyToClipboard(virtualAccount.accountNumber)}
                    variant="secondary"
                    size="small"
                  />
                </View>
              </View>

              <View style={styles.accountInfo}>
                <Text style={styles.infoLabel}>Bank</Text>
                <Text style={styles.infoValue}>{virtualAccount.bankName}</Text>
              </View>

              <View style={styles.accountInfo}>
                <Text style={styles.infoLabel}>Business Name</Text>
                <Text style={styles.infoValue}>{virtualAccount.businessName}</Text>
              </View>

              <View style={styles.accountInfo}>
                <Text style={styles.infoLabel}>Merchant ID</Text>
                <Text style={styles.infoValue}>{virtualAccount.merchantId}</Text>
              </View>

              <View style={styles.balanceCard}>
                <Text style={styles.balanceLabel}>Current Balance</Text>
                <Text style={styles.balanceAmount}>₦25,500.00</Text>
              </View>

              <View style={styles.actions}>
                <SquadButton
                  title="View Full Statement"
                  onPress={() => Alert.alert('Statement', 'Full transaction statement')}
                  variant="primary"
                />
                <SquadButton
                  title="Transaction History"
                  onPress={() => Alert.alert('History', 'Recent transactions')}
                  variant="secondary"
                />
              </View>
            </View>
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateIcon}>🏦</Text>
              <Text style={styles.emptyStateTitle}>No Account Yet</Text>
              <Text style={styles.emptyStateText}>
                Create a virtual account to receive payments directly
              </Text>
              <SquadButton
                title="Create Account"
                onPress={handleCreateVirtualAccount}
                loading={loading}
                variant="primary"
              />
            </View>
          )}
        </View>
      )}

      {/* Payment Link Tab */}
      {activeTab === 'payment' && (
        <View style={styles.tabContent}>
          {!paymentLink ? (
            <View style={styles.formCard}>
              <Text style={styles.formTitle}>Create Payment Link</Text>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>Amount (₦)</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter amount"
                  keyboardType="decimal-pad"
                  value={amount}
                  onChangeText={setAmount}
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>Description</Text>
                <TextInput
                  style={[styles.input, styles.textArea]}
                  placeholder="What is this payment for?"
                  multiline
                  numberOfLines={3}
                  value={description}
                  onChangeText={setDescription}
                />
              </View>

              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>Customer Email (Optional)</Text>
                <TextInput
                  style={styles.input}
                  placeholder="customer@example.com"
                  keyboardType="email-address"
                  value={customerEmail}
                  onChangeText={setCustomerEmail}
                />
              </View>

              <SquadButton
                title="Generate Payment Link"
                onPress={handleGeneratePaymentLink}
                loading={loading}
                variant="primary"
              />
            </View>
          ) : (
            <View style={styles.resultCard}>
              <Text style={styles.resultTitle}>✓ Payment Link Created</Text>

              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Payment Link</Text>
                <View style={styles.copyField}>
                  <Text style={styles.resultValue}>{paymentLink}</Text>
                  <SquadButton
                    title="Copy"
                    onPress={() => copyToClipboard(paymentLink)}
                    variant="secondary"
                    size="small"
                  />
                </View>
              </View>

              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Amount</Text>
                <Text style={styles.resultValue}>₦{parseFloat(amount).toLocaleString()}</Text>
              </View>

              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Description</Text>
                <Text style={styles.resultValue}>{description}</Text>
              </View>

              <View style={styles.actions}>
                <SquadButton
                  title="Share Link"
                  onPress={() => Alert.alert('Share', 'Share payment link')}
                  variant="primary"
                />
                <SquadButton
                  title="Create Another"
                  onPress={() => {
                    setPaymentLink(null);
                    setAmount('');
                    setDescription('');
                    setCustomerEmail('');
                  }}
                  variant="secondary"
                />
              </View>
            </View>
          )}
        </View>
      )}

      <AILoader visible={loading} message="Processing..." type="payment" />
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
  tabs: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  tab: {
    flex: 1,
    paddingVertical: 16,
    paddingHorizontal: 12,
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
    alignItems: 'center',
  },
  tab_active: {
    borderBottomColor: '#3B82F6',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
  tabContent: {
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  accountCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
  },
  accountTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#047857',
    marginBottom: 16,
  },
  accountInfo: {
    marginBottom: 16,
  },
  infoLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  copyField: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  balanceCard: {
    backgroundColor: '#F0FDF4',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 12,
    marginVertical: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#10B981',
  },
  balanceLabel: {
    fontSize: 12,
    color: '#6B7280',
  },
  balanceAmount: {
    fontSize: 20,
    fontWeight: '700',
    color: '#047857',
    marginTop: 4,
  },
  actions: {
    marginTop: 16,
    gap: 8,
  },
  emptyState: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 32,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  emptyStateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
  },
  formTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16,
  },
  formGroup: {
    marginBottom: 16,
  },
  formLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 6,
  },
  input: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 12,
    fontSize: 14,
    color: '#1F2937',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  resultCard: {
    backgroundColor: '#F0FDF4',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#10B981',
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#047857',
    marginBottom: 16,
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
});

export default SquadPayScreen;
