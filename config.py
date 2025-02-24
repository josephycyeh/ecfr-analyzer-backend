import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment (Heroku sets DATABASE_URL)
database_url = os.getenv('DATABASE_URL')

if database_url and database_url.startswith('postgres://'):
    # Heroku's DATABASE_URL uses 'postgres://', but psycopg2 expects 'postgresql://'
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Parse database URL if available, otherwise use local config
if database_url:
    url = urlparse(database_url)
    DB_CONFIG = {
        'dbname': url.path[1:],
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port or 5432
    }
else:
    # Local development configuration
    DB_CONFIG = {
        'dbname': os.getenv('DB_NAME', 'ecfr'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432))
    } 