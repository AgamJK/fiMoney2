# Fi MCP + Gemini Personal Finance Agent

An AI-native personal finance assistant that provides secure, privacy-preserving financial insights using Fi's Model Context Protocol (MCP) and Google Gemini.

## Features

- **Secure Authentication**: JWT-based authentication with refresh tokens
- **User Management**: Self-service user registration and profile management
- **Net Worth Tracking**: View historical net worth trends and forecasts
- **Portfolio Analysis**: Analyze investment performance across asset classes
- **Expense Insights**: Categorize and analyze spending patterns
- **Loan Affordability**: Simulate loan scenarios and check affordability
- **Goal Planning**: Plan and track financial goals with projections
- **Anomaly Detection**: Identify unusual spending and potential fraud

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- PostgreSQL (recommended) or SQLite
- Fi MCP API credentials
- Google Gemini API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/fi-gemini-finance.git
   cd fi-gemini-finance
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update it with your credentials:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file with your actual credentials. The minimum required settings are:
   ```env
   # Security
   SECRET_KEY=generate-with-openssl-rand-hex-32
   
   # Database
   DATABASE_URL=sqlite:///./sql_app.db  # or PostgreSQL: postgresql://user:password@localhost:5432/fi_gemini_finance
   
   # First Superuser (change these!)
   FIRST_SUPERUSER_EMAIL=admin@example.com
   FIRST_SUPERUSER_PASSWORD=changethis
   
   # MCP Configuration
   MCP_API_KEY=your_mcp_api_key
   MCP_API_URL=https://api.mcp.fi
   
   # Gemini Configuration
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. Initialize the database and create the first superuser:
   ```bash
   python scripts/init_db.py
   ```

## Running the Application

1. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

3. Access the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/access-token` - Login and get access token
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/refresh-token` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `POST /api/v1/users/me/password` - Change password

### Net Worth
- `GET /api/v1/net-worth/` - Get net worth data and trends

### Portfolio
- `GET /api/v1/portfolio/analysis` - Analyze investment portfolio

### Expenses
- `GET /api/v1/expenses/analysis` - Analyze spending patterns

### Simulations
- `POST /api/v1/simulations/loan-affordability` - Simulate loan affordability
- `POST /api/v1/simulations/goal-planning` - Plan financial goals

## Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer your-jwt-token-here
```

To get a token:

1. Register a new user:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepassword", "full_name": "John Doe"}'
   ```

2. Login to get tokens:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=securepassword"
   ```

3. Use the access token in subsequent requests:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer your-access-token"
   ```

## Development

### Project Structure

```
fi-gemini-finance/
├── app/
│   ├── api/                  # API routes
│   ├── core/                 # Core configurations
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic models
│   ├── services/             # Business logic
│   └── utils/                # Helper functions
├── tests/                    # Test cases
├── scripts/                  # Utility scripts
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## Support

For support, please open an issue in the GitHub repository or contact the development team.
