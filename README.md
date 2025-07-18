# Air Travel Agent

This project is an AI-powered airline assistant with a FastAPI backend and a modern React/Next.js frontend.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repo-url>
cd air-travel-agent
```

### 2. Backend Setup (`air-backend`)
- Install dependencies:
  ```bash
  cd air-backend
  pip install -r requirements.txt
  ```
- Create a `.env` file in `air-backend/` with the following variables:
  ```env
  # Gemini API Key (required for LLM calls)
  GEMINI_API_KEY=your_gemini_api_key_here

  # OpenAI API Key (optional, if using OpenAI models)
  OPENAI_API_KEY=your_openai_api_key_here

  # MongoDB connection URI
  MONGODB_URI=mongodb://localhost:27017
  ```
- Start the backend:
  ```bash
  uvicorn main:app --reload
  ```

### 3. Frontend Setup (`airline-chatbot-frontend`)
- Install dependencies:
  ```bash
  cd airline-chatbot-frontend
  npm install
  # or
  yarn install
  ```
- Start the frontend:
  ```bash
  npm run dev
  # or
  yarn dev
  ```

### 4. Environment Variables Summary
| Variable         | Description                        | Required | Example Value                  |
|------------------|------------------------------------|----------|-------------------------------|
| GEMINI_API_KEY   | Gemini LLM API Key                 | Yes      | `your_gemini_api_key_here`    |
| OPENAI_API_KEY   | OpenAI API Key (if using OpenAI)   | Optional | `sk-...`                      |
| MONGODB_URI      | MongoDB connection string          | Yes      | `mongodb://localhost:27017`   |

### 5. Notes
- The backend uses Gemini API by default for LLM calls. You can switch to OpenAI by providing the `OPENAI_API_KEY` and updating the code if needed.
- Ensure your MongoDB instance is running and accessible.
- The frontend expects the backend to run on `http://localhost:8000` by default.

---

For any issues, please check the logs or open an issue in the repository. 