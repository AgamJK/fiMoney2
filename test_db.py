import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from app.db.base_class import Base
from app.db.session import engine

def test_database_connection():
    """Test database connection and table creation."""
    try:
        # Test connection
        print("Testing database connection...")
        conn = engine.connect()
        print("✅ Successfully connected to the database")
        
        # Create all tables
        print("\nCreating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # List all tables
        print("\nTables in the database:")
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f"- {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_database_connection()
