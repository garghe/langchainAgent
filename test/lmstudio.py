import requests

def test_lmstudio_connection(base_url="http://127.0.0.1:9999/v1"):
    try:
        response = requests.get(f"{base_url}/models")  # Or any simple endpoint
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to LMStudio: {e}")

if __name__ == "__main__":
    test_lmstudio_connection()