/**
 * SmartSync Frontend - Main App
 * React Native Expo app with TypeScript
 */

import React from 'react';
import { StatusBar, SafeAreaView, StyleSheet } from 'react-native';
import { RootNavigator } from './src/navigation/RootNavigator';

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <RootNavigator />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
});
