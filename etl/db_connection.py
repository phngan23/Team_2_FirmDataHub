import os
import getpass
from pathlib import Path
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Get database connection with automatic password prompt if needed
    No .env file required
    """
    try:
        # Try to connect without password first (if MySQL has no password)
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='team2_firmhub',
                user='root',
                password=''
            )
            return connection
        except Error:
            # If fails, ask for password
            password = getpass.getpass("🔐 Enter MySQL password for root: ")
            connection = mysql.connector.connect(
                host='localhost',
                database='team2_firmhub',
                user='root',
                password=password
            )
            return connection
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        print("\n💡 Make sure:")
        print("   1. MySQL is running")
        print("   2. Database 'team2_firmhub' exists")
        print("   3. You have correct credentials")
        return None

def get_project_root():
    """Get project root directory dynamically"""
    return Path(__file__).parent.parent

def get_data_path(filename):
    """Get data file path dynamically - no hardcoding"""
    project_root = get_project_root()
    data_path = project_root / "data" / filename
    
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        print(f"📁 Expected location: {data_path.absolute()}")
        return None
    
    return data_path

def get_output_path(filename):
    """Get output file path dynamically"""
    output_dir = get_project_root() / "outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir / filename