import urllib.request
import json
import time
import sys

# Define base URL - adjust port if needed
BASE_URL = "http://127.0.0.1:8000/api/v1/query/"

def test_query(query, session_id=None):
    print(f"\n{'='*60}")
    print(f"Testing Query: '{query}'")
    
    data = {"query": query}
    if session_id:
        data["session_id"] = session_id
        
    json_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(BASE_URL, data=json_data, headers={'Content-Type': 'application/json'})
    
    try:
        print("Sending request...", end="", flush=True)
        start_time = time.time()
        with urllib.request.urlopen(req) as response:
            duration = time.time() - start_time
            response_body = response.read().decode('utf-8')
            
            print(f" Done ({duration:.2f}s)")
            print(f"Status Code: {response.getcode()}")
            
            try:
                parsed = json.loads(response_body)
                print("✅ JSON Response Received")
                print(f"Session ID: {parsed.get('session_id')}")
                
                content = parsed.get('data', {})
                
                response_text = content.get('response')
                reasoning = content.get('reasoning')
                status = content.get('status')
                conversation_type = content.get('conversation_type')
                
                print(f"\n[RESPONSE FIELD]: {response_text}")
                print(f"[REASONING]: {reasoning[:100]}..." if reasoning else "[REASONING]: None")
                print(f"[STATUS]: {status}")
                print(f"[TYPE]: {conversation_type}")
                
                if not response_text and reasoning:
                    print("\n⚠️  WARNING: 'response' field is empty, but 'reasoning' is present.")
                    print("   The fallback logic in the endpoint should have handled this by now.")
                    
                return parsed.get('session_id')
                
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON response")
                print(f"Raw Body: {response_body}")
                return session_id
                
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error: {e.code}")
        print(f"Reason: {e.reason}")
        try:
            err_body = e.read().decode('utf-8')
            print(f"Error Body: {err_body}")
        except:
            pass
        return session_id
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return session_id

if __name__ == "__main__":
    print("Starting Live API Tests...")
    print(f"Target URL: {BASE_URL}")
    
    # 1. Test the specific failure case that was reported
    sid = test_query("what is compliance audit report?")
    
    # 2. Test a follow up if the first one succeeded
    if sid:
        time.sleep(1)
        test_query("tell me more about the requirements", sid)
    else:
        print("\nSkipping follow-up test due to initial failure.")
