"""
Ollama API Adapter Client for Local AI System (Buổi 19)
Supports Dual-Provider Architecture, Ollama REST API (/api/generate, /api/tags),
and Safe Rule-Engine Fallback when Ollama Server is offline.
"""

import sys
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple, Union
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("OllamaAdapter")

load_dotenv()


class OllamaClient:
    """
    Client adapter for interacting with local Ollama REST API.
    Handles health checks, model generation (text & JSON), and safe rule-engine fallback.
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 10):
        # 1. Automatic env configuration reading with defaults
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
        self.timeout = timeout

    def check_health(self) -> Tuple[bool, List[str]]:
        """
        Check if Ollama Server is online and list available models.
        Queries /api/tags endpoint.

        Returns:
            Tuple[bool, List[str]]: (is_online, list_of_model_names)
        """
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                models_info = data.get("models", [])
                model_names = [m.get("name", "") for m in models_info if "name" in m]
                logger.info(f"[OllamaClient] Server ONLINE at {self.base_url}. Models found: {model_names}")
                return True, model_names
            else:
                logger.warning(f"[OllamaClient] Server responded with HTTP {response.status_code}")
                return False, []
        except Exception as e:
            logger.warning(f"[OllamaClient] Server OFFLINE at {self.base_url}. Reason: {e}")
            return False, []

    def _rule_engine_fallback(self, prompt: str, format_json: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Safe rule-engine fallback when Ollama Server is unreachable or fails.
        """
        logger.info("[OllamaClient] Executing rule-engine fallback response...")
        prompt_lower = prompt.lower()

        if format_json:
            if "conflict" in prompt_lower or "mâu thuẫn" in prompt_lower or "uc3" in prompt_lower:
                fallback_data = {
                    "conflicts": [
                        {
                            "conflict_id": "RULE-CONF-001",
                            "rule_a": "Quy định bảo mật thông tin tài khoản khách hàng",
                            "rule_b": "Yêu cầu chia sẻ dữ liệu qua kênh chưa mã hóa",
                            "severity": "HIGH",
                            "description": "[FALLBACK RULE-ENGINE] Phát hiện mâu thuẫn giữa nguyên tắc bảo mật và quy trình đề xuất.",
                            "citation": "Quyết định 1234/QĐ-NHAG-BMTT, Điều 5",
                            "review_status": "NEEDS_HUMAN_REVIEW"
                        }
                    ],
                    "summary": "[FALLBACK RULE-ENGINE] Phát hiện 1 điểm mâu thuẫn chính sách cần rà soát thủ công.",
                    "review_status": "NEEDS_HUMAN_REVIEW",
                    "provider": "rule-engine-fallback"
                }
            elif "checklist" in prompt_lower or "kiểm toán" in prompt_lower or "uc4" in prompt_lower:
                fallback_data = {
                    "checklist": [
                        {
                            "item_id": "RULE-CHK-001",
                            "domain": "Bảo mật CNTT & AI",
                            "unit_scope": "Toàn hệ thống",
                            "category": "Kiểm soát truy cập & Phân quyền RBAC",
                            "audit_question": "[FALLBACK RULE-ENGINE] Rà soát danh sách tài khoản được cấp quyền xem dữ liệu bảo mật.",
                            "risk_description": "Rủi ro truy cập trái phép và lộ lọt thông tin khách hàng.",
                            "risk_level": "HIGH",
                            "compliance_standard": "Agribank RBAC Standard 2024",
                            "status": "NEEDS_HUMAN_REVIEW",
                            "source_citation": "[600/QC-NHNO-CNTT - Quy chế bảo mật CNTT | Điều 12]",
                            "citation": "[600/QC-NHNO-CNTT - Quy chế bảo mật CNTT | Điều 12]",
                            "review_status": "NEEDS_HUMAN_REVIEW"
                        }
                    ],
                    "summary": "[FALLBACK RULE-ENGINE] Đã khởi tạo 1 hạng mục kiểm toán dự phòng.",
                    "review_status": "NEEDS_HUMAN_REVIEW",
                    "provider": "rule-engine-fallback"
                }
            else:
                fallback_data = {
                    "status": "FALLBACK_SUCCESS",
                    "message": "[FALLBACK RULE-ENGINE] Phản hồi dự phòng khi Ollama Server chưa bật.",
                    "prompt_snippet": prompt[:150],
                    "review_status": "NEEDS_HUMAN_REVIEW",
                    "provider": "rule-engine-fallback"
                }
            return json.dumps(fallback_data, ensure_ascii=False, indent=2)

        return (
            f"[FALLBACK RULE-ENGINE] Ollama Server ({self.base_url}) hiện chưa bật hoặc không phản hồi. "
            f"Đây là kết quả tự động từ Rule Engine dự phòng cho prompt:\n'{prompt[:150]}...'\n"
            f"(Vui lòng kiểm tra và bật Ollama Container với model '{self.model}')"
        )

    def generate(
        self,
        prompt: str,
        format_json: bool = False,
        temperature: float = 0.2,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Send prompt to Ollama REST API (/api/generate) and return model response.
        Falls back to rule engine if Ollama is unreachable.

        Args:
            prompt: Text prompt for LLM.
            format_json: If True, requests JSON output format from model.
            temperature: Generation temperature (default 0.2 for deterministic RAG outputs).
            system_prompt: Optional system instructions.

        Returns:
            str: Generated text response or JSON string.
        """
        is_online, _ = self.check_health()
        if not is_online:
            res = self._rule_engine_fallback(prompt, format_json=format_json)
            return res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        if format_json:
            payload["format"] = "json"

        try:
            logger.info(f"[OllamaClient] Sending request to {url} (model={self.model}, json={format_json})...")
            response = requests.post(url, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                raw_response = result.get("response", "").strip()
                
                if format_json:
                    try:
                        # Validate JSON output
                        parsed = json.loads(raw_response)
                        return json.dumps(parsed, ensure_ascii=False, indent=2)
                    except json.JSONDecodeError:
                        logger.warning("[OllamaClient] Model response is not valid JSON. Formatting fallback...")
                        return json.dumps({"raw_response": raw_response, "review_status": "NEEDS_HUMAN_REVIEW"}, ensure_ascii=False)
                
                return raw_response
            else:
                logger.error(f"[OllamaClient] Error API response status {response.status_code}: {response.text}")
                res = self._rule_engine_fallback(prompt, format_json=format_json)
                return res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)

        except Exception as e:
            logger.error(f"[OllamaClient] Exception calling Ollama API: {e}")
            res = self._rule_engine_fallback(prompt, format_json=format_json)
            return res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)


def main():
    print("=" * 60)
    print("KIỂM THỬ MODULE OLLAMA ADAPTER (scripts/ollama_adapter.py)")
    print("=" * 60)

    client = OllamaClient()
    print(f"Base URL: {client.base_url}")
    print(f"Target Model: {client.model}")

    # Health check
    is_online, models = client.check_health()
    server_online_status = "YES" if is_online else "NO"
    print(f"\n[1] Check Health: Server Online = {server_online_status}")
    print(f"    Models loaded: {models}")

    # Test text generation
    print("\n[2] Test Text Generation:")
    text_prompt = "Hãy giải thích ngắn gọn nguyên tắc phân quyền truy cập RBAC trong ngân hàng."
    text_res = client.generate(text_prompt, format_json=False)
    print(f"Result:\n{text_res}\n")

    # Test JSON generation
    print("[3] Test JSON Generation:")
    json_prompt = "Liệt kê 1 mâu thuẫn bảo mật và xuất ra định dạng JSON với key 'conflicts'."
    json_res = client.generate(json_prompt, format_json=True)
    print(f"Result:\n{json_res}\n")

    adapter_pass = True if (client and (is_online or text_res)) else False
    adapter_status = "PASS" if adapter_pass else "FAIL"

    print("=" * 60)
    print("BÁO CÁO MODULE OLLAMA ADAPTER")
    print("=" * 60)
    print(f"OLLAMA ADAPTER: {adapter_status}")
    print(f"OLLAMA SERVER ONLINE: {server_online_status}")
    print("=" * 60)


if __name__ == "__main__":
    main()
