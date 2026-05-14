import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import client from '../api/client';

const ProfileScreen: React.FC<any> = ({ navigation }) => {
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    (async () => {
      const p = await SecureStore.getItemAsync('user_profile');
      if (p) setProfile(JSON.parse(p));
      else {
        try {
          const res = await client.get('/auth/profile');
          setProfile(res.data);
          await SecureStore.setItemAsync('user_profile', JSON.stringify(res.data));
        } catch (e) {
          console.warn('Profile fetch', e);
        }
      }
    })();
  }, []);

  const handleLogout = async () => {
    await SecureStore.deleteItemAsync('auth_token');
    await SecureStore.deleteItemAsync('user_profile');
    navigation.replace('Auth');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.name}>{profile?.name || 'User'}</Text>
      <Text style={styles.meta}>{profile?.email}</Text>
      <View style={styles.card}>
        <Text style={{ fontWeight: '700' }}>Trust Score</Text>
        <Text style={{ fontSize: 24, fontWeight: '800' }}>{profile?.trust_score ?? 0}</Text>
      </View>

      <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
        <Text style={{ color: '#fff', fontWeight: '700' }}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fff' },
  name: { fontSize: 20, fontWeight: '800' },
  meta: { color: '#6B7280', marginBottom: 16 },
  card: { padding: 12, borderRadius: 8, backgroundColor: '#F9FAFB', marginVertical: 12 },
  logoutBtn: { backgroundColor: '#EF4444', padding: 12, borderRadius: 8, alignItems: 'center', marginTop: 20 },
});

export default ProfileScreen;
