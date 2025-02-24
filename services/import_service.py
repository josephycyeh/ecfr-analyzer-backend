import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import process_agency_data, process_corrections_data
from services.agency_service import insert_agency_data
from services.corrections_service import insert_corrections_data

def import_agency_data():
    """Process and import agency data into database."""
    try:
        print("Processing agency information...")
        agencies_data = process_agency_data()
        
        transformed_data = [
            {
                "name": agency_name,
                "word_count": data["total_words"],
                "sections": data["total_sections"],
                "slug": data["slug"],
                "children": data.get("children", {})
            }
            for agency_name, data in agencies_data.items()
        ]
        
        print(f"Importing {len(transformed_data)} agencies and their children into database...")
        insert_agency_data(transformed_data)
        print("Agency data import completed successfully!")
        return True
    except Exception as e:
        print(f"Error importing agency data: {e}")
        raise

def import_corrections_data():
    """Process and import corrections data into database."""
    try:
        print("Processing corrections data...")
        corrections_data = process_corrections_data()
        
        print(f"Importing corrections data for {len(corrections_data)} years...")
        insert_corrections_data(corrections_data)
        print("Corrections data import completed successfully!")
        return True
    except Exception as e:
        print(f"Error importing corrections data: {e}")
        raise 