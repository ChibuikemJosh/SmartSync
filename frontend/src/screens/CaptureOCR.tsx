/**
 * CaptureOCR Screen
 * UI for capturing and processing physical ledger photos
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Image,
} from 'react-native';
import { CameraView } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import SquadButton from '../components/SquadButton';
import AILoader from '../components/AILoader';
import { processOCR } from '../api/ai';

interface CaptureOCRScreenProps {
  navigation: any;
}

interface ExtractedData {
  date: string;
  entries: Array<{ description: string; amount: number }>;
  total: number;
}

const CaptureOCRScreen: React.FC<CaptureOCRScreenProps> = ({ navigation }) => {
  const cameraRef = useRef<CameraView>(null);
  const [permission, setPermission] = useState<boolean | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);

  useEffect(() => {
    requestCameraPermission();
  }, []);

  const requestCameraPermission = async () => {
    try {
      const { status } = await CameraView.requestCameraPermissionsAsync();
      setPermission(status === 'granted');
    } catch (error) {
      console.error('Camera permission error:', error);
    }
  };

  const takePicture = async () => {
    try {
      if (cameraRef.current) {
        const photo = await cameraRef.current.takePictureAsync({ quality: 0.8 });
        setCapturedImage(photo.uri);
        setShowCamera(false);
        await processImage(photo.uri);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take picture');
      console.error('Camera error:', error);
    }
  };

  const pickImageFromLibrary = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.8,
      });

      if (!result.cancelled) {
        const uri = result.assets[0].uri;
        setCapturedImage(uri);
        await processImage(uri);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
      console.error('Image picker error:', error);
    }
  };

  const processImage = async (uri: string) => {
    try {
      setProcessing(true);
      const response = await processOCR(uri);

      if (response.status === 'success') {
        setExtractedData(response.extracted_data as ExtractedData);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to process image');
      console.error('Processing error:', error);
    } finally {
      setProcessing(false);
    }
  };

  const handleSaveExtraction = () => {
    // TODO: Save extracted data to database
    Alert.alert('Success', 'Ledger data saved successfully');
    setExtractedData(null);
    setCapturedImage(null);
  };

  if (permission === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.center}>Requesting camera permission...</Text>
      </View>
    );
  }

  if (!permission) {
    return (
      <View style={styles.container}>
        <View style={styles.permissionCard}>
          <Text style={styles.permissionTitle}>📸 Camera Permission Required</Text>
          <Text style={styles.permissionText}>
            SmartSync needs camera access to capture ledger images.
          </Text>
          <SquadButton
            title="Grant Permission"
            onPress={requestCameraPermission}
            variant="primary"
          />
        </View>
      </View>
    );
  }

  if (showCamera) {
    return (
      <View style={styles.cameraContainer}>
        <CameraView ref={cameraRef} style={styles.camera}>
          <View style={styles.cameraOverlay}>
            <Text style={styles.cameraGuide}>
              📖 Align ledger with the frame
            </Text>
            <View style={styles.frameGuide} />
          </View>

          <View style={styles.cameraControls}>
            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => setShowCamera(false)}
            >
              <Text style={styles.cancelButtonText}>✕</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
              <View style={styles.captureButtonInner} />
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>📸 Capture Ledger</Text>
        <Text style={styles.subtitle}>
          Take a photo of your physical ledger and extract data
        </Text>
      </View>

      {capturedImage && (
        <View style={styles.previewCard}>
          <Image source={{ uri: capturedImage }} style={styles.previewImage} />
        </View>
      )}

      {!capturedImage && (
        <View style={styles.optionsCard}>
          <Text style={styles.optionsTitle}>Choose an option:</Text>
          <View style={styles.optionsButtons}>
            <SquadButton
              title="📷 Take Photo"
              onPress={() => setShowCamera(true)}
              variant="primary"
            />
            <SquadButton
              title="📁 Choose from Gallery"
              onPress={pickImageFromLibrary}
              variant="secondary"
            />
          </View>
        </View>
      )}

      {/* Extracted Data Display */}
      {extractedData && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>✓ Ledger Data Extracted</Text>

          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>Date</Text>
            <Text style={styles.resultValue}>{extractedData.date}</Text>
          </View>

          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>Entries</Text>
            {extractedData.entries.map((entry, index) => (
              <View key={index} style={styles.entryItem}>
                <Text style={styles.entryDescription}>{entry.description}</Text>
                <Text style={styles.entryAmount}>
                  ₦{entry.amount.toLocaleString()}
                </Text>
              </View>
            ))}
          </View>

          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Total</Text>
            <Text style={styles.totalAmount}>
              ₦{extractedData.total.toLocaleString()}
            </Text>
          </View>

          <View style={styles.resultActions}>
            <SquadButton
              title="Save Extraction"
              onPress={handleSaveExtraction}
              variant="primary"
            />
            <SquadButton
              title="Capture Again"
              onPress={() => {
                setExtractedData(null);
                setCapturedImage(null);
              }}
              variant="secondary"
            />
          </View>
        </View>
      )}

      {/* Instructions */}
      <View style={styles.instructionsCard}>
        <Text style={styles.instructionsTitle}>📋 Best Practices</Text>
        <Text style={styles.instructionItem}>
          • Ensure good lighting and clear visibility
        </Text>
        <Text style={styles.instructionItem}>
          • Avoid shadows and reflections
        </Text>
        <Text style={styles.instructionItem}>
          • Capture the entire ledger page
        </Text>
        <Text style={styles.instructionItem}>
          • Use clear, legible handwriting
        </Text>
      </View>

      <AILoader
        visible={processing}
        message="Reading ledger and extracting data"
        type="ocr"
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  cameraGuide: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 24,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  frameGuide: {
    width: '100%',
    aspectRatio: 3 / 4,
    borderWidth: 2,
    borderColor: '#3B82F6',
    borderRadius: 8,
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
  },
  cameraControls: {
    position: 'absolute',
    bottom: 16,
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  cancelButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 24,
    color: '#FFFFFF',
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonInner: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#3B82F6',
  },
  center: {
    textAlign: 'center',
    marginTop: 20,
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
  previewCard: {
    marginHorizontal: 16,
    marginTop: 20,
    borderRadius: 12,
    overflow: 'hidden',
  },
  previewImage: {
    width: '100%',
    height: 300,
    resizeMode: 'cover',
  },
  optionsCard: {
    marginHorizontal: 16,
    marginTop: 20,
    backgroundColor: '#FFFFFF',
    paddingVertical: 20,
    paddingHorizontal: 16,
    borderRadius: 12,
  },
  optionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  optionsButtons: {
    gap: 8,
  },
  permissionCard: {
    marginHorizontal: 16,
    marginTop: '50%',
    backgroundColor: '#FFFFFF',
    paddingVertical: 24,
    paddingHorizontal: 16,
    borderRadius: 12,
  },
  permissionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  permissionText: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 16,
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
  entryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
    marginTop: 4,
  },
  entryDescription: {
    fontSize: 13,
    color: '#1F2937',
  },
  entryAmount: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#D1D5DB',
    marginTop: 8,
  },
  totalLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  totalAmount: {
    fontSize: 14,
    fontWeight: '700',
    color: '#047857',
  },
  resultActions: {
    marginTop: 16,
    gap: 8,
  },
  instructionsCard: {
    marginHorizontal: 16,
    marginTop: 20,
    marginBottom: 20,
    backgroundColor: '#FEF3C7',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  instructionsTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#92400E',
    marginBottom: 8,
  },
  instructionItem: {
    fontSize: 12,
    color: '#92400E',
    marginBottom: 4,
  },
});

export default CaptureOCRScreen;
