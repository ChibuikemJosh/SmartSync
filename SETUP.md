# SmartSync Setup Guide

Quick setup guide for getting SmartSync up and running.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Git
- Expo CLI (`npm install -g expo-cli`)

## Backend Setup (FastAPI)

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create environment file
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run the backend
```bash
python main.py
```

The backend will start on `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup (React Native)

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Create environment file
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 4. Start the Expo development server
```bash
npx expo start
```

### 5. Run on your platform

- **Android**: Press `a` in terminal or run `npx expo start --android`
- **iOS**: Press `i` in terminal or run `npx expo start --ios`
- **Web**: Press `w` in terminal or run `npx expo start --web`

## Project Structure Quick Reference

```
backend/          → FastAPI REST API
  main.py         → Entry point
  routes/         → API endpoints
  services/       → Business logic
  models/         → Data schemas
  utils/          → Helper functions

frontend/         → React Native app
  src/screens/    → Application screens
  src/components/ → Reusable components
  src/api/        → API client & services
  src/navigation/ → Navigation setup
```

## Available Scripts

### Backend
```bash
python main.py                    # Run development server
```

### Frontend
```bash
npm start                         # Start Expo dev server
npx expo start --android          # Start Android emulator
npx expo start --ios              # Start iOS simulator
npx expo start --web              # Start web preview
npm run lint                      # Run ESLint
npm run type-check               # Check TypeScript
```

## API Integration

The frontend uses a centralized API client at `frontend/src/api/client.ts`

**Key API Services:**
- `squad.ts` - Squad payment endpoints
- `ai.ts` - Voice & OCR endpoints

All requests automatically:
- Handle errors
- Add authentication headers
- Timeout after 30 seconds

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://...
NEO4J_URI=bolt://...
SQUAD_API_KEY=...
DEBUG=False
```

### Frontend (.env.local)
```
EXPO_PUBLIC_API_URL=http://localhost:8000/api
EXPO_PUBLIC_APP_ENV=development
```

## Database Setup (Optional)

For full functionality, setup:

1. **PostgreSQL**
```bash
createdb smartsync
```

2. **Neo4j**
```bash
docker run -p 7687:7687 -p 7474:7474 neo4j
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Verify all dependencies: `pip list`
- Check if port 8000 is available

### Frontend build errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Expo cache: `expo r -c`
- Check Node version: `node --version` (need 16+)

### API connection errors
- Verify backend is running on correct port
- Check `EXPO_PUBLIC_API_URL` in `.env.local`
- Ensure CORS is enabled in backend

## Next Steps

1. **Configure Databases**: Set up PostgreSQL and Neo4j
2. **Add AI Services**: Integrate speech-to-text and OCR APIs
3. **Setup Squad API**: Add your Squad API credentials
4. **Deploy**: Follow deployment guide for production setup

## Support

For issues or questions:
1. Check the main README.md
2. Review API documentation at `/docs`
3. Check component documentation in source files

---

**Ready to go!** 🚀 Start building with SmartSync
