import requests
import time
import sys
import os

BASE_URL = "http://127.0.0.1:8000/api"

def test_tool_flow(tool_name, files, params=None):
    print(f"\n>>> Testing tool: {tool_name}")
    
    # 1. Enqueue Job
    url = f"{BASE_URL}/tools/{tool_name}"
    try:
        resp = requests.post(url, files=files, data=params)
        if resp.status_code != 222 and resp.status_code != 202:
            print(f"FAILED to enqueue: {resp.status_code} {resp.text}")
            return False
            
        job_data = resp.json()
        job_id = job_data.get("job_id")
        print(f"Job enqueued: {job_id}")
    except Exception as e:
        print(f"Connection error enqueuing: {e}")
        return False

    # 2. Poll Status
    status_url = f"{BASE_URL}/jobs/{job_id}"
    start_time = time.time()
    while True:
        try:
            resp = requests.get(status_url)
            if resp.status_code != 200:
                print(f"Status check failed: {resp.status_code} {resp.text}")
                return False
                
            data = resp.json()
            status = data.get("status")
            print(f"Current status: {status}")
            
            if status == "finished":
                print("Job finished successfully!")
                print(f"Metadata: {data.get('metadata')}")
                break
            elif status == "failed":
                print(f"Job FAILED: {data.get('error')}")
                return False
                
            if time.time() - start_time > 60:
                print("Polling timed out after 60s")
                return False
                
            time.sleep(2)
        except Exception as e:
            print(f"Connection error polling: {e}")
            return False

    # 3. Download Result
    download_url = f"{status_url}/download"
    try:
        resp = requests.get(download_url)
        if resp.status_code == 200:
            print(f"Download successful! Size: {len(resp.content)} bytes")
            return True
        else:
            print(f"Download failed: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"Connection error downloading: {e}")
        return False

def main():
    # Create dummy PDF for testing
    dummy_pdf = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<< /Root 1 0 R >>\n%%EOF"
    with open("test1.pdf", "wb") as f: f.write(dummy_pdf)
    with open("test2.pdf", "wb") as f: f.write(dummy_pdf)
    
    success = True
    
    # Test Merge
    with open("test1.pdf", "rb") as f1, open("test2.pdf", "rb") as f2:
        files = [
            ("files", ("test1.pdf", f1, "application/pdf")),
            ("files", ("test2.pdf", f2, "application/pdf"))
        ]
        if not test_tool_flow("merge-pdf", files):
            success = False

    # Test Protect (with params)
    with open("test1.pdf", "rb") as f1:
        files = [("files", ("test1.pdf", f1, "application/pdf"))]
        params = {"password": "testpassword"}
        if not test_tool_flow("protect-pdf", files, params):
            success = False

    # Cleanup test files
    os.remove("test1.pdf")
    os.remove("test2.pdf")
    
    if success:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
