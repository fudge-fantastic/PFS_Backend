import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException
from PIL import Image
from app.config import settings

class FileUploadService:
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.products_dir = os.path.join(self.upload_dir, "products")
        self.max_file_size = settings.max_file_size
        self.allowed_extensions = settings.allowed_image_extensions.split(",")
        
        # Create directories if they don't exist
        os.makedirs(self.products_dir, exist_ok=True)

    def _validate_image(self, file: UploadFile) -> None:
        """Validate uploaded image file."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '{file_extension}' not allowed. Allowed: {', '.join(self.allowed_extensions)}"
            )
        
        # Check file size
        if file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size {file.size} exceeds maximum allowed size of {self.max_file_size} bytes"
            )

    async def upload_product_images(self, files: List[UploadFile]) -> List[str]:
        """Upload multiple product images and return their paths."""
        if len(files) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 images allowed per product")
        
        uploaded_paths = []
        
        for file in files:
            self._validate_image(file)
            
            # Generate unique filename
            file_extension = file.filename.split(".")[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(self.products_dir, unique_filename)
            
            try:
                # Save file without aiofiles for now
                content = await file.read()
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # Validate image integrity using PIL
                with Image.open(file_path) as img:
                    img.verify()
                
                # Return relative path for database storage
                relative_path = f"uploads/products/{unique_filename}"
                uploaded_paths.append(relative_path)
                
            except Exception as e:
                # Clean up file if it was created
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
        
        return uploaded_paths

    def delete_product_images(self, image_paths: List[str]) -> None:
        """Delete product images from filesystem."""
        for path in image_paths:
            if path.startswith("uploads/"):
                full_path = os.path.join(os.getcwd(), path)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print(f"Warning: Failed to delete image {full_path}: {str(e)}")

upload_service = FileUploadService()
