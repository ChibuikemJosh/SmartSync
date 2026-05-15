# Font & Assets Setup Guide

## 🎨 Adding Fonts

The app uses **Google Fonts 'Inter'** for professional typography. The font is loaded dynamically via the `google_fonts` package.

### Font Configuration in pubspec.yaml

```yaml
google_fonts: ^6.1.0
```

The fonts are automatically fetched from Google Fonts API at runtime. No manual font files needed in most cases.

### Manual Font Setup (Optional)

If you want to use local font files:

1. **Create font directory:**
   ```bash
   mkdir -p assets/fonts
   ```

2. **Download Inter fonts from:**
   https://fonts.google.com/specimen/Inter

3. **Save these files to `assets/fonts/`:**
   - Inter-Regular.ttf (weight: 400)
   - Inter-Medium.ttf (weight: 500)
   - Inter-SemiBold.ttf (weight: 600)
   - Inter-Bold.ttf (weight: 700)

4. **Update pubspec.yaml:**
   ```yaml
   fonts:
     - family: Inter
       fonts:
         - asset: assets/fonts/Inter-Regular.ttf
           weight: 400
         - asset: assets/fonts/Inter-Medium.ttf
           weight: 500
         - asset: assets/fonts/Inter-SemiBold.ttf
           weight: 600
         - asset: assets/fonts/Inter-Bold.ttf
           weight: 700
   ```

5. **Use in code:**
   ```dart
   Text(
     'Hello',
     style: TextStyle(fontFamily: 'Inter', fontSize: 16),
   )
   ```

## 🖼️ Creating Assets Structure

### Images Directory

```bash
mkdir -p assets/images
mkdir -p assets/icons
mkdir -p assets/illustrations
mkdir -p assets/logos
```

### Directory Structure

```
assets/
├── images/
│   ├── logo.png
│   ├── icon_*.png
│   └── illustration_*.png
├── icons/
│   ├── ic_home.svg
│   ├── ic_voice.svg
│   ├── ic_ocr.svg
│   ├── ic_chat.svg
│   └── ic_profile.svg
├── illustrations/
│   ├── empty_state.svg
│   ├── error_state.svg
│   └── success_state.svg
└── fonts/
    ├── Inter-Regular.ttf
    ├── Inter-Medium.ttf
    ├── Inter-SemiBold.ttf
    └── Inter-Bold.ttf
```

## 📋 Asset References in pubspec.yaml

```yaml
flutter:
  uses-material-design: true

  assets:
    - assets/images/
    - assets/icons/
    - assets/illustrations/
    - assets/logos/
```

## 🎯 App Icons

### Android Icon

1. **Create icon:**
   - Size: 192x192 px (main)
   - Also create: 48x48, 72x72, 96x96, 144x144, 192x192, 512x512
   - Format: PNG with transparency

2. **Place in Android:**
   ```
   android/app/src/main/res/mipmap-*/
   ic_launcher.png
   ```

3. **Update AndroidManifest.xml:**
   ```xml
   <application
       android:icon="@mipmap/ic_launcher"
       ...
   ```

### iOS Icon

1. **Create icon:**
   - Size: 1024x1024 px
   - Format: PNG with transparency
   - Include App Store icon variations

2. **Place in iOS:**
   ```
   ios/Runner/Assets.xcassets/AppIcon.appiconset/
   ```

3. **Configure in Xcode:**
   - Open ios/Runner.xcworkspace in Xcode
   - Select Assets.xcassets
   - Import icons

## 🎨 Using SVG Icons

SVG icons provide sharp graphics at any size.

### Installation

Already included in pubspec.yaml:
```yaml
flutter_svg: ^2.0.0
```

### Usage

```dart
import 'package:flutter_svg/flutter_svg.dart';

// From asset
SvgPicture.asset(
  'assets/icons/ic_home.svg',
  width: 24,
  height: 24,
  color: AppTheme.primaryColor,
)

// From network
SvgPicture.network(
  'https://example.com/icon.svg',
  width: 24,
  height: 24,
)
```

## 🖼️ Using Network Images

```dart
Image.network(
  'https://example.com/image.png',
  width: 200,
  height: 200,
  fit: BoxFit.cover,
  loadingBuilder: (context, child, progress) {
    if (progress == null) return child;
    return CircularProgressIndicator(
      value: progress.expectedTotalBytes != null
          ? progress.cumulativeBytesLoaded /
              progress.expectedTotalBytes!
          : null,
    );
  },
  errorBuilder: (context, error, stackTrace) {
    return Container(
      color: Colors.grey[300],
      child: Icon(Icons.error),
    );
  },
)
```

## 📦 Image Caching

Configure image caching in main.dart:

```dart
void main() {
  // Configure image cache
  imageCache
    ..maximumSize = 100
    ..maximumSizeBytes = 50 * 1024 * 1024; // 50 MB
  
  runApp(const MyApp());
}
```

## 🎬 Creating App Logo

### Design Specifications

1. **Main Logo (app icon):**
   - 1024x1024 px minimum
   - Should work at 192x192 px
   - All corners rounded to 10%
   - Keep important details away from edges

2. **Splash Screen:**
   - 1920x1080 px
   - Logo centered
   - Background solid color or gradient

3. **App Store Listings:**
   - Feature graphic: 1024x500 px
   - Icon: 512x512 px
   - Screenshots: 1080x1920 px

### Tools

- **Figma** - Design logo: https://figma.com
- **Adobe XD** - Professional design
- **Sketch** - macOS-only design tool
- **Inkscape** - Free vector editor

## 🎨 Using Custom Colors in SVGs

```dart
// SVG with color override
SvgPicture.asset(
  'assets/icons/ic_home.svg',
  color: AppTheme.primaryColor,
  colorBlendMode: BlendMode.srcIn,
)
```

## 📸 Loading Local Images

```dart
// From assets
Image.asset(
  'assets/images/logo.png',
  width: 200,
  height: 200,
  fit: BoxFit.contain,
)

// From file
import 'dart:io';

Image.file(
  File('/path/to/image.png'),
  width: 200,
  height: 200,
)
```

## 🎬 Splash Screen Setup

### Android

1. **Edit `android/app/src/main/AndroidManifest.xml`:**
   ```xml
   <activity
       android:name=".MainActivity"
       android:theme="@style/LaunchTheme"
       ...
   ```

2. **Create `android/app/src/main/res/values/styles.xml`:**
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <resources>
       <style name="LaunchTheme" parent="@android:style/Theme.Black.NoTitleBar">
           <item name="android:windowBackground">@drawable/launch_background</item>
       </style>
   </resources>
   ```

3. **Place splash image in `mipmap` folders**

### iOS

1. **Open `ios/Runner.xcworkspace` in Xcode**
2. **Select Runner → Assets.xcassets**
3. **Drag splash image to LaunchScreen**

## 🎨 Dynamic Icon Generation

Generate app icons from a base image:

```bash
# Using flutter_launcher_icons
flutter pub add flutter_launcher_icons

# Configuration in pubspec.yaml
flutter_launcher_icons:
  android: true
  ios: true
  image_path: "assets/app_icon.png"

# Generate
flutter pub run flutter_launcher_icons:main
```

## 🌈 Asset Loading Best Practices

1. **Compress images** - Reduce file size
2. **Use appropriate formats:**
   - PNG - For icons and transparent images
   - JPG - For photos
   - SVG - For scalable icons
   - WebP - For better compression
3. **Optimize resolution** - Match screen DPI
4. **Use asset variants** - Different densities
5. **Lazy load images** - Don't load all at once

## 📊 Asset File Size Guide

| Type | Format | Max Size |
|------|--------|----------|
| App Icon | PNG | 1-2 MB |
| Splash Screen | PNG/JPG | 2-3 MB |
| User Avatar | JPG | 500 KB |
| Illustration | SVG | 100 KB |
| Icon | SVG | 20 KB |
| Background | JPG | 500 KB |

## ✅ Asset Checklist

- [ ] `assets/` directories created
- [ ] Images optimized for web
- [ ] Icons in SVG format
- [ ] App icon 1024x1024 px
- [ ] Fonts configured in pubspec.yaml
- [ ] Assets declared in pubspec.yaml
- [ ] All image paths correct in code
- [ ] No hardcoded asset sizes
- [ ] Image caching configured
- [ ] Splash screen designed

## 🚀 Performance Tips

- **Use SVG for icons** - Smaller file size
- **Compress images** - Reduce APK/IPA size
- **Lazy load images** - Load on demand
- **Cache network images** - Avoid re-downloading
- **Use fit property** - Prevent stretching/distortion

## 📦 Optimizing APK Size

```bash
# Build APK with size info
flutter build apk --analyze-size

# Build separate APKs per architecture
flutter build apk --split-per-abi

# Check APK contents
unzip -l app-release.apk | grep "assets/"
```

## 🎨 Custom App Fonts in Text

```dart
// Using google_fonts
import 'package:google_fonts/google_fonts.dart';

Text(
  'Hello World',
  style: GoogleFonts.inter(
    fontSize: 20,
    fontWeight: FontWeight.bold,
    color: AppTheme.primaryColor,
  ),
)
```

---

**Font & Assets Guide v1.0** | **For:** SmartSync Flutter App

