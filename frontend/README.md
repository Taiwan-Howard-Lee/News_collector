# Flutter Frontend - Singapore News Intelligence Dashboard

A modern, cross-platform Flutter application for the Singapore News Intelligence Dashboard. This app provides a beautiful, responsive interface for browsing personalized news content with AI-powered insights.

## 🎯 Features

### ✅ Implemented
- **Modern Material Design 3 UI** with dynamic theming
- **Cross-platform support** (iOS, Android, Web, Desktop)
- **Dark/Light theme** with system preference detection
- **User onboarding** with personalized profile creation
- **Advanced search and filtering** with real-time results
- **Article bookmarking** with local storage
- **Offline support** with intelligent caching
- **Responsive design** that works on all screen sizes
- **Accessibility support** with proper ARIA labels and navigation

### 🚧 In Development
- AI chat interface for article discussions
- Push notifications for relevant articles
- Social sharing functionality
- Advanced analytics and insights
- Voice search capabilities

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.16.0 or higher
- Dart SDK 3.0.0 or higher
- Android Studio / VS Code with Flutter extensions

### Installation

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
flutter pub get
```

3. **Run the app**
```bash
# For development (debug mode)
flutter run

# For specific platforms
flutter run -d chrome          # Web
flutter run -d ios             # iOS Simulator
flutter run -d android         # Android Emulator
flutter run -d macos           # macOS Desktop
```

### Building for Production

```bash
# Android APK
flutter build apk --release

# Web
flutter build web --release

# macOS Desktop
flutter build macos --release
```

## 🛠️ Technology Stack

- **Framework**: Flutter 3.16+
- **Language**: Dart 3.0+
- **State Management**: Riverpod 2.4+
- **Local Storage**: Hive + SharedPreferences
- **HTTP Client**: Dio
- **UI Components**: Material Design 3
- **Theming**: FlexColorScheme
- **Fonts**: Google Fonts (Inter)

## 📱 Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Android | ✅ Full Support | Minimum SDK 21 (Android 5.0) |
| iOS | ✅ Full Support | iOS 12.0+ |
| Web | ✅ Full Support | Modern browsers |
| macOS | ✅ Full Support | macOS 10.14+ |
| Windows | ✅ Full Support | Windows 10+ |

## 🧪 Testing

```bash
# Run tests
flutter test

# Generate coverage
flutter test --coverage
```

## 🤝 Contributing

1. Follow Flutter/Dart style guidelines
2. Add tests for new functionality
3. Ensure all tests pass: `flutter test`
4. Submit a pull request

---

**Built with Flutter 💙 for the Singapore tech community**
