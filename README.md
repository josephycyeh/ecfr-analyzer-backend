# eCFR Backend API

A Flask-based REST API that provides analytics and data about federal regulations from the Electronic Code of Federal Regulations (eCFR).

## Features

- Agency statistics and hierarchy
- Word count and section analysis
- Historical corrections tracking
- RESTful API endpoints
- PostgreSQL database integration

## API Endpoints

- `GET /api/agencies` - List all agencies with their statistics
- `GET /api/agencies/<slug>` - Get detailed information about a specific agency and its child agencies
- `GET /api/statistics/total` - Get aggregate statistics across all agencies
- `GET /api/corrections` - Get historical correction data by year
- `GET /api/health` - Health check endpoint

## Prerequisites

- Python 3.11.7 or higher
- PostgreSQL 12 or higher
- pip and virtualenv

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/josephycyeh/ecfr-analyzer-backend.git
cd eCFR-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

5. Create the database:
```bash
createdb ecfr
```

6. Create a `.env` file in the project root:
```
FLASK_ENV=development
PORT=5001

DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecfr
DB_USER=postgres
DB_PASSWORD=postgres
```

7. Initialize the database and import data:
```bash
python init_db.py
```

8. Run the development server:
```bash
python app.py
```

The API will be available at `http://localhost:5001`

## Deployment to Heroku

1. Install the Heroku CLI and login:
```bash
brew tap heroku/brew && brew install heroku
heroku login
```

2. Create a new Heroku app:
```bash
heroku create ecfr-backend
```

3. Add PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:mini
```

4. Set environment variables:
```bash
heroku config:set FLASK_ENV=production
```

5. Deploy the application:
```bash
git push heroku main
```

6. Initialize the database:
```bash
heroku run python init_db.py
```

## Data Processing

The application processes eCFR data by:
1. Fetching agency information from the eCFR API
2. Downloading and parsing XML content for each title
3. Computing word counts and section numbers
4. Tracking historical corrections
5. Storing processed data in PostgreSQL

## Project Structure

- `app.py` - Main Flask application and API routes
- `config.py` - Configuration management
- `db.py` - Database connection and query utilities
- `init_db.py` - Database initialization script
- `main.py` - Data processing utilities
- `schema.sql` - Database schema
- `services/` - Business logic and data services
  - `agency_service.py` - Agency-related operations
  - `corrections_service.py` - Corrections data handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
