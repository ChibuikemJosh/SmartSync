# SmartSync Flutter App - Backend Integration Guide

## 🔗 API Integration Overview

This Flutter app connects to the SmartSync backend running at `http://YOUR_IP:8000`.

### Setting Up the Connection

1. **Identify Backend IP:**
   ```bash
   # From the machine running backend
   ifconfig | grep inet | grep -v 127.0.0.1
   # Example: 192.168.1.100
   ```

2. **Configure in Flutter:**
   ```dart
   // lib/services/api_service.dart
   static const String baseUrl = 'http://192.168.1.100:8000';
   ```

3. **Test Connection:**
   ```bash
   curl http://192.168.1.100:8000/health
   # Should return 200 OK
   ```

## 📡 API Endpoints

### Authentication Endpoints

#### Login
- **URL:** `POST /auth/login`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "token_here",
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "full_name": "User Name",
      "business_name": "Business",
      "phone": "+234XXXXXXXXXX",
      "trust_score": 75.5
    }
  }
  ```

#### Signup
- **URL:** `POST /auth/signup`
- **Body:**
  ```json
  {
    "email": "newuser@example.com",
    "password": "StrongPassword123",
    "full_name": "New User",
    "business_name": "My Business",
    "phone": "+234XXXXXXXXXX"
  }
  ```
- **Response:** Same as login

### Dashboard Endpoints

#### Get Dashboard Data
- **URL:** `GET /api/dashboard`
- **Headers:** `Authorization: Bearer {token}`
- **Response:**
  ```json
  {
    "trust_score": 85.0,
    "user": { /* user object */ },
    "recent_transactions": [ /* transaction array */ ]
  }
  ```

#### Get Profile
- **URL:** `GET /api/profile`
- **Headers:** `Authorization: Bearer {token}`
- **Response:**
  ```json
  {
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "full_name": "User Name",
      "business_name": "Business",
      "trust_score": 85.0
    }
  }
  ```

#### Get Transactions
- **URL:** `GET /api/transactions`
- **Headers:** `Authorization: Bearer {token}`
- **Response:**
  ```json
  {
    "transactions": [
      {
        "id": "trans_id",
        "description": "Transaction name",
        "amount": 5000.00,
        "currency": "NGN",
        "status": "completed",
        "category": "payment",
        "timestamp": "2026-05-14T10:30:00Z",
        "verification_status": "verified"
      }
    ]
  }
  ```

### AI & Voice Endpoints

#### Process Voice
- **URL:** `POST /ai/process-voice`
- **Headers:** 
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "audio_data": "base64_encoded_audio",
    "format": "wav"
  }
  ```
- **Response:**
  ```json
  {
    "transcription": "Text from voice",
    "confidence": 0.95,
    "action": "create_transaction"
  }
  ```

#### Process Ledger (OCR)
- **URL:** `POST /ai/process-ledger`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "image_data": "base64_encoded_image",
    "format": "jpeg"
  }
  ```
- **Response:**
  ```json
  {
    "id": "ocr_id",
    "image_path": "/path/to/image",
    "extracted_text": "Extracted text from image",
    "confidence": 0.92,
    "parsed_data": {
      "date": "2026-05-14",
      "amount": 50000,
      "reference": "REF123"
    }
  }
  ```

### Chat Endpoints

#### Send Message
- **URL:** `POST /chat/ask`
- **Headers:**
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "message": "What is my trust score?",
    "conversation_id": "optional_conversation_id"
  }
  ```
- **Response:**
  ```json
  {
    "response": "Your current trust score is 85.0",
    "conversation_id": "conv_id"
  }
  ```

#### Get Chat History
- **URL:** `GET /chat/history`
- **Headers:** `Authorization: Bearer {token}`
- **Response:**
  ```json
  {
    "messages": [
      {
        "id": "msg_id",
        "content": "Your message",
        "timestamp": "2026-05-14T10:30:00Z",
        "is_user": true
      },
      {
        "id": "msg_id",
        "content": "AI response",
        "timestamp": "2026-05-14T10:30:05Z",
        "is_user": false
      }
    ]
  }
  ```

## 🔐 Authentication Flow

1. **User Signs Up:**
   - App sends credentials to `/auth/signup`
   - Backend creates user and returns access token
   - App stores token securely in `FlutterSecureStorage`

2. **User Logs In:**
   - App sends credentials to `/auth/login`
   - Backend validates and returns access token
   - App stores token securely

3. **Authenticated Requests:**
   - App includes token in `Authorization: Bearer {token}` header
   - Backend validates token
   - Returns protected resource

4. **Token Expiration:**
   - Backend returns 401 Unauthorized
   - App redirects to login screen
   - User must re-authenticate

5. **Logout:**
   - App deletes token from secure storage
   - Redirects to auth screen

## 📝 Implementation Examples

### Login Implementation
```dart
// In auth_provider.dart
Future<bool> login(String email, String password) async {
  final result = await _apiService.login(email, password);
  if (result['success']) {
    _user = result['user'];
    _token = result['token'];
    return true;
  }
  return false;
}
```

### API Call with Token
```dart
// In api_service.dart
Future<List<Transaction>> getTransactions() async {
  final token = await getToken();
  final response = await http.get(
    Uri.parse('$baseUrl/api/transactions'),
    headers: _getHeaders(token),
  );
  // Handle response
}

Map<String, String> _getHeaders(String? token) {
  return {
    'Content-Type': 'application/json',
    if (token != null) 'Authorization': 'Bearer $token',
  };
}
```

### Sending Voice Data
```dart
// In voice_ocr_provider.dart
Future<void> stopRecordingAndProcess(String base64Audio) async {
  final result = await _apiService.processVoice(base64Audio);
  _voiceProcessingResult = result['transcription'];
}
```

### Sending Chat Messages
```dart
// In chat_provider.dart
Future<void> sendMessage(String content) async {
  final response = await _apiService.sendChatMessage(content);
  final aiMessage = ChatMessage(
    content: response['response'],
    isUser: false,
  );
  _messages.add(aiMessage);
}
```

## 🧪 Testing API Integration

### Test with cURL

```bash
# Test backend is running
curl http://192.168.1.100:8000/health

# Test login
curl -X POST http://192.168.1.100:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@smartsync.com",
    "password": "Demo@123456"
  }'

# Test with token
curl http://192.168.1.100:8000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test in Flutter App

1. Launch app with `flutter run`
2. Try to login with demo credentials
3. Check console for API logs
4. Verify profile loads correctly
5. Test each feature:
   - Voice: Press mic button
   - OCR: Upload image
   - Chat: Send message
   - Dashboard: View data

## 🐛 Debugging API Issues

### Enable Debug Logging

Add to `api_service.dart`:
```dart
print('Request: $method $url');
print('Headers: $headers');
print('Body: $body');
print('Response: ${response.statusCode}');
print('Response Body: ${response.body}');
```

### Check Network Connectivity

```dart
import 'package:connectivity_plus/connectivity_plus.dart';

final connectivityResult = await Connectivity().checkConnectivity();
print('Connectivity: $connectivityResult');
```

### Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Token expired, need to login again |
| 404 Not Found | Check endpoint URL spelling |
| 500 Server Error | Check backend logs |
| Network timeout | Verify backend is running |
| SSL error | Use HTTP in dev, HTTPS in prod |

## 🚀 Deployment Considerations

### Development
- Use `http://` with local IP
- Backend runs on `http://localhost:8000`

### Production
- Use HTTPS with domain
- Backend runs on `https://api.smartsync.ng`
- Update base URL in `api_service.dart`
- Enable SSL pinning for security

## 📚 Backend Reference

For backend API documentation, see:
- [Backend README](../../backend/README.md)
- Backend route files:
  - `backend/routes/auth.py` - Authentication
  - `backend/routes/ai.py` - AI/Voice/OCR
  - `backend/routes/chat.py` - Chat
  - `backend/routes/transactions.py` - Transactions

## ✅ Integration Checklist

- [ ] Backend is running and accessible
- [ ] IP address configured in app
- [ ] Demo account login works
- [ ] API responses match expected format
- [ ] Token storage works
- [ ] Voice API working
- [ ] OCR API working
- [ ] Chat API working
- [ ] Error handling works
- [ ] Token refresh works (if implemented)

---

**Version:** 1.0.0
**Last Updated:** May 2026
**For:** SmartSync Flutter Backend Integration

