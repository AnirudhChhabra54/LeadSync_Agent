# LeadSync Agent 📇

LeadSync Agent is a production-ready, AI-powered conversational agent designed to seamlessly digitize physical visiting cards, manage sales contacts, and append voice notes directly into a Google Sheets CRM.

Built with an asynchronous FastAPI backend and a modern React frontend, this project leverages LangGraph to orchestrate a highly reliable, interrupt-driven human-in-the-loop (HITL) workflow.

## 🚀 Features

- **Multimodal AI Extraction:** Upload an image of a visiting card. The agent uses Google's `gemini-flash-latest` vision model to intelligently extract the Name, Phone, Email, Company, and Designation into structured JSON.
- **Human-in-the-Loop Confirmation:** Before any data is permanently saved, the workflow pauses, allowing the user to review, edit, or reject the extracted contact details via the React UI.
- **Intelligent Deduplication:** Automatically checks the connected Google Sheet for existing contacts using normalized phone numbers and emails to prevent CRM clutter.
- **Background Company Enrichment:** Automatically infers the company's website or LinkedIn presence using LLM reasoning.
- **Audio Voice Notes:** Once a contact is synced, users can upload an audio voice note detailing the context of the meeting. The agent transcribes the audio, summarizes it, uploads the raw file to Cloudinary, and links both the URL and summary to the specific row in Google Sheets.
- **Session Management:** Robust session tracking using MongoDB ensures context is maintained across page reloads and multiple parallel conversations.

## 🛠️ Architecture & Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Agent Orchestration:** LangChain & LangGraph (StateGraph, Checkpointing)
- **AI/LLM:** Google Gemini API (`gemini-flash-latest` for Vision & Audio)
- **Database:** MongoDB Atlas (for LangGraph state persistence and session tracking)
- **CRM Integration:** Google Sheets API (`gspread`)
- **Cloud Storage:** Cloudinary (Audio hosting)

### Frontend
- **Framework:** React.js (Vite)
- **Styling:** Vanilla CSS with modern Glassmorphism aesthetics
- **Icons:** React Icons (Lucide)
- **Audio Processing:** `react-audio-voice-recorder`

## ⚙️ Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Google Cloud Project with the Google Sheets API enabled and a Service Account JSON.
- MongoDB Atlas cluster URL.
- Gemini API Key.
- Cloudinary Account.

### Environment Variables
Create a `.env` file in the root of the project:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://<user>:<password>@cluster...

# Google Sheets
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Starting the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Starting the Frontend
```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

## 🧠 LangGraph Workflow Design
The backend agent operates on a cyclic `StateGraph` that transitions through distinct nodes:
1. `extract_card_data`: Parses the incoming image via Gemini Vision.
2. `enrich_company`: (Parallel) Derives company metadata.
3. `confirm_with_user`: **Interrupt Node.** Yields control back to the frontend awaiting the user's manual approval of the extracted payload.
4. `deduplicate_contact`: Checks the target Google Sheet for existing records.
5. `write_to_sheets`: Appends the verified, unique contact.
6. `process_voice_note`: (Conditional) If audio is received, transcodes to base64, fetches a summary, uploads to Cloudinary, and updates the specific row in Google Sheets.

## 📝 License
This project is open-source and available under the MIT License.
