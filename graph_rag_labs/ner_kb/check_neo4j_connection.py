import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 60)
    print("BƯỚC 7: KIỂM TRA KẾT NỐI NEO4J")
    print("=" * 60)
    
    env_path = os.path.join("ner_kb", ".env")
    if not os.path.exists(env_path):
        print(f"Lỗi: Không tìm thấy file cấu hình {env_path}")
        sys.exit(1)
        
    load_dotenv(env_path)
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    if not uri or not user or not password:
        print("Lỗi: Thông tin kết nối Neo4j trong file .env chưa đầy đủ.")
        sys.exit(1)
        
    print(f"Đang kết nối tới Neo4j tại địa chỉ: {uri} (User: {user}) ...")
    
    driver = None
    try:
        # Create driver
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # 5. Verify connectivity
        driver.verify_connectivity()
        print("Trạng thái kết nối: THÀNH CÔNG (Verified connectivity)")
        
        # 6. Run simple read query
        # We will query database information or run a simple query
        with driver.session(database=database) as session:
            result = session.run("RETURN 1 AS val").single()
            if result and result["val"] == 1:
                print(f"Kiểm thử truy vấn đọc trên DB '{database}': THÀNH CÔNG (Trả về: {result['val']})")
            else:
                print(f"Cảnh báo: Truy vấn đọc thành công nhưng trả về giá trị bất thường.")
                
            # Count current nodes count in this database
            count_result = session.run("MATCH (n) RETURN count(n) AS count").single()
            print(f"Số lượng nút hiện có trên database '{database}': {count_result['count']}")
            
        print("\n[PASS] Neo4j Connection")
        print(f"Database đang sử dụng: {database}")
        
    except Exception as e:
        print("\n[FAIL] Neo4j Connection")
        print(f"Lỗi chi tiết: {e}")
        sys.exit(1)
    finally:
        # 7. Close driver properly
        if driver:
            driver.close()
            print("Đã đóng kết nối driver an toàn.")

if __name__ == "__main__":
    main()
