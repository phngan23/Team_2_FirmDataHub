import os
import sys
import subprocess
import getpass
from pathlib import Path

def get_project_root():
    return Path(__file__).parent.parent

def find_mysql():
    import shutil
    mysql_path = shutil.which('mysql')
    if mysql_path:
        return mysql_path
    
    common_paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
        r"C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe",
    ]
    
    for path in common_paths:
        if Path(path).exists():
            return path
    
    try:
        result = subprocess.run(['where', 'mysql'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    raise FileNotFoundError("MySQL not found")

def init_database():
    project_root = get_project_root()
    sql_file = project_root / "sql" / "schema_and_seed.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        print(f"📁 Expected location: {sql_file.absolute()}")
        return False
    
    try:
        mysql_exe = find_mysql()
        print(f"✅ Found MySQL at: {mysql_exe}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    
    mysql_user = 'root'
    mysql_password = getpass.getpass("🔐 Enter MySQL password (press Enter if none): ")
    
    # Cách 1: Dùng input redirection với shell
    print(f"\n📁 Executing SQL file: {sql_file}")
    print("⏳ Creating database and tables...")
    
    try:
        # Đọc nội dung SQL file
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Tạo command
        if mysql_password:
            cmd = [mysql_exe, f'-u{mysql_user}', f'-p{mysql_password}']
        else:
            cmd = [mysql_exe, f'-u{mysql_user}']
        
        # Chạy với input từ SQL content
        result = subprocess.run(
            cmd,
            input=sql_content,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=project_root
        )
        
        # Kiểm tra kết quả
        if result.returncode == 0:
            print("✅ Database initialized successfully!")
            return True
        else:
            # Bỏ qua warning, chỉ in lỗi thực sự
            if result.stderr and "Using a password" not in result.stderr:
                print(f"❌ Error: {result.stderr}")
            elif result.stdout:
                print("✅ Database initialized (warnings ignored)")
                return True
            else:
                print("❌ Failed to initialize database")
                if result.stderr:
                    print(f"Details: {result.stderr}")
                return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout: MySQL command took too long")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)