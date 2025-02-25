# eCFR Backend API

## Overview:
REST-API built on Flask for https://ecfr-frontend-1b42d1c0ad44.herokuapp.com/
The API is used to fetch agency information and statistics. It includes a script to initialize the database and import the data from the eCFR API, so that the data is pre-computed and the API can serve the data quickly.

## API Endpoints

- `GET /api/agencies` - List all top level agencies with their stats
- `GET /api/agencies/<slug>` - Get detailed information about a specific agency and its child agencies
- `GET /api/statistics/total` - Get aggregate stats
- `GET /api/corrections` - Get historical correction data by year

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/josephycyeh/ecfr-analyzer-backend.git
cd eCFR-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate 
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL (SKIP IF YOU ALREADY HAVE IT INSTALLED)
```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql
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

This will create the database, run a script to compute the stats, and import the data.

```bash
python init_db.py
```

8. Run the development server:
```bash
python app.py
```

The API will be available at `http://localhost:5001`


## Data Processing

The eCFR stats is precomputed by:

1. Fetching agency information from the eCFR API
2. Parsing the references for each agency
4. Getting the latest date for each title
5. Downloading and parsing XML content for each title
6. Computing word counts and section numbers

Verifying the data:

1. Check if the data is correctly parsed
2. Wrote another script by using the /api/versioner/v1/structure/{date}/title-{title}.json endpoint
3. Manually checked the data for a few agencies

Callouts
 - Depending how you're parsing the XML data, you might get slightly different word counts and section counts. 
 
 For example, on DOGE, Appalachian Regional Commission has 77 words while I counted 85.
 Another example is the General Services Administration. DOGE counted 536 sections while I counted 1.15k (verified through the structures API).

## Areas of improvement

- Cron job to update the stats daily
- Streaming XML data from the eCFR API so it can be more memory efficient
- More robust database schema to store the data so we can track historical changes

