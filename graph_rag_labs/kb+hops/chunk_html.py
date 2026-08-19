import os
import re
import json
import pandas as pd
import bs4
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

# Paths
WORKSPACE_DIR = r"c:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\kb+hops"
CONTENT_CSV = os.path.join(WORKSPACE_DIR, "content.csv")
METADATA_CSV = os.path.join(WORKSPACE_DIR, "metadata.csv")
OUTPUT_JSON = os.path.join(WORKSPACE_DIR, "chunks.json")

def clean_text(text):
    """
    Cleans whitespaces and normalizes spacing in a text segment.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def table_to_markdown(table_tag):
    """
    Converts HTML table element into standard Markdown table format.
    """
    rows = []
    tr_tags = table_tag.find_all('tr')
    for tr in tr_tags:
        cols = tr.find_all(['td', 'th'])
        col_texts = [clean_text(col.get_text()) for col in cols]
        rows.append(col_texts)
    
    if not rows:
        return ""
    
    # Standardize column count
    num_cols = max(len(r) for r in rows) if rows else 0
    if num_cols == 0:
        return ""
        
    standardized_rows = []
    for r in rows:
        if len(r) < num_cols:
            r += [""] * (num_cols - len(r))
        standardized_rows.append(r)
        
    md_lines = []
    # Header row
    header = standardized_rows[0]
    md_lines.append("| " + " | ".join(header) + " |")
    # Separator row
    md_lines.append("| " + " | ".join(["---"] * num_cols) + " |")
    # Data rows
    for r in standardized_rows[1:]:
        md_lines.append("| " + " | ".join(r) + " |")
        
    return "\n".join(md_lines)

def classify_element(tag):
    """
    Classifies HTML element to its hierarchical level and type.
    Levels:
      1: Chapter (Chương)
      2: Section (Mục)
      3: Subsection (Tiểu mục)
      4: Article (Điều)
      5: Clause (Khoản)
      6: Item (Điểm)
      7: Content/Table (Nội dung chi tiết/Bảng)
    """
    if tag.name == 'table':
        return 7, 'Table'
    
    classes = tag.get('class', [])
    if 'prov-chapter' in classes:
        return 1, 'Chapter'
    elif 'prov-section' in classes:
        return 2, 'Section'
    elif 'prov-subsection' in classes:
        return 3, 'Subsection'
    elif 'prov-article' in classes:
        return 4, 'Article'
    elif 'prov-clause' in classes:
        return 5, 'Clause'
    elif 'prov-item' in classes:
        return 6, 'Item'
    elif 'prov-content' in classes:
        return 7, 'Content'
    
    # Fallbacks based on content regex if classes are missing or generic
    text = tag.get_text(strip=True)
    if re.match(r'^Chương\s+[IVXLCDM0-9\-\s\.]+\b', text, re.IGNORECASE):
        return 1, 'Chapter'
    elif re.match(r'^Mục\s+[0-9IVXLCDM\-\s\.]+\b', text, re.IGNORECASE):
        return 2, 'Section'
    elif re.match(r'^Tiểu\s+mục\s+[0-9IVXLCDM\-\s\.]+\b', text, re.IGNORECASE):
        return 3, 'Subsection'
    elif re.match(r'^Điều\s+[0-9]+[a-z]*[\.\s\-\:]', text, re.IGNORECASE):
        return 4, 'Article'
        
    return 7, 'Content'

class ChunkNode:
    def __init__(self, node_id, level, node_type, title, content, doc_id):
        self.node_id = node_id
        self.level = level
        self.node_type = node_type
        self.title = title
        self.content = content
        self.doc_id = doc_id
        self.parent = None
        self.children = []
        self.next_sibling = None

def build_document_tree(doc_id, html_content):
    """
    Parses HTML content, filters tags, classifies types, and builds a hierarchical tree of Chunks.
    """
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    
    # Collect paragraph, table, and direct text-containing div tags
    candidates = []
    for tag in soup.find_all(True):
        if tag.name == 'p':
            candidates.append(tag)
        elif tag.name == 'table':
            candidates.append(tag)
        elif tag.name == 'div':
            # Include divs that contain direct text and no paragraph or table elements inside
            direct_text = "".join(tag.find_all(string=True, recursive=False)).strip()
            if direct_text and not tag.find(['p', 'table']):
                candidates.append(tag)
                
    root = ChunkNode(node_id=str(doc_id), level=0, node_type='Document', title="", content="", doc_id=str(doc_id))
    
    stack = [root]
    all_nodes = []
    chunk_index = 0
    
    for tag in candidates:
        text = clean_text(tag.get_text())
        if not text and tag.name != 'table':
            continue
            
        level, node_type = classify_element(tag)
        
        if tag.name == 'table':
            content = table_to_markdown(tag)
        else:
            content = text
            
        title = ""
        if node_type in ['Chapter', 'Section', 'Subsection', 'Article']:
            title = content
            
        node_id = f"{doc_id}_chunk_{chunk_index}"
        chunk_index += 1
        
        node = ChunkNode(node_id=node_id, level=level, node_type=node_type, title=title, content=content, doc_id=str(doc_id))
        all_nodes.append(node)
        
        # Pop elements from stack to find the parent
        while stack and stack[-1].level >= level:
            stack.pop()
            
        if stack:
            parent = stack[-1]
            node.parent = parent
            parent.children.append(node)
        else:
            node.parent = root
            root.children.append(node)
            
        stack.append(node)
        
    # Connect sibling NEXT relationships
    def link_siblings(parent_node):
        if len(parent_node.children) > 1:
            for i in range(len(parent_node.children) - 1):
                parent_node.children[i].next_sibling = parent_node.children[i+1]
        for child in parent_node.children:
            link_siblings(child)
            
    link_siblings(root)
    
    return root, all_nodes

def serialize_tree_to_dict(all_nodes):
    """
    Serializes a list of ChunkNodes to a list of dicts.
    """
    chunks_dict_list = []
    for node in all_nodes:
        chunks_dict_list.append({
            "id": node.node_id,
            "doc_id": node.doc_id,
            "type": node.node_type,
            "title": node.title,
            "content": node.content,
            "parent_id": node.parent.node_id if node.parent else None,
            "next_id": node.next_sibling.node_id if node.next_sibling else None
        })
    return chunks_dict_list

def print_visual_tree(node, indent=0, max_lines_per_node=80):
    """
    Recursively prints a visual representation of the tree hierarchy.
    """
    indent_str = "│   " * indent
    if indent > 0:
        indent_str = indent_str[:-4] + "├── "
        
    title_part = f" [{node.title}]" if node.title else ""
    content_preview = node.content[:max_lines_per_node] + "..." if len(node.content) > max_lines_per_node else node.content
    content_preview = content_preview.replace("\n", " [NL] ") # representation for tables
    
    print(f"{indent_str}[{node.node_type}] ID: {node.node_id}{title_part} -> {content_preview}")
    for child in node.children:
        print_visual_tree(child, indent + 1, max_lines_per_node)

def main():
    print("Đang nạp dữ liệu content.csv...")
    if not os.path.exists(CONTENT_CSV):
        print(f"Lỗi: Không tìm thấy tệp {CONTENT_CSV}")
        return
        
    df = pd.read_csv(CONTENT_CSV)
    print(f"Tổng số tài liệu cần phân tách: {len(df)}")
    
    all_serialized_chunks = []
    sample_root = None
    sample_nodes = None
    sample_doc_id = "185630"
    
    for idx, row in df.iterrows():
        doc_id = str(row['id'])
        html_content = str(row['content_html'])
        
        root, all_nodes = build_document_tree(doc_id, html_content)
        
        if doc_id == sample_doc_id:
            sample_root = root
            sample_nodes = all_nodes
            
        all_serialized_chunks.extend(serialize_tree_to_dict(all_nodes))
        
    # Write chunks to file
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_serialized_chunks, f, ensure_ascii=False, indent=2)
        
    print(f"Đã lưu thành công {len(all_serialized_chunks)} phân đoạn vào tệp: {OUTPUT_JSON}")
    
    # Print sample visualization
    if sample_root:
        print("\n" + "="*80)
        print(f"MINH HỌA KẾT QUẢ PHÂN TÁCH MẪU CHO TÀI LIỆU (ID: {sample_doc_id})")
        print("="*80)
        print(f"Tổng số phân đoạn (chunks) được tạo: {len(sample_nodes)}")
        print("\nCẤU TRÚC HÂN CẤP CỦA TÀI LIỆU:")
        print_visual_tree(sample_root, max_lines_per_node=60)
        
        print("\n" + "-"*80)
        print("MINH HỌA MỐI QUAN HỆ NEXT GIỮA CÁC ANH EM LIỀN KỀ:")
        print("-"*80)
        
        # Collect and print some sibling relations
        relations_printed = 0
        def show_next_relations(node):
            nonlocal relations_printed
            if relations_printed >= 10:
                return
            if len(node.children) > 1:
                for i in range(len(node.children) - 1):
                    if relations_printed >= 10:
                        break
                    c1 = node.children[i]
                    c2 = node.children[i+1]
                    print(f"[{c1.node_type}] {c1.node_id} --[:NEXT]--> [{c2.node_type}] {c2.node_id}")
                    relations_printed += 1
            for child in node.children:
                show_next_relations(child)
                
        show_next_relations(sample_root)
        
        # Show table cleaning example if any table in the sample document
        tables = [n for n in sample_nodes if n.node_type == 'Table']
        if tables:
            print("\n" + "-"*80)
            print("MINH HỌA LÀM SẠCH BẢNG BIỂU (Chuyển đổi thành Markdown Table):")
            print("-"*80)
            print(f"ID Bảng: {tables[0].node_id}")
            print(tables[0].content)
            
if __name__ == "__main__":
    main()
