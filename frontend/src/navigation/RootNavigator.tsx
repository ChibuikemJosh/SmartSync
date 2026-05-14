/**
 * Navigation Configuration
 * Setup for React Navigation with Stack and BottomTab navigators
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import * as SecureStore from 'expo-secure-store';
import { ActivityIndicator, View } from 'react-native';
import { AuthProvider, useAuth } from '../contexts/AuthContext';

// Screens
import DashboardScreen from '../screens/Dashboard';
import VoiceERPScreen from '../screens/VoiceERP';
import CaptureOCRScreen from '../screens/CaptureOCR';
import SquadPayScreen from '../screens/SquadPay';
import ChatScreen from '../screens/ChatScreen';
import AuthScreen from '../screens/AuthScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

/**
 * Dashboard Stack Navigator
 */
const DashboardStackNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen
        name="DashboardScreen"
        component={DashboardScreen}
        options={{ title: 'Dashboard' }}
      />
    </Stack.Navigator>
  );
};

/**
 * Voice ERP Stack Navigator
 */
const VoiceStackNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen
        name="VoiceERPScreen"
        component={VoiceERPScreen}
        options={{ title: 'Voice Entry' }}
      />
    </Stack.Navigator>
  );
};

/**
 * OCR Stack Navigator
 */
const OCRStackNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen
        name="CaptureOCRScreen"
        component={CaptureOCRScreen}
        options={{ title: 'Capture Ledger' }}
      />
    </Stack.Navigator>
  );
};

/**
 * Squad Pay Stack Navigator
 */
const SquadStackNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen
        name="SquadPayScreen"
        component={SquadPayScreen}
        options={{ title: 'Squad Pay' }}
      />
    </Stack.Navigator>
  );
};

/**
 * Bottom Tab Navigator - Main app structure
 */
const BottomTabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Voice') {
            iconName = focused ? 'mic' : 'mic-outline';
          } else if (route.name === 'OCR') {
            iconName = focused ? 'camera' : 'camera-outline';
          } else if (route.name === 'Squad') {
            iconName = focused ? 'card' : 'card-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3B82F6',
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarLabelStyle: {
          fontSize: 12,
          marginTop: -4,
        },
        tabBarStyle: {
          borderTopWidth: 1,
          borderTopColor: '#E5E7EB',
          paddingBottom: 4,
          paddingTop: 4,
          height: 56,
        },
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardStackNavigator}
        options={{
          title: 'Dashboard',
        }}
      />
      <Tab.Screen
        name="Voice"
        component={VoiceStackNavigator}
        options={{
          title: 'Voice',
        }}
      />
      <Tab.Screen
        name="OCR"
        component={OCRStackNavigator}
        options={{
          title: 'Ledger',
        }}
      />
      <Tab.Screen
        name="Squad"
        component={SquadStackNavigator}
        options={{
          title: 'Payments',
        }}
      />
      <Tab.Screen
        name="Chat"
        component={ChatScreen}
        options={{ title: 'Advisor' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
};

/**
 * Root Navigator - Main app entry point
 */
export const RootNavigatorInner: React.FC = () => {
  const { authenticated } = useAuth();

  return (
    <NavigationContainer>
      {authenticated ? <BottomTabNavigator /> : (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Auth" component={AuthScreen} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
};

export const RootNavigator: React.FC = () => {
  return (
    <AuthProvider>
      <RootNavigatorInner />
    </AuthProvider>
  );
};

export default RootNavigator;
