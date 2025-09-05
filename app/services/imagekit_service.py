import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from app.config import settings

class ImageKitService:
    def __init__(self):
        if not all([settings.imagekit_private_key, settings.imagekit_public_key, settings.imagekit_url_endpoint]):
            raise ValueError("ImageKit configuration is incomplete. Please check environment variables.")
        
        self.imagekit = ImageKit(
            private_key=settings.imagekit_private_key,
            public_key=settings.imagekit_public_key,
            url_endpoint=settings.imagekit_url_endpoint
        )
        self.max_file_size = settings.max_file_size
        self.allowed_extensions = settings.allowed_image_extensions.split(",")

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
        """Upload multiple product images to ImageKit and return their URLs."""
        if len(files) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 images allowed per product")
        
        uploaded_urls = []
        
        for file in files:
            self._validate_image(file)
            
            # Generate unique filename
            file_extension = file.filename.split(".")[-1].lower()
            unique_filename = f"product_{uuid.uuid4()}.{file_extension}"
            
            try:
                # Read file content
                file_content = await file.read()
                
                # Convert to base64 for ImageKit SDK compatibility
                import base64
                file_content_b64 = base64.b64encode(file_content).decode('utf-8')
                
                # Upload to ImageKit using base64 encoded content
                result = self.imagekit.upload_file(
                    file=file_content_b64,
                    file_name=unique_filename,
                    options=UploadFileRequestOptions(
                        folder="/products/",
                        use_unique_file_name=True,
                        tags=["product", "image"]
                    )
                )
                
                # Check if upload was successful
                if isinstance(result, dict):
                    if result.get('error'):
                        raise HTTPException(
                            status_code=400,
                            detail=f"ImageKit upload failed: {result['error']}"
                        )
                    
                    # Store the URL for database
                    if result.get('url'):
                        uploaded_urls.append(result['url'])
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="ImageKit upload succeeded but no URL returned"
                        )
                else:
                    # Handle object response
                    if hasattr(result, 'error') and result.error:
                        raise HTTPException(
                            status_code=400,
                            detail=f"ImageKit upload failed: {result.error}"
                        )
                    
                    # Store the URL for database
                    if hasattr(result, 'url') and result.url:
                        uploaded_urls.append(result.url)
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="ImageKit upload succeeded but no URL returned"
                        )
                
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload image to ImageKit: {str(e)}"
                )
        
        return uploaded_urls

    def delete_product_images(self, image_urls: List[str]) -> None:
        """Delete product images from ImageKit."""
        for url in image_urls:
            try:
                # Extract file path from ImageKit URL
                if settings.imagekit_url_endpoint in url:
                    # Get the file path after the endpoint
                    path_part = url.replace(settings.imagekit_url_endpoint, "")
                    if path_part.startswith("/"):
                        path_part = path_part[1:]
                    
                    # List files to find the one with matching path
                    list_result = self.imagekit.list_files({
                        "path": "/products/",
                        "limit": 100
                    })
                    
                    # Handle both dict and object responses
                    file_list = []
                    if isinstance(list_result, dict):
                        file_list = list_result.get('list', [])
                    elif hasattr(list_result, 'list'):
                        file_list = list_result.list
                    
                    if file_list:
                        # Find the file by matching the URL or file path
                        target_file = None
                        for file_info in file_list:
                            file_url = file_info.get('url') if isinstance(file_info, dict) else getattr(file_info, 'url', None)
                            file_path = file_info.get('filePath') if isinstance(file_info, dict) else getattr(file_info, 'filePath', None)
                            
                            if file_url == url:
                                target_file = file_info
                                break
                            elif file_path and file_path in path_part:
                                target_file = file_info
                                break
                        
                        if target_file:
                            file_id = target_file.get('fileId') if isinstance(target_file, dict) else getattr(target_file, 'fileId', None)
                            if file_id:
                                delete_result = self.imagekit.delete_file(file_id)
                                
                                # Check delete result
                                error = None
                                if isinstance(delete_result, dict):
                                    error = delete_result.get('error')
                                elif hasattr(delete_result, 'error'):
                                    error = delete_result.error
                                
                                if error:
                                    print(f"Warning: Failed to delete image {url} from ImageKit: {error}")
                            else:
                                print(f"Warning: Could not find file ID for image: {url}")
                        else:
                            print(f"Warning: Image not found in ImageKit: {url}")
                    else:
                        print(f"Warning: No files found in ImageKit products folder")
                        
            except Exception as e:
                print(f"Warning: Failed to delete image {url} from ImageKit: {str(e)}")

    def get_upload_signature(self, token: str, expire: int) -> dict:
        """Generate upload signature for client-side uploads."""
        try:
            auth_params = self.imagekit.get_authentication_parameters(token, expire)
            
            # Handle both dict and object responses
            if isinstance(auth_params, dict):
                return {
                    "signature": auth_params.get("signature"),
                    "expire": auth_params.get("expire"),
                    "token": auth_params.get("token")
                }
            else:
                return {
                    "signature": getattr(auth_params, 'signature', None),
                    "expire": getattr(auth_params, 'expire', None),
                    "token": getattr(auth_params, 'token', None)
                }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate upload signature: {str(e)}"
            )

# Create global instance (will be initialized when first accessed)
_imagekit_service: Optional[ImageKitService] = None

def get_imagekit_service() -> ImageKitService:
    """Get ImageKit service instance."""
    global _imagekit_service
    if _imagekit_service is None:
        _imagekit_service = ImageKitService()
    return _imagekit_service
