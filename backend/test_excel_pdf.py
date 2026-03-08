import io
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app

def test_excel_to_pdf():
    client = TestClient(app)
    
    # Create a dummy Excel file in memory
    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
        df1 = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [25, 30]})
        df1.to_excel(writer, sheet_name="People", index=False)
        
        df2 = pd.DataFrame({"Item": ["Apple", "Banana"], "Price": [1.2, 0.8]})
        df2.to_excel(writer, sheet_name="Products", index=False)
        
        # Empty sheet
        df3 = pd.DataFrame()
        df3.to_excel(writer, sheet_name="Empty", index=False)
        
    excel_io.seek(0)
    
    print("Sending request to /api/tools/excel-to-pdf...")
    response = client.post(
        "/api/tools/excel-to-pdf",
        files={"files": ("test.xlsx", excel_io, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! PDF received.")
        print(f"Headers: {response.headers}")
        print(f"Content Length: {len(response.content)} bytes")
        with open("test_output.pdf", "wb") as f:
            f.write(response.content)
        print("Saved test_output.pdf for manual inspection.")
    else:
        print(f"Error: {response.json()}")

if __name__ == "__main__":
    test_excel_to_pdf()
