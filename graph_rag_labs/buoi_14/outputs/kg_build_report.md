# BÁO CÁO XÂY DỰNG KNOWLEDGE GRAPH MINI (NEO4J)

## TRẠNG THÁI: `NEO4J_NOT_CONNECTED`

> [!WARNING]
> Không thể kết nối tới cơ sở dữ liệu Neo4j tại thời điểm chạy.
> **Chi tiết lỗi**: `Không thể ping tới Neo4j server.`

### Hướng dẫn khởi động Neo4j:
1. **Sử dụng Neo4j Desktop**: Khởi động DBMS của bạn và đảm bảo bolt port là `7687`.
2. **Sử dụng Docker**:
   ```bash
   docker run -d --name neo4j-buoi14 -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.26
   ```
3. Cập nhật thông tin đăng nhập trong file `buoi_14/.env` và chạy lại:
   ```bash
   python scripts/load_mini_kg.py
   ```
