import asyncio
import io
from PIL import Image

# Import the router and endpoint
from disease.router import predict_disease

# Mock FastAPI UploadFile
class MockUploadFile:
    def __init__(self, content: bytes, content_type: str):
        self._content = content
        self.content_type = content_type

    async def read(self):
        return self._content

async def main():
    # Create a dummy image
    img = Image.new("RGB", (256, 256), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    file = MockUploadFile(content=image_bytes, content_type="image/jpeg")

    print("Testing /api/disease/predict...")
    response = await predict_disease(file)

    print("--- Response Details ---")
    print(f"Disease: {response.disease}")
    print(f"Treatment: {response.treatment}")
    
    if response.heatmap_image:
        print(f"Heatmap Base64 starts with: {response.heatmap_image[:50]}...")
        print("✓ Heatmap effectively generated!")
    else:
        print("✗ Heatmap is None.")

if __name__ == "__main__":
    asyncio.run(main())
