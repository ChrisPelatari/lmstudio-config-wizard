import json
import urllib.request
import urllib.error

LMS_BASE = "http://localhost:1234/v1"


def test_config(model_name: str, config: dict, prompt: str) -> str:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": config.get("temperature", 0.7),
        "top_p": config.get("top_p", 0.9),
        "top_k": config.get("top_k", 40),
        "repeat_penalty": config.get("repeat_penalty", 1.1),
        "max_tokens": config.get("max_tokens", 1024),
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{LMS_BASE}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.load(resp)
            return body["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        return f"[Could not reach LM Studio: {e.reason}]"
    except (KeyError, json.JSONDecodeError) as e:
        return f"[Unexpected response: {e}]"
