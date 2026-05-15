# SmartSync Flutter App - Quick Reference

## 🚀 Quick Start (3 Steps)

### 1️⃣ Setup
```bash
cd /workspaces/SmartSync/frontend_new
flutter pub get
```

### 2️⃣ Configure
Edit `lib/services/api_service.dart` line 9:
```dart
static const String baseUrl = 'http://192.168.1.100:8000'; // Your IP
```

### 3️⃣ Run
```bash
flutter run
```

## 📱 App Navigation

```
┌─────────────────────────────────┐
│  SmartSync App Navigation       │
├─────────────────────────────────┤
│                                 │
│  Unauthenticated (Auth Screen) │
│  ├── Login Tab                 │
│  │   ├── Email field           │
│  │   ├── Password field        │
│  │   └── Forgot Password link  │
│  │                              │
│  └── Signup Tab                │
│      ├── Full Name             │
│      ├── Business Name         │
│      ├── Phone                 │
│      ├── Email                 │
│      └── Password              │
│                                 │
│  Authenticated (Dashboard)      │
│  ├── Home Tab                  │
│  │   ├── Trust Score Gauge     │
│  │   ├── Quick Actions         │
│  │   └── Recent Transactions   │
│  │                              │
│  ├── Voice Tab                 │
│  │   ├── Record Button         │
│  │   └── Results Display       │
│  │                              │
│  ├── OCR Tab                   │
│  │   ├── Upload Button         │
│  │   └── Scan Results          │
│  │                              │
│  ├── Chat Tab                  │
│  │   ├── Chat Messages         │
│  │   └── Input Field           │
│  │                              │
│  └── Profile Tab               │
│      ├── User Info             │
│      ├── Statistics            │
│      └── Settings              │
└─────────────────────────────────┘
```

## 🎨 Design Colors

```dart
AppTheme.primaryColor        // #1A237E (Deep Navy)
AppTheme.secondaryColor      // #2E7D32 (Emerald Green)
AppTheme.backgroundColor     // #FFFFFF (White)
AppTheme.surfaceColor        // #F5F5F5 (Light Gray)
AppTheme.successColor        // #2E7D32 (Green)
AppTheme.errorColor          // #D32F2F (Red)
AppTheme.warningColor        // #F57C00 (Orange)
AppTheme.infoColor           // #1976D2 (Blue)
```

## 🔧 Common Tasks

### Add a New Screen

1. Create file: `lib/screens/new_screen.dart`
2. Create StatefulWidget extending SafeArea/Scaffold
3. Add to Dashboard navigation
4. Add BottomNavigationBarItem

### Add API Endpoint

1. Add method to `lib/services/api_service.dart`
2. Create model in `lib/models/models.dart` if needed
3. Use in provider
4. Call from screen

### Add State Management

1. Create provider: `lib/providers/new_provider.dart`
2. Extend ChangeNotifier
3. Add to main.dart providers list
4. Use Consumer in widgets

### Create Reusable Widget

1. Add to `lib/widgets/custom_widgets.dart` or `specialized_widgets.dart`
2. Make StatelessWidget if no state
3. Use throughout app
4. Document parameters

## 📡 API Testing

```bash
# Test backend health
curl http://192.168.1.100:8000/health

# Login and get token
TOKEN=$(curl -s -X POST http://192.168.1.100:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@smartsync.com","password":"Demo@123456"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Use token for authenticated requests
curl http://192.168.1.100:8000/api/profile \
  -H "Authorization: Bearer $TOKEN"
```

## 🎯 Feature Implementation Checklist

### Voice Feature
- [x] UI with mic button
- [x] Recording timer
- [x] Animation during recording
- [x] API integration
- [x] Result display

### OCR Feature
- [x] UI with upload button
- [x] Image selection
- [x] API integration
- [x] Result parsing
- [x] Confidence display

### Chat Feature
- [x] Message bubble UI
- [x] Message list
- [x] Input field
- [x] API integration
- [x] Auto-scroll

### Dashboard
- [x] Trust score gauge
- [x] Transaction list
- [x] Quick actions
- [x] Stats display
- [x] Refresh capability

### Auth
- [x] Login form
- [x] Signup form
- [x] Validation
- [x] Token storage
- [x] Error handling

## 📦 Key Providers

### AuthProvider
```dart
// Properties
user              // Current user
token             // Auth token
isLoggedIn        // Boolean
isLoading         // Request state
error             // Error message

// Methods
login()           // Login user
signup()          // Create account
logout()          // Clear session
```

### DashboardProvider
```dart
// Properties
user              // User data
transactions      // Transaction list
trustScore        // Score value
isLoading         // Loading state

// Methods
loadDashboard()   // Fetch all data
refreshTransactions()
refreshProfile()
```

### ChatProvider
```dart
// Properties
messages          // Chat messages
isLoading         // Loading state
isReceivingMessage // Response state

// Methods
loadChatHistory() // Get messages
sendMessage()     // Send & receive
clearMessages()   // Reset
```

### VoiceOCRProvider
```dart
// Properties
isRecording       // Recording state
isProcessing      // Processing state
recordingDuration // Duration
lastOCRResult     // OCR data
voiceProcessingResult // Transcription

// Methods
startRecording()
stopRecordingAndProcess()
processOCRImage()
```

## 🛠️ Useful Commands

```bash
# Development
flutter run                   # Run in debug
flutter run --release       # Run in release
flutter run --profile       # Performance profiling

# Code Quality
flutter analyze             # Check code
dart format lib/            # Format code
flutter pub get             # Get packages
flutter pub upgrade         # Update packages

# Testing
flutter test                # Run tests
flutter test --coverage    # Code coverage

# Building
flutter build apk           # Android APK
flutter build appbundle     # Android App Bundle
flutter build ios           # iOS app
flutter build web           # Web app

# Debugging
flutter devices             # List devices
flutter logs                # View logs
flutter devtools            # Open DevTools
```

## 🔐 Secure Storage

```dart
// Store token
final storage = const FlutterSecureStorage();
await storage.write(key: 'auth_token', value: token);

// Retrieve token
final token = await storage.read(key: 'auth_token');

// Delete token
await storage.delete(key: 'auth_token');
```

## 💱 Currency Formatting

```dart
// Full format with decimals
CurrencyFormatter.formatNaira(1234.56)  // ₦1,234.56

// Short format (K, M)
CurrencyFormatter.formatNairaShort(1200)  // ₦1.2K

// Without decimals
CurrencyFormatter.formatNairaWithoutDecimal(1234)  // ₦1,234
```

## 📅 Date Formatting

```dart
DateFormatter.formatDate(date)        // MMM dd, yyyy
DateFormatter.formatTime(date)        // hh:mm a
DateFormatter.formatDateTime(date)    // MMM dd, yyyy - hh:mm a
DateFormatter.formatDateShort(date)   // MMM dd
DateFormatter.getRelativeTime(date)   // "2h ago"
```

## ✔️ Input Validation

```dart
ValidationUtils.isValidEmail(email)              // true/false
ValidationUtils.isValidPhone(phone)              // true/false
ValidationUtils.isValidNigerianPhone(phone)      // true/false
ValidationUtils.isValidPassword(password)        // true/false
ValidationUtils.getPasswordStrength(password)    // "Strong"
```

## 🎨 Text Styles

```dart
AppTextStyles.display1          // 32px, Bold
AppTextStyles.display2          // 28px, Bold
AppTextStyles.heading1          // 24px, Bold
AppTextStyles.heading2          // 20px, Bold
AppTextStyles.heading3          // 18px, Semi-bold
AppTextStyles.bodyLarge         // 16px, Medium
AppTextStyles.bodyMedium        // 14px, Medium
AppTextStyles.bodySmall         // 12px, Regular
AppTextStyles.label             // 12px, Semi-bold
AppTextStyles.labelSmall        // 10px, Semi-bold
```

## 🚨 Error Handling

```dart
try {
  final result = await apiService.login(email, password);
  if (result['success']) {
    // Handle success
  } else {
    // Handle API error
    print(result['error']);
  }
} catch (e) {
  // Handle exception
  print('Error: ${e.toString()}');
}
```

## 🎬 Animation Examples

```dart
// Animated gauge (Trust Score)
TrustScoreGauge(
  score: 85.0,
  animated: true,
)

// Pulse animation (Voice recording)
AnimationController(duration: Duration(seconds: 1))
_animation.repeat()

// Loading indicator
LoadingIndicator(message: 'Loading...')
```

## 📊 Widget Tree Example

```dart
Scaffold(
  appBar: AppBar(title: Text('Home')),
  body: SafeArea(
    child: SingleChildScrollView(
      child: Column(
        children: [
          // Trust Score
          TrustScoreGauge(score: 85),
          // Actions
          GridView(...),
          // Transactions
          CustomCard(child: TransactionTile(...)),
        ],
      ),
    ),
  ),
  bottomNavigationBar: BottomNavigationBar(...),
)
```

## 🔗 File References

| Feature | Main File |
|---------|-----------|
| Themes | config/theme.dart |
| Models | models/models.dart |
| API | services/api_service.dart |
| Auth | providers/auth_provider.dart |
| Dashboard | providers/dashboard_provider.dart |
| Chat | providers/chat_provider.dart |
| Voice/OCR | providers/voice_ocr_provider.dart |
| Auth UI | screens/auth_screen.dart |
| Dashboard UI | screens/dashboard_screen.dart |
| Voice UI | screens/voice_screen.dart |
| OCR UI | screens/ocr_screen.dart |
| Chat UI | screens/chat_screen.dart |
| Profile UI | screens/profile_screen.dart |
| Widgets | widgets/custom_widgets.dart |
| Special | widgets/specialized_widgets.dart |
| Formatters | utils/formatters.dart |

## 🌐 Environment Setup

```bash
# Set Flutter channel
flutter channel stable

# Upgrade Flutter
flutter upgrade

# Check setup
flutter doctor

# Analyze project
flutter analyze

# View available devices
flutter devices
```

## 📱 Testing on Device

```bash
# Connect device via USB
adb devices

# Run on device
flutter run

# Run in release mode
flutter run --release

# View device logs
flutter logs

# Reverse port (for remote debugging)
adb reverse tcp:8888 tcp:8888
```

## 💡 Tips & Tricks

- **Hot Reload:** Press `R` to reload code
- **Hot Restart:** Press `Shift+R` to restart app
- **Quit:** Press `Q` to quit
- **DevTools:** Press `D` to open DevTools
- **Screenshots:** Press `S` to save screenshot
- **Performance:** Use `--profile` mode to check
- **Release Size:** Use `--split-per-abi` for APK

## ❌ Common Mistakes to Avoid

- ❌ Forgetting to set IP in api_service.dart
- ❌ Not running backend before testing
- ❌ Using `http://` instead of correct IP
- ❌ Not handling null values in UI
- ❌ Blocking UI with synchronous operations
- ❌ Not disposing controllers/listeners
- ❌ Hardcoding values instead of using theme
- ❌ Not validating API responses

## ✅ Before Deployment

- [ ] Backend IP configured
- [ ] API endpoints tested
- [ ] All screens working
- [ ] Forms validated
- [ ] Error handling implemented
- [ ] Secure storage verified
- [ ] Performance profiled
- [ ] No console errors
- [ ] Code formatted
- [ ] Analysis passed (flutter analyze)

---

**Quick Ref v1.0** | **For:** SmartSync Flutter App | **Updated:** May 2026

