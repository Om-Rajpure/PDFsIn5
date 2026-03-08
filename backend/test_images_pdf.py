import io
from fastapi.testclient import TestClient
from PIL import Image

# Import the FastAPI app
try:
    from app.main import app
except ImportError:
    print("Could not import app. Run this from the backend directory.")
    exit(1)

client = TestClient(app)

def create_mock_image(format="JPEG", color="red"):
    """Create a mock image in memory and return its bytes."""
    img = Image.new('RGB', (100, 100), color=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

def test_images_to_pdf():
    print("Sending request to /api/tools/images-to-pdf...")
    
    # Create mock images natively in memory
    img1_bytes = create_mock_image(format="JPEG", color="red")
    img2_bytes = create_mock_image(format="PNG", color="green")
    img3_bytes = create_mock_image(format="BMP", color="blue")
    
    files = [
        ("files", ("image1.jpg", img1_bytes, "image/jpeg")),
        ("files", ("image2.png", img2_bytes, "image/png")),
        ("files", ("image3.bmp", img3_bytes, "image/bmp")),
    ]
    
    response = client.post("/api/tools/images-to-pdf", files=files)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Content Length: {len(response.content)} bytes")
        print(f"Headers: {response.headers}")
        # Save output for manual inspection
        with open("images_test_output.pdf", "wb") as f:
            f.write(response.content)
        print("Saved images_test_output.pdf for manual inspection.")
    else:
        print(f"Error: {response.json()}")

if __name__ == "__main__":
    test_images_to_pdf()
