import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import client from '../api/client';
import { useAuth } from '../contexts/AuthContext';

const AuthScreen: React.FC<any> = ({ navigation }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [location, setLocation] = useState('');
  const [role, setRole] = useState<'Trader' | 'Worker'>('Trader');
  const [loading, setLoading] = useState(false);
  const { setAuthenticated } = useAuth();

  const saveToken = async (token: string) => {
    await SecureStore.setItemAsync('auth_token', token);
  };

  const fetchProfileAndNavigate = async (token: string) => {
    try {
      const res = await client.get('/auth/profile', {
        headers: { Authorization: `Bearer ${token}` },
      });
      // Optionally store profile
      await SecureStore.setItemAsync('user_profile', JSON.stringify(res.data));
      setAuthenticated(true);
    } catch (e) {
      console.warn('Profile fetch failed', e);
      setAuthenticated(true);
    }
  };

  const handleRegister = async () => {
    setLoading(true);
    try {
      const payload = { name, email, password, role, location };
      const res = await client.post('/auth/register', payload);
      // If backend returns profile, try to login automatically
      const loginParams = new URLSearchParams();
      loginParams.append('username', email);
      loginParams.append('password', password);
      const tokenRes = await client.post('/auth/login', loginParams.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const token = tokenRes.data.access_token || tokenRes.data.token || tokenRes.data;
      if (token) {
        await saveToken(token);
        await fetchProfileAndNavigate(token);
      }
    } catch (err: any) {
      Alert.alert('Register failed', err?.response?.data?.detail || err.message || 'Unknown');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const res = await client.post('/auth/login', params.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const token = res.data.access_token || res.data.token || res.data;
      if (!token) throw new Error('No token returned');
      await saveToken(token);
      await fetchProfileAndNavigate(token);
    } catch (err: any) {
      Alert.alert('Login failed', err?.response?.data?.detail || err.message || 'Unknown');
    } finally {
      setLoading(false);
    }
  };

  const { setAuthenticated } = useAuth();

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>SmartSync</Text>
      <Text style={styles.subtitle}>Nigerian Market Assistant</Text>

      {isRegister && (
        <TextInput placeholder="Name" style={styles.input} value={name} onChangeText={setName} />
      )}

      <TextInput placeholder="Email" style={styles.input} value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
      <TextInput placeholder="Password" style={styles.input} value={password} onChangeText={setPassword} secureTextEntry />

      {isRegister && (
        <>
          <TextInput placeholder="Location (e.g. Lagos Market)" style={styles.input} value={location} onChangeText={setLocation} />
          <View style={styles.roleRow}>
            <TouchableOpacity style={[styles.roleBtn, role === 'Trader' && styles.roleActive]} onPress={() => setRole('Trader')}>
              <Text style={role === 'Trader' ? styles.roleTextActive : styles.roleText}>Trader</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.roleBtn, role === 'Worker' && styles.roleActive]} onPress={() => setRole('Worker')}>
              <Text style={role === 'Worker' ? styles.roleTextActive : styles.roleText}>Worker</Text>
            </TouchableOpacity>
          </View>
        </>
      )}

      <TouchableOpacity style={styles.primaryBtn} onPress={isRegister ? handleRegister : handleLogin} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>{isRegister ? 'Register' : 'Login'}</Text>}
      </TouchableOpacity>

      <TouchableOpacity onPress={() => setIsRegister(!isRegister)} style={styles.switchRow}>
        <Text style={styles.switchText}>{isRegister ? 'Have an account? Login' : "No account? Register"}</Text>
      </TouchableOpacity>

      <Text style={styles.hint}>Oga, if you no get token, register make we sabi you.</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: 'center' },
  logo: { fontSize: 32, fontWeight: '700', color: '#2196F3', textAlign: 'center' },
  subtitle: { textAlign: 'center', marginBottom: 24, color: '#6B7280' },
  input: { borderWidth: 1, borderColor: '#E5E7EB', padding: 12, borderRadius: 8, marginBottom: 12 },
  primaryBtn: { backgroundColor: '#2196F3', padding: 14, borderRadius: 8, alignItems: 'center', marginTop: 8 },
  btnText: { color: '#fff', fontWeight: '600' },
  switchRow: { marginTop: 12, alignItems: 'center' },
  switchText: { color: '#374151' },
  hint: { marginTop: 24, textAlign: 'center', color: '#9CA3AF' },
  roleRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  roleBtn: { flex: 1, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: '#E5E7EB', marginHorizontal: 4, alignItems: 'center' },
  roleActive: { backgroundColor: '#2196F3', borderColor: '#2196F3' },
  roleText: { color: '#374151' },
  roleTextActive: { color: '#fff', fontWeight: '600' },
});

export default AuthScreen;
