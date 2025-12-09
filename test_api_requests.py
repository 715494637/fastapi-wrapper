#!/usr/bin/env python3
"""
Quick test script for the Gemini API wrapper (using requests library).
"""

import json
import time
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint using requests."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Timeout:
        print("❌ Health check timed out")
    except ConnectionError:
        print("❌ Cannot connect to server")
    except RequestException as e:
        print(f"❌ Health check failed: {e}")


def test_models():
    """Test models endpoint using requests."""
    print("\n📋 Testing models endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/v1/models", timeout=10)
        if response.status_code == 200:
            print("✅ Models endpoint passed")
            models = response.json()
            print(f"   Available models: {[m['id'] for m in models['data']]}")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
    except Timeout:
        print("❌ Models endpoint timed out")
    except ConnectionError:
        print("❌ Cannot connect to server")
    except RequestException as e:
        print(f"❌ Models endpoint failed: {e}")


def test_chat_completion():
    """Test chat completion endpoint using requests."""
    print("\n💬 Testing chat completion...")

    payload = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": "Hello! Please respond with just 'Hello back!'"}
        ],
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ Chat completion passed")
            result = response.json()
            print(f"   Response: {result['choices'][0]['message']['content']}")
            print(f"   Model: {result['model']}")
            print(f"   Usage: {result.get('usage', 'N/A')}")
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Timeout:
        print("❌ Chat completion timed out")
    except ConnectionError:
        print("❌ Cannot connect to server")
    except requests.exceptions.JSONDecodeError:
        print("❌ Failed to parse JSON response")
    except RequestException as e:
        print(f"❌ Chat completion failed: {e}")


def test_with_system_prompt():
    """Test chat completion with system prompt."""
    print("\n🤖 Testing with system prompt...")

    payload = {
        "model": "gemini-2.5-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Always be very brief."},
            {"role": "user", "content": "What is Python?"}
        ],
    }

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ System prompt test passed")
            result = response.json()
            print(f"   Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"❌ System prompt test failed: {response.status_code}")
    except Timeout:
        print("❌ System prompt test timed out")
    except ConnectionError:
        print("❌ Cannot connect to server")
    except RequestException as e:
        print(f"❌ System prompt test failed: {e}")


def test_streaming():
    """Test streaming chat completion."""
    print("\n🌊 Testing streaming chat completion...")

    payload = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5 slowly"}
        ],
        "stream": True,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ Streaming test started")
            content = ""
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    chunk = line[6:]
                    if chunk != '[DONE]':
                        try:
                            data = json.loads(chunk)
                            if 'choices' in data and data['choices']:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content += delta['content']
                        except json.JSONDecodeError:
                            pass
            print(f"   Received streaming content length: {len(content)} characters")
        else:
            print(f"❌ Streaming test failed: {response.status_code}")
    except Timeout:
        print("❌ Streaming test timed out")
    except ConnectionError:
        print("❌ Cannot connect to server")
    except RequestException as e:
        print(f"❌ Streaming test failed: {e}")


def test_multiple_turns():
    """Test multiple turns conversation."""
    print("\n🔄 Testing multiple turns conversation...")

    # First message
    payload1 = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": "Remember the number 42"}
        ],
    }

    # Second message
    payload2 = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": "What number did I ask you to remember?"},
            {"role": "assistant", "content": "I'll remember that number for you."},
            {"role": "user", "content": "What was it?"}
        ],
    }

    try:
        response1 = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload1,
            timeout=30
        )

        if response1.status_code == 200:
            result1 = response1.json()
            assistant_msg = result1['choices'][0]['message']['content']

            # Update second payload with actual response
            payload2['messages'][1]['content'] = assistant_msg

            response2 = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                json=payload2,
                timeout=30
            )

            if response2.status_code == 200:
                result2 = response2.json()
                print("✅ Multiple turns test passed")
                print(f"   First response: {assistant_msg[:50]}...")
                print(f"   Second response: {result2['choices'][0]['message']['content'][:50]}...")
            else:
                print(f"❌ Multiple turns second request failed: {response2.status_code}")
        else:
            print(f"❌ Multiple turns first request failed: {response1.status_code}")
    except RequestException as e:
        print(f"❌ Multiple turns test failed: {e}")


def test_error_handling():
    """Test error handling with invalid requests."""
    print("\n⚠️ Testing error handling...")

    # Test with invalid model
    invalid_payload = {
        "model": "invalid-model-name",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
    }

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=invalid_payload,
            timeout=10
        )
        if response.status_code != 200:
            print("✅ Error handling works correctly")
            print(f"   Expected error: {response.status_code}")
        else:
            print("⚠️ Invalid model was accepted (unexpected)")
    except RequestException as e:
        print(f"❌ Error handling test failed: {e}")


def performance_test():
    """Simple performance test."""
    print("\n⚡ Running performance test...")

    payload = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": "Say 'Performance test complete'"}
        ],
    }

    times = []
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            end_time = time.time()

            if response.status_code == 200:
                times.append(end_time - start_time)
                print(f"   Request {i+1}: {(end_time - start_time):.2f}s")
            else:
                print(f"   Request {i+1} failed: {response.status_code}")
        except RequestException as e:
            print(f"   Request {i+1} failed: {e}")

    if times:
        avg_time = sum(times) / len(times)
        print(f"   Average response time: {avg_time:.2f}s")


def main():
    """Run all tests."""
    print("🧪 Starting API tests (using requests)...\n")

    try:
        test_health()
        test_models()
        test_chat_completion()
        test_with_system_prompt()
        test_streaming()
        test_multiple_turns()
        test_error_handling()
        performance_test()

        print("\n✨ All tests completed!")

    except ConnectionRefusedError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()