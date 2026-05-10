
import requests
import json

# HTTPS 测试 - 自签名证书需要禁用验证
url = "https://localhost:5000/v1/chat/completions"
payload = {
    "model": "interview-assistant",
    "messages": [
        {"type": "human", "content": "你好"}
    ],
    "stream": True,
    "session_id": "test_123"
}

print("Testing HTTPS streaming API...")
response = requests.post(url, json=payload, stream=True, verify=False)
print(f"Status code: {response.status_code}")

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data_str = line[6:]
            if data_str == '[DONE]':
                break
            try:
                data = json.loads(data_str)
                if data.get('choices'):
                    delta = data['choices'][0].get('delta', {})
                    if 'content' in delta:
                        print(delta['content'], end='', flush=True)
            except Exception as e:
                print(f"\nError parsing: {e}")
                print(f"Raw line: {line}")
print("\nStream completed!")
