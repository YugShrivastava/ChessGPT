# Setup Guide

Follow these steps to set up and run the project.

---

## 1. Environment Variables

Create a `.env` file in the root directory of the project with the following variables:

```env
STOCKFISH_PATH=/absolute/path/to/stockfish
GOOGLE_API_KEY=your_gemini_2.5_flash_api_key
```

- **STOCKFISH_PATH** → Provide the **absolute path** to your locally downloaded Stockfish binary.  
- **GOOGLE_API_KEY** → Provide your **Google Gemini 2.5 Flash API key**.  

---

## 2. Install Dependencies

It is recommended to use a Python virtual environment.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # On Linux/Mac
venv\Scripts\activate       # On Windows

# Install required dependencies
pip install -r requirements.txt
```

---

## 3. Run the FastAPI Server

Start the development server using:

```bash
fastapi dev main.py
```

The server should now be running locally (default: `http://127.0.0.1:8000`).

---

## 4. API Usage

### Endpoint: `/analyze`

- **Method:** `POST`  
- **Body Parameter:** `fen` (string)  

Example Request:

```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
}
```

### Response:

The server will return feedback about the given chess position based on Stockfish analysis and Gemini insights.

---

✅ You are now ready to use the project!
