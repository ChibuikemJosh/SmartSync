/**
 * Squad Payment API Services
 * Handles virtual accounts and payment links
 */

import client from './client';

export interface VirtualAccountRequest {
  merchant_id: string;
  business_name: string;
  email: string;
  phone: string;
}

export interface VirtualAccountResponse {
  status: string;
  account_number: string;
  bank_name: string;
  merchant_id: string;
  business_name: string;
}

export interface PaymentLinkRequest {
  merchant_id: string;
  amount: number;
  transaction_id: string;
  description: string;
  customer_email?: string;
}

export interface PaymentLinkResponse {
  status: string;
  payment_link: string;
  transaction_id: string;
  amount: number;
}

/**
 * Create a virtual account for a trader
 */
export const createVirtualAccount = async (
  data: VirtualAccountRequest
): Promise<VirtualAccountResponse> => {
  const response = await client.post<VirtualAccountResponse>(
    '/squad/create-virtual-account',
    data
  );
  return response.data;
};

/**
 * Generate a payment link for a transaction
 */
export const generatePaymentLink = async (
  data: PaymentLinkRequest
): Promise<PaymentLinkResponse> => {
  const response = await client.post<PaymentLinkResponse>(
    '/squad/generate-payment-link',
    data
  );
  return response.data;
};

/**
 * Get transactions for a merchant
 */
export const getTransactions = async (merchantId: string) => {
  const response = await client.get(`/squad/transactions/${merchantId}`);
  return response.data;
};
