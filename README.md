# AgroLink - AI-Powered Farming Assistant

AgroLink is a comprehensive platform designed to assist farmers with crop recommendations, fertilizer advice, weather information, and more. The platform features an AI-powered chatbot that can answer farming-related questions in multiple Indian languages.

## Project Structure

```
agrolink/
├── agrolink-backend/     # FastAPI backend with AI chatbot
├── agrolink-frontend/    # React frontend application
└── README.md            # This file
```

## Features

- **AI Chatbot**: Multilingual assistant for farming questions
- **Crop Recommendation**: Get suggestions based on soil and climate conditions using machine learning
- **Fertilizer Guide**: Information on proper fertilizer usage
- **Weather Information**: Location-based weather forecasts
- **Marketplace**: Platform for buying and selling agricultural products
- **Plant Disease Detection**: Identify and get treatment for plant diseases

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Google Gemini API key

## Backend Setup

### Option 1: Manual Setup

1. Navigate to the backend directory:
   ```bash
   cd agrolink-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Option 2: Windows Batch Scripts

1. Navigate to the backend directory:
   ```bash
   cd agrolink-backend
   ```

2. Run the setup script:
   ```bash
   setup.bat
   ```

3. Create a `.env` file with your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. Run the server:
   ```bash
   run.bat
   ```

## Frontend Setup

### Option 1: Manual Setup

1. Navigate to the frontend directory:
   ```bash
   cd agrolink-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### Option 2: Windows Batch Scripts

1. Navigate to the frontend directory:
   ```bash
   cd agrolink-frontend
   ```

2. Run the setup script:
   ```bash
   setup.bat
   ```

3. Run the development server:
   ```bash
   run.bat
   ```

## Usage

1. Start both the backend and frontend servers
2. Open your browser and navigate to `http://localhost:3000`
3. Use the chatbot to ask farming-related questions in your preferred language

## API Endpoints

- `GET /` - Health check endpoint
- `POST /api/chatbot/ask` - Ask the AI chatbot a question
- `POST /api/crop/predict` - Get crop recommendation based on soil and climate conditions

## Supported Languages

- English (en)
- Hindi (hi)
- Odia (or)
- Bengali (bn)
- Tamil (ta)
- Telugu (te)
- Kannada (kn)
- Marathi (mr)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.