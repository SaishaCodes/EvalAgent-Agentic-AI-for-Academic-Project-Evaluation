# backend/app/llm_provider.py
import os
from typing import List, Dict, Any
import json
import yaml

# ---------- 1️⃣  Local Llama‑cpp (CPU) ----------
from llama_cpp import Llama

class LlamaCPPProvider:
    """
    Wrapper around llama-cpp-python (llama.cpp compiled model).
    Expects a GGML .bin model in ./models/
    """
    def __init__(self, model_path: str = "./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        self.llama = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=os.cpu_count(),
            n_gpu_layers=0,                 # set >0 if you have a GPU + cuBLAS support
        )

    def _format_prompt(self, system: str, user: str) -> str:
        # Llama‑2 chat format
        return f"<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{user} [/INST]"

    def chat(self, system: str, user: str, temperature: float = 0.2,
             max_tokens: int = 1024) -> str:
        prompt = self._format_prompt(system, user)
        out = self.llama(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "[/INST]"],
        )
        return out["choices"][0]["text"].strip()

# ---------- 2️⃣  HuggingFace Inference API (free tier) ----------
import httpx
from huggingface_hub import InferenceClient

class HFInferenceProvider:
    """
    Calls the public inference endpoint.
    You need a (free) HF token – you can create one at huggingface.co/settings/tokens.
    """
    def __init__(self, repo_id: str = "mistral-7b-instruct-v0.2.Q4_K_M"):
        token = os.getenv("HF_TOKEN")
        if not token:
            raise EnvironmentError("Set HF_TOKEN env variable")
        self.client = InferenceClient(repo_id=repo_id, token=token)

    def chat(self, system: str, user: str, temperature: float = 0.2,
             max_new_tokens: int = 512) -> str:
        # The HF inference endpoint expects a single string with the chat history.
        # We'll use the same Llama‑2 format as above.
        prompt = f"<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{user} [/INST]"
        response = self.client.text_generation(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=False,
            stop_sequences=["</s>", "[/INST]"],
        )
        # The API returns a generator; we just need the first chunk
        return response[0]["generated_text"].strip()

# ---------- 3️⃣  Unified interface ----------
class LLMProvider:
    """
    Choose the backend at runtime via env variable LLM_BACKEND:
        - "local"   → LlamaCPPProvider (requires model file)
        - "hf"      → HFInferenceProvider (requires HF_TOKEN)
    """
    def __init__(self):
        backend = os.getenv("LLM_BACKEND", "local")
        if backend == "local":
            self.impl = LlamaCPPProvider()
        elif backend == "hf":
            self.impl = HFInferenceProvider()
        else:
            raise ValueError(f"Unsupported LLM_BACKEND={backend}")

    def chat(self, system: str, user: str,
             temperature: float = 0.2,
             max_tokens: int = 1024) -> str:
        return self.impl.chat(system, user, temperature, max_tokens)