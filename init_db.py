from db import init_db
from services.import_service import import_agency_data, import_corrections_data

def main():
    print("Initializing database...")
    init_db()
    
    print("\nImporting agency data...")
    import_agency_data()
    
    print("\nImporting corrections data...")
    import_corrections_data()
    
    print("\nDatabase setup and data import complete!")

if __name__ == "__main__":
    main() 