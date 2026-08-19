import sys
from pathlib import Path

def download():
    model_name = "BAAI/bge-reranker-v2-m3"
    print(f"Starting download of model {model_name} from HuggingFace...")
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
    except ImportError:
        print("Error: 'transformers' or 'torch' is not installed.")
        sys.exit(1)

    print("Downloading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("Downloading Model weights (~2.2 GB)...")
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    print("Model downloaded successfully!")

if __name__ == "__main__":
    download()
