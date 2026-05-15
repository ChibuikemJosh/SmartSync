# SmartSync Flutter App - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Flutter SDK 3.0+ ([Install Flutter](https://flutter.dev/docs/get-started/install))
- Dart 3.0+
- Android Studio or Xcode (for emulator/device testing)
- Backend API running at http://YOUR_IP:8000

### Step 1: Clone/Navigate to Project
```bash
cd /workspaces/SmartSync/frontend_new
```

### Step 2: Install Dependencies
```bash
flutter pub get
```

### Step 3: Configure Backend IP
Edit `lib/services/api_service.dart`:
```dart
// Line ~9
static const String baseUrl = 'http://192.168.1.100:8000'; // Change to your IP
```

### Step 4: Run the App
```bash
# Android
flutter run

# iOS (macOS only)
flutter run -d ios

# Web
flutter run -d web
```

## 📱 Platform-Specific Setup

### Android Setup

1. **Install Android SDK:**
   ```bash
   flutter doctor -v
   # Follow any missing component instructions
   ```

2. **Create Android Virtual Device:**
   ```bash
   flutter emulators
   flutter emulators create --name smartsync_emulator
   flutter emulators launch smartsync_emulator
   ```

3. **Run on Emulator:**
   ```bash
   flutter run
   ```

4. **Run on Physical Device:**
   - Enable Developer Mode on phone
   - Connect device via USB
   - Allow USB debugging
   ```bash
   flutter devices  # Verify device appears
   flutter run
   ```

### iOS Setup (macOS only)

1. **Install CocoaPods:**
   ```bash
   sudo gem install cocoapods
   ```

2. **Open iOS Project:**
   ```bash
   open ios/Runner.xcworkspace
   ```

3. **Configure Signing:**
   - In Xcode: Select Runner > Signing & Capabilities
   - Choose your Apple Team ID
   - Update Bundle ID if needed

4. **Run on Simulator:**
   ```bash
   flutter run -d ios
   ```

5. **Run on Device:**
   ```bash
   flutter devices
   flutter run -d <device-id>
   ```

## 🔧 Configuration

### Backend Connection

1. **Find Your Machine IP:**
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```

2. **Update API Service:**
   ```dart
   // lib/services/api_service.dart
   static const String baseUrl = 'http://YOUR_MACHINE_IP:8000';
   ```

3. **Verify Backend is Running:**
   ```bash
   curl http://192.168.1.100:8000/health
   # Should return 200 OK
   ```

### Environment Variables

Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your configuration.

## 🧪 Testing

### Run Tests
```bash
flutter test
```

### Test Specific File
```bash
flutter test test/services/api_service_test.dart
```

### Code Coverage
```bash
flutter test --coverage
```

## 🔍 Debugging

### Debug Mode
```bash
flutter run  # Default debug mode
```

### Release Mode
```bash
flutter run --release
```

### Profile Mode (Performance)
```bash
flutter run --profile
```

### DevTools
```bash
flutter pub global activate devtools
flutter pub global run devtools
```

Then open: http://localhost:9100

### Hot Reload
- Press `R` after changes
- Press `Shift+R` for hot restart

## 📦 Build for Distribution

### Android APK
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-app-release.apk
```

### Android App Bundle
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS Archive
```bash
flutter build ios --release
# Use Xcode to create IPA
```

## 🛠️ Common Issues & Solutions

### Issue: "flutter: command not found"
**Solution:**
```bash
# Add Flutter to PATH
export PATH="$PATH:`pwd`/flutter/bin"
```

### Issue: "Cannot connect to API"
**Solution:**
1. Check backend is running: `curl http://IP:8000/health`
2. Verify IP address in `api_service.dart`
3. Check network connectivity
4. Ensure firewall allows port 8000

### Issue: "Gradle build failed"
**Solution:**
```bash
flutter clean
flutter pub get
flutter run
```

### Issue: "CocoaPods error"
**Solution (macOS):**
```bash
cd ios
pod repo update
pod install
cd ..
flutter run -d ios
```

### Issue: "Emulator won't start"
**Solution:**
```bash
flutter emulators
flutter emulators create --name new_emulator
flutter emulators launch new_emulator
```

### Issue: "Hot reload not working"
**Solution:**
- Press `R` to hot reload
- Press `Shift+R` for full restart
- Use `flutter run` again if issues persist

## 📋 Development Checklist

- [ ] Flutter installed and verified (`flutter doctor`)
- [ ] Backend API configured and running
- [ ] Backend IP set in `api_service.dart`
- [ ] Dependencies installed (`flutter pub get`)
- [ ] Can run on device/emulator (`flutter run`)
- [ ] API calls working (check auth endpoints)
- [ ] Login with demo account works
- [ ] All screens load without errors
- [ ] Voice input can be triggered
- [ ] Chat sends messages
- [ ] Profile shows user data

## 🔐 Security Setup

### Store Sensitive Data
```dart
// Use Flutter Secure Storage (already configured)
final secureStorage = const FlutterSecureStorage();
await secureStorage.write(key: 'token', value: myToken);
```

### API Authentication
- Tokens are automatically stored securely
- Refresh tokens on expiration
- Clear storage on logout

## 📱 Testing Demo Flow

1. **Launch App:**
   ```bash
   flutter run
   ```

2. **Login:**
   - Email: `demo@smartsync.com`
   - Password: `Demo@123456`

3. **Test Features:**
   - ✅ View Dashboard with Trust Score
   - ✅ View Recent Transactions
   - ✅ Record Voice (press & hold mic)
   - ✅ Upload Ledger Image
   - ✅ Chat with AI
   - ✅ View Profile

## 📊 Project Statistics

- **Total Lines of Code:** ~3000+
- **Screens:** 5 (Auth, Dashboard, Voice, OCR, Chat, Profile)
- **API Endpoints:** 10+
- **Custom Widgets:** 15+
- **Providers:** 4
- **Models:** 4

## 🎨 Theme Customization

Edit `lib/config/theme.dart`:

```dart
// Change primary color
static const Color primaryColor = Color(0xFF1A237E);

// Change font
AppTextStyles.bodyMedium.copyWith(fontFamily: 'YourFont')

// Change spacing
static const double md = 16.0;
```

## 📚 Useful Commands

```bash
# List all devices/emulators
flutter devices

# Clean build
flutter clean

# Analyze code
flutter analyze

# Format code
dart format lib/

# Get package info
flutter pub info

# Update packages
flutter pub upgrade

# Check Flutter version
flutter --version

# Generate code coverage
flutter test --coverage

# Profile app
flutter run --profile
```

## 🚀 Deployment

### Play Store (Android)
1. Create Google Play Developer account
2. Generate signing key
3. Build app bundle: `flutter build appbundle --release`
4. Upload to Play Store Console

### App Store (iOS)
1. Create Apple Developer account
2. Set up certificates
3. Build iOS: `flutter build ios --release`
4. Upload via Xcode/Transporter

## 📞 Support

For issues or questions:
1. Check Flutter documentation: https://flutter.dev/docs
2. Review Dart documentation: https://dart.dev/guides
3. Check Provider package docs
4. Review API service logs

## ✅ Completion Checklist

- [ ] All dependencies installed
- [ ] Backend API configured
- [ ] App runs on device/emulator
- [ ] Can login with demo account
- [ ] All screens display correctly
- [ ] API calls work properly
- [ ] Voice and OCR features functional
- [ ] Chat interface responsive
- [ ] Profile page displays user data
- [ ] No console errors

---

**Version:** 1.0.0
**Last Updated:** May 2026
**For:** SmartSync Flutter Development

