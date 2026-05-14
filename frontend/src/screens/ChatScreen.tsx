import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import client from '../api/client';

type Message = { id: string; text: string; sender: 'me' | 'bot' };

const ChatScreen: React.FC<any> = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setMessages([
      { id: 'welcome', text: "How you dey? Ask about your balance or sales, e.g. 'Wetin be my balance'", sender: 'bot' },
    ]);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { id: Date.now().toString(), text: input.trim(), sender: 'me' };
    setMessages((s) => [...s, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const res = await client.post(
        '/chat/chat',
        { message: userMsg.text },
        { headers: token ? { Authorization: `Bearer ${token}` } : undefined }
      );

      const botText = res.data?.answer || res.data?.message || JSON.stringify(res.data || {});
      const botMsg: Message = { id: 'bot-' + Date.now().toString(), text: botText, sender: 'bot' };
      setMessages((s) => [...s, botMsg]);
    } catch (err) {
      const errMsg: Message = { id: 'err-' + Date.now().toString(), text: 'Sorry, I no fit answer now. Try again.', sender: 'bot' };
      setMessages((s) => [...s, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }: { item: Message }) => (
    <View style={[styles.msgRow, item.sender === 'me' ? styles.msgRowRight : styles.msgRowLeft]}>
      <View style={[styles.bubble, item.sender === 'me' ? styles.bubbleMe : styles.bubbleBot]}>
        <Text style={item.sender === 'me' ? styles.textMe : styles.textBot}>{item.text}</Text>
      </View>
    </View>
  );

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
      <FlatList data={messages} keyExtractor={(i) => i.id} renderItem={renderItem} contentContainerStyle={{ padding: 12 }} />

      <View style={styles.composer}>
        <TextInput style={styles.input} placeholder="Ask AI Market Advisor..." value={input} onChangeText={setInput} />
        <TouchableOpacity style={styles.sendBtn} onPress={sendMessage} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.sendText}>Send</Text>}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  msgRow: { marginVertical: 6 },
  msgRowLeft: { alignItems: 'flex-start' },
  msgRowRight: { alignItems: 'flex-end' },
  bubble: { padding: 12, borderRadius: 12, maxWidth: '85%' },
  bubbleBot: { backgroundColor: '#F3F4F6' },
  bubbleMe: { backgroundColor: '#2196F3' },
  textBot: { color: '#111827' },
  textMe: { color: '#fff' },
  composer: { flexDirection: 'row', padding: 8, borderTopWidth: 1, borderColor: '#E5E7EB', backgroundColor: '#fff' },
  input: { flex: 1, padding: 12, borderRadius: 8, backgroundColor: '#F9FAFB', marginRight: 8 },
  sendBtn: { backgroundColor: '#2196F3', paddingHorizontal: 16, justifyContent: 'center', borderRadius: 8 },
  sendText: { color: '#fff', fontWeight: '600' },
});

export default ChatScreen;
