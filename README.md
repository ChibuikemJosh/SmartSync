# SmartSync - Intelligent Economy Engine 🚀

A full-stack smart economic platform for the Squad Hackathon 3.0, designed to digitize informal traders using Voice-ERP, OCR technology, and Squad payment APIs.

## 🎯 Project Goal

Empower informal traders with digital tools:
- **Voice-ERP**: Convert spoken transactions to structured data
- **OCR Processing**: Digitize physical ledgers through image recognition
- **Smart Dashboard**: Real-time transaction monitoring and analytics
- **Squad Integration**: Seamless payment processing and virtual accounts

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python) with async/await support
- PostgreSQL & Neo4j (Graph database placeholders)
- RESTful API architecture

**Frontend:**
- React Native with Expo
- TypeScript for type safety
- NativeWind (Tailwind CSS for native apps)
- React Navigation (Stack + Bottom Tab)

## 📁 Project Structure

```
SmartSync/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt         # Python dependencies
│   ├── routes/
│   │   ├── squad.py           # Squad payment endpoints
│   │   ├── ai.py              # Voice & OCR endpoints
│   │   └── health.py          # Health check endpoints
│   ├── services/              # Business logic layer
│   ├── models/                # Data models & schemas
│   └── utils/                 # Helper functions
│
└── frontend/
    ├── App.tsx                # Main application file
    ├── package.json           # Dependencies
    ├── app.json              # Expo configuration
    ├── tsconfig.json         # TypeScript configuration
    ├── tailwind.config.js    # Tailwind CSS config
    ├── src/
    │   ├── screens/
    │   │   ├── Dashboard.tsx      # Main dashboard screen
    │   │   ├── VoiceERP.tsx       # Voice transaction entry
    │   │   ├── CaptureOCR.tsx     # Ledger image capture
    │   │   └── SquadPay.tsx       # Payment management
    │   ├── components/
    │   │   ├── SquadButton.tsx    # Reusable button
    │   │   └── AILoader.tsx       # Loading indicator
    │   ├── api/
    │   │   ├── client.ts         # Centralized Axios instance
    │   │   ├── squad.ts          # Squad API services
    │   │   └── ai.ts             # AI processing services
    │   ├── navigation/
    │   │   └── RootNavigator.tsx # Navigation setup
    │   ├── types/                # TypeScript types
    │   └── utils/                # Utility functions
    └── assets/                   # Images & icons
```

## 🔌 Backend API Endpoints

### Squad Routes (`/api/squad`)
- `POST /create-virtual-account` - Create merchant virtual account
- `POST /generate-payment-link` - Generate payment links
- `GET /transactions/{merchant_id}` - Retrieve transaction history

### AI Routes (`/api/ai`)
- `POST /process-voice` - Convert speech to transaction JSON
- `POST /process-ocr` - Extract data from ledger images
- `GET /voice-status/{job_id}` - Check voice processing status
- `GET /ocr-status/{job_id}` - Check OCR processing status

### Health Routes
- `GET /health` - Service health status
- `GET /ready` - Service readiness check

## 🚀 Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend will run on `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd frontend
npm install
npx expo start
```

**Running on different platforms:**
```bash
npx expo start --android    # Android emulator
npx expo start --ios        # iOS simulator
npx expo start --web        # Web browser
```

## 🎨 Key Features

### Dashboard
- Account balance display
- Recent transaction list
- Quick action buttons
- "Intelligent Economy" theme

### Voice Entry (VoiceERP)
- Large accessible microphone button
- Real-time recording timer
- AI-powered speech-to-JSON conversion
- Transaction preview before saving
- Tips for optimal recording

### Ledger Capture (OCR)
- Camera integration for document photography
- Image gallery selection option
- Automatic data extraction
- Entry list with amounts
- Total calculation

### Squad Payment
- Virtual account management
- Payment link generation
- Account details display
- Transaction history
- Balance monitoring

## 📱 UI Components

### SquadButton
Customizable button component with variants:
- Variants: `primary`, `secondary`, `danger`
- Sizes: `small`, `medium`, `large`
- Loading states
- Disabled states

### AILoader
Loading indicator with animated status:
- Types: `voice`, `ocr`, `payment`
- Progress tracking
- Custom messages
- Smooth animations

## 🔐 API Client

Centralized Axios instance in `/src/api/client.ts`:
- Automatic error handling
- Request/response interceptors
- Bearer token management (placeholder)
- Timeout configuration

## 🛠️ Development

### Environment Variables

**Backend (.env):**
```
DATABASE_URL=postgresql://user:password@localhost/smartsync
NEO4J_URI=bolt://localhost:7687
SQUAD_API_KEY=your_squad_api_key
```

**Frontend (.env):**
```
EXPO_PUBLIC_API_URL=http://localhost:8000/api
```

### Code Quality
- TypeScript for type safety
- ESLint for code linting
- Proper error handling
- Comprehensive documentation

## 📊 Expected Data Flow

```
User Input (Voice/Image)
    ↓
Frontend Capture
    ↓
Send to Backend API
    ↓
AI Processing (Voice-to-JSON / OCR-to-JSON)
    ↓
Structured Transaction Data
    ↓
Squad Payment Processing
    ↓
Database Storage
    ↓
Dashboard Update
```

## 🔄 Integration Points

1. **Speech-to-Text**: Integrate with Google Cloud Speech-to-Text or similar
2. **OCR Service**: Connect to Tesseract or Google Cloud Vision
3. **Squad APIs**: Implement virtual account and payment link endpoints
4. **Database**: Configure PostgreSQL and Neo4j connections

## 📝 Notes

- All API calls use centralized Axios client for consistency
- Components are reusable and prop-driven
- Clean code with proper documentation
- Follows React and FastAPI best practices
- TypeScript for enhanced type safety

## 🎓 Theme: Intelligent Economy

SmartSync represents the future of informal commerce:
- **Digitization**: Transform paper-based systems to digital
- **Intelligence**: AI-powered data extraction and processing
- **Accessibility**: Voice and image-based input for ease of use
- **Integration**: Seamless payment processing
- **Empowerment**: Tools for traders to grow their business

## 📄 License

See LICENSE file for details

---

**Built for Squad Hackathon 3.0** 🚀

Made with ❤️ for the informal economy
