<!-- Quick Reference Card for SmartSync Development -->

# SmartSync Developer Quick Reference

### Terminal 1: Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
# Backend running at http://localhost:8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npx expo start
# Press 'a' for Android, 'i' for iOS, 'w' for web
```

## 📚 File Quick Access

| Purpose | Location |
|---------|----------|
| Main app | `frontend/App.tsx` |
| Navigation | `frontend/src/navigation/RootNavigator.tsx` |
| API client | `frontend/src/api/client.ts` |
| Backend entry | `backend/main.py` |
| Squad APIs | `backend/routes/squad.py` |
| AI APIs | `backend/routes/ai.py` |

## 🎨 UI Screens Location

| Screen | File | Route |
|--------|------|-------|
| Dashboard | `frontend/src/screens/Dashboard.tsx` | Bottom tab |
| Voice Entry | `frontend/src/screens/VoiceERP.tsx` | Bottom tab |
| Capture OCR | `frontend/src/screens/CaptureOCR.tsx` | Bottom tab |
| Squad Pay | `frontend/src/screens/SquadPay.tsx` | Bottom tab |

## 🔌 API Endpoints

### Test Endpoints

```bash
# Backend health
curl http://localhost:8000/health

# API docs
curl http://localhost:8000/docs

# Create virtual account
curl -X POST http://localhost:8000/api/squad/create-virtual-account \
  -H "Content-Type: application/json" \
  -d '{"merchant_id":"test","business_name":"Test","email":"test@test.com","phone":"+234000"}'
```

## 🛠️ Common Tasks

### Add a new screen
1. Create file: `frontend/src/screens/NewScreen.tsx`
2. Add to navigation: `frontend/src/navigation/RootNavigator.tsx`
3. Add route in bottom tab

### Add a new API endpoint
1. Create file: `backend/routes/newroute.py`
2. Add to main: `app.include_router(router, prefix="/api/new")`

### Add a reusable component
1. Create file: `frontend/src/components/MyComponent.tsx`
2. Export from component
3. Import in screens

## 📱 Important Components

### SquadButton
```tsx
<SquadButton
  title="Click me"
  onPress={() => {}}
  variant="primary"  // primary | secondary | danger
  size="medium"      // small | medium | large
  loading={false}
/>
```

### AILoader
```tsx
<AILoader
  visible={loading}
  message="Processing..."
  type="voice"       // voice | ocr | payment
  progress={50}      // 0-100
/>
```

## 🔑 Environment Variables

### Backend (.env)
- `DATABASE_URL` - PostgreSQL connection
- `SQUAD_API_KEY` - Squad payment API key
- `DEBUG` - Debug mode

### Frontend (.env.local)
- `EXPO_PUBLIC_API_URL` - Backend URL (http://localhost:8000/api)

## 📊 Database Models (To implement)

```python
# backend/models/schemas.py
- Transaction
- VirtualAccount
- PaymentLink
- User
- Merchant
```

## 🔐 Next Integration Points

1. **Hero** file for adding new features: `backend/main.py`
2. **Navigation** hub: `frontend/src/navigation/RootNavigator.tsx`
3. **API** client hub: `frontend/src/api/client.ts`

## 🐛 Debugging Tips

### Backend
```bash
# Verbose logging
DEBUG=True python main.py

# Check API endpoints
curl http://localhost:8000/docs
```

### Frontend
```bash
# Clear cache
expo r -c

# Check logs
expo logs
```

## 📱 Mobile Testing

**Android**: `npx expo start --android`
**iOS**: `npx expo start --ios`
**Web**: `npx expo start --web`

## 📚 Documentation Files

- `README.md` - Project overview
- `SETUP.md` - Installation guide
- `CHECKLIST.md` - Implementation tasks
- `BLUEPRINT_SUMMARY.md` - What's included

## 💾 Git Commands

```bash
# Initial commit
git add .
git commit -m "feat: SmartSync blueprint implementation"
git push

# Branch for feature
git checkout -b feature/payment-integration
```

## 🎯 Priority Implementation Order

1. Database setup (PostgreSQL)
2. Squad API integration
3. Authentication
4. AI/OCR services
5. Testing suite
6. Deployment

## ⚡ Performance Tips

- Use React.memo for components
- Lazy load screens
- Cache API responses
- Use requestAnimationFrame for animations
- Monitor bundle size

## 🔗 Resource Links

- FastAPI docs: https://fastapi.tiangolo.com
- React Native: https://reactnative.dev
- Expo: https://expo.dev
- React Navigation: https://reactnavigation.org

## 📞 Support Resources

1. Check main README.md
2. Review SETUP.md
3. Check component documentation in files
4. API docs at `/docs`

---

**Last Updated**: 2026-05-10
**Version**: 1.0.0
**Status**: Ready for Development ✅
