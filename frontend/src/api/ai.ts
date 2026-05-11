/**
 * AI Processing API Services
 * Handles voice-to-JSON and OCR processing
 */

import client from './client';
import * as FileSystem from 'expo-file-system';

export interface VoiceProcessResponse {
  status: string;
  transaction_data: Record<string, unknown>;
  confidence: number;
  raw_text: string;
}

export interface OCRProcessResponse {
  status: string;
  extracted_data: Record<string, unknown>;
  confidence: number;
  image_text: string;
}

/**
 * Process voice file for transaction extraction
 * Converts speech to structured transaction JSON
 */
export const processVoice = async (
  audioFilePath: string
): Promise<VoiceProcessResponse> => {
  try {
    // Read file as base64
    const base64Data = await FileSystem.readAsStringAsync(audioFilePath, {
      encoding: FileSystem.EncodingType.Base64,
    });

    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('file', {
      uri: audioFilePath,
      name: 'audio.mp3',
      type: 'audio/mpeg',
    } as any);

    const response = await client.post<VoiceProcessResponse>(
      '/ai/process-voice',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error('Voice processing error:', error);
    throw error;
  }
};

/**
 * Process image file for OCR extraction
 * Extracts data from physical ledger images
 */
export const processOCR = async (
  imagePath: string
): Promise<OCRProcessResponse> => {
  try {
    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('file', {
      uri: imagePath,
      name: 'ledger.jpg',
      type: 'image/jpeg',
    } as any);

    const response = await client.post<OCRProcessResponse>(
      '/ai/process-ocr',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error('OCR processing error:', error);
    throw error;
  }
};

/**
 * Get voice processing job status
 */
export const getVoiceStatus = async (jobId: string) => {
  const response = await client.get(`/ai/voice-status/${jobId}`);
  return response.data;
};

/**
 * Get OCR processing job status
 */
export const getOCRStatus = async (jobId: string) => {
  const response = await client.get(`/ai/ocr-status/${jobId}`);
  return response.data;
};
