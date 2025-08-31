# fiMoney2

fiMoney2 is a modern, AI-native personal finance assistant with a secure backend and interactive frontend. It provides privacy-preserving financial insights using Fi's Model Context Protocol (MCP) and Google Gemini, and offers a feature-rich React user interface.

---

## Features

- **Secure Authentication** (JWT-based with refresh tokens)
- **User Management** (self-service registration & profile)
- **Net Worth Tracking** (history & forecast)
- **Portfolio Analysis** (multi-asset performance)
- **Expense Insights** (categorization & analytics)
- **Loan Affordability** (simulations)
- **Goal Planning** (projections & tracking)
- **Anomaly Detection** (unusual spend/fraud alerts)
- **Rich Frontend** (React app for intuitive user experience)

---

## Technologies Used

- **Backend:** Python 3.9+, FastAPI, PostgreSQL/SQLite, MCP, Google Gemini
- **Frontend:** React (Create React App)

---

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- PostgreSQL (recommended) or SQLite
- Node.js & npm (for React frontend)
- Fi MCP API credentials
- Google Gemini API key

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/AgamJK/fiMoney2.git
cd fiMoney2
```

### 2. Backend Setup

- Create and activate a python virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```
- Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
- Copy and edit the environment file:
    ```bash
    cp .env.example .env
    ```
    Update `.env` with at least:
    ```env
    # Security
    SECRET_KEY=your_secret_key

    # Database
    DATABASE_URL=sqlite:///./sql_app.db
    # or
    DATABASE_URL=postgresql://user:password@localhost:5432/fi_gemini_finance

    # Superuser
    FIRST_SUPERUSER_EMAIL=admin@example.com
    FIRST_SUPERUSER_PASSWORD=changethis

    # MCP & Gemini
    MCP_API_KEY=your_mcp_api_key
    MCP_API_URL=https://api.mcp.fi
    GEMINI_API_KEY=your_gemini_api_key
    ```
- Initialize the database and create a superuser:
    ```bash
    python scripts/init_db.py
    ```
- Start the backend server:
    ```bash
    uvicorn app.main:app --reload
    ```
    Access API at [http://localhost:8000](http://localhost:8000) and docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Frontend Setup

- Navigate to the frontend directory (adjust if necessary):
    ```bash
    cd frontend
    ```
- Install dependencies:
    ```bash
    npm install
    ```
- Start the React app:
    ```bash
    npm start
    ```
    App runs at [http://localhost:3000](http://localhost:3000).

---

## Usage

- Register and log in via the React frontend or the API endpoints.
- Use financial features from the dashboard.
- For API usage, most endpoints require JWT authentication:
    ```
    Authorization: Bearer <your-jwt-token>
    ```

---

## Project Structure

```
fiMoney2/
├── app/           # Backend application (FastAPI)
├── frontend/      # React frontend
├── scripts/       # Utility scripts
├── tests/         # Backend tests
├── .env.example   # Example env vars
├── requirements.txt
├── README.md
```

---

## Running Tests

- Backend tests:
    ```bash
    pytest
    ```
- Frontend tests:
    ```bash
    npm test
    ```

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting PRs.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support

For help, open an issue or contact the development team.
