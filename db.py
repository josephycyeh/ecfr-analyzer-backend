import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            **DB_CONFIG,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        print(f"Connection parameters: host={DB_CONFIG['host']}, "
              f"port={DB_CONFIG['port']}, "
              f"database={DB_CONFIG['dbname']}, "
              f"user={DB_CONFIG['user']}")
        raise

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch (bool): Whether to fetch results or just execute (for INSERT/UPDATE/DELETE)
    
    Returns:
        list: Query results if fetch=True, None otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()
            return None
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error executing query: {e}")
        print(f"Query: {query}")
        print(f"Parameters: {params}")
        raise
    finally:
        if conn:
            conn.close()

def execute_transaction(queries):
    """Execute multiple queries in a transaction.
    
    Args:
        queries (list): List of tuples containing (query, params)
    
    Returns:
        list: List of results from each query
    """
    conn = get_db_connection()
    try:
        results = []
        with conn.cursor() as cur:
            for query, params in queries:
                cur.execute(query, params)
                try:
                    results.append(cur.fetchall())
                except psycopg2.ProgrammingError:
                   
                    results.append(None)
        conn.commit()
        return results
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Transaction error: {e}")
        raise
    finally:
        conn.close()

def init_db():
    """Initialize the database schema."""
    try:
        with open('schema.sql', 'r') as f:
            schema = f.read()
        execute_query(schema, fetch=False)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise 