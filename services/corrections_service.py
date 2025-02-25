from db import execute_query, execute_transaction

def get_all_corrections():
    """Get all corrections data ordered by year."""
    query = """
        SELECT year, count
        FROM corrections
        ORDER BY year
    """
    return execute_query(query)

def insert_corrections_data(corrections_data):
    """Insert corrections data into database."""
    queries = [
        (
            """
            INSERT INTO corrections (year, count)
            VALUES (%s, %s)
            ON CONFLICT (year) DO UPDATE
            SET count = EXCLUDED.count,
                updated_at = CURRENT_TIMESTAMP
            """,
            (int(year), count)
        )
        for year, count in corrections_data.items()
    ]
    
    execute_transaction(queries)
    return True 