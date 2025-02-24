from db import execute_query, execute_transaction

def get_total_statistics():
    try:
        query = """
            SELECT 
                COUNT(DISTINCT a.id) as total_agencies,
                SUM(s.section_count) as total_sections,
                SUM(s.word_count) as total_words
            FROM agencies a
            LEFT JOIN agency_statistics s ON s.agency_id = a.id
            WHERE a.parent_id IS NULL
        """
        return execute_query(query)[0]
    except Exception as e:
        print(f"Error in get_total_statistics: {str(e)}")
        raise

def get_all_agencies():
    try:
        query = """
            SELECT 
                a.id,
                a.name,
                a.slug,
                a.created_at,
                a.updated_at,
                s.word_count,
                s.section_count,
                s.snapshot_date
            FROM agencies a
            LEFT JOIN agency_statistics s ON s.agency_id = a.id
            WHERE a.parent_id IS NULL
            ORDER BY a.name
        """
        return execute_query(query)
    except Exception as e:
        print(f"Error in get_all_agencies: {str(e)}")
        raise

def get_agency_with_children(slug):
    agency_query = """
        SELECT 
            a.id,
            a.name,
            a.slug,
            a.created_at,
            a.updated_at,
            s.word_count,
            s.section_count,
            s.snapshot_date
        FROM agencies a
        LEFT JOIN agency_statistics s ON s.agency_id = a.id
        WHERE a.slug = %s
    """
    agency = execute_query(agency_query, (slug,))
    if not agency:
        return None, []
    children_query = """
        SELECT 
            a.id,
            a.name,
            a.slug,
            a.created_at,
            a.updated_at,
            s.word_count,
            s.section_count,
            s.snapshot_date
        FROM agencies a
        LEFT JOIN agency_statistics s ON s.agency_id = a.id
        WHERE a.parent_id = %s
        ORDER BY a.name
    """
    children = execute_query(children_query, (agency[0]['id'],))
    
    return agency[0], children

def insert_agency_data(agencies_data):
    agency_stats = []  

    def insert_single_agency(name, slug, parent_id=None):
        agency_query = """
            INSERT INTO agencies (name, slug, parent_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        results = execute_transaction([
            (agency_query, (name, slug, parent_id))
        ])
        if not results or not results[0]:
            raise Exception(f"Failed to insert agency: {name}")
        return results[0][0]['id']

    for agency_data in agencies_data:
        parent_id = insert_single_agency(
            agency_data['name'],
            agency_data['slug']
        )
        agency_stats.append((parent_id, agency_data['word_count'], agency_data['sections']))
        
        if 'children' in agency_data and agency_data['children']:
            for child_name, child_data in agency_data['children'].items():
                child_id = insert_single_agency(
                    child_name,
                    child_data['slug'],
                    parent_id
                )
                agency_stats.append((child_id, child_data['words'], child_data['sections']))

    if agency_stats:
        placeholders = ','.join(['(%s, %s, %s)'] * len(agency_stats))
        stats_query = f"""
            INSERT INTO agency_statistics 
            (agency_id, word_count, section_count)
            VALUES {placeholders}
        """
        values = [val for tup in agency_stats for val in tup]
        execute_transaction([(stats_query, values)])
    
    return True 