import os
import sys
from rag_qa import retrieve_graph_rag_context

sys.stdout.reconfigure(encoding='utf-8')

def main():
    question = "Nghị định 46/2023/NĐ-CP thay thế cho nghị định nào, và nghị định bị thay thế đó có nội dung gì nổi bật về kinh doanh bảo hiểm?"
    
    print("="*80)
    print(f"BÀI THỬ NGHIỆM TRUY VẤN ĐỒ THỊ ĐA BƯỚC (STEP 2)")
    print(f"Câu hỏi: \"{question}\"")
    print("="*80)
    
    for h in [0, 1, 2]:
        print(f"\n" + "#"*50)
        print(f"TRUY VẤN VỚI H= {h} HOPS (BƯỚC NHẢY)")
        print("#"*50)
        
        context = retrieve_graph_rag_context(question, k=2, hops=h, m=3)
        print(context[:1500])
        if len(context) > 1500:
            print("\n... [Văn bản được rút gọn vì hiển thị dài] ...")
            
if __name__ == "__main__":
    main()
