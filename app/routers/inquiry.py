from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from app.schemas import InquiryRequest, APIResponse
from app.services.email import email_service

router = APIRouter(
    prefix="/inquiry",
    tags=["Inquiry"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.post("/contact", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def submit_inquiry(inquiry: InquiryRequest, background_tasks: BackgroundTasks):
    """
    Submit a customer inquiry/contact form.
    
    This endpoint accepts customer inquiries and:
    1. Sends a notification email to the admin
    2. Sends a confirmation email to the customer
    3. Returns a success response
    
    **Request Body:**
    - **first_name**: Customer's first name (required)
    - **last_name**: Customer's last name (required) 
    - **email**: Customer's email address (required)
    - **phone_number**: Customer's phone number (optional)
    - **subject**: Inquiry subject (required)
    - **message**: Inquiry message (required, min 10 characters)
    - **subscribe_newsletter**: Whether to subscribe to newsletter (optional)
    """
    try:
        # Log the inquiry
        logger.info(f"New inquiry received from {inquiry.email} - Subject: {inquiry.subject}")
        
        # Prepare inquiry data for email
        inquiry_data = {
            "first_name": inquiry.first_name,
            "last_name": inquiry.last_name,
            "email": inquiry.email,
            "phone_number": inquiry.phone_number,
            "subject": inquiry.subject,
            "message": inquiry.message,
            "subscribe_newsletter": inquiry.subscribe_newsletter,
            "submitted_at": datetime.now().isoformat()
        }
        
        # Send emails in the background to avoid blocking the response
        background_tasks.add_task(email_service.send_inquiry_notification, inquiry_data)
        
        # Generate a reference number for the inquiry
        reference_id = f"INQ-{datetime.now().strftime('%Y%m%d')}-{hash(inquiry.email) % 10000:04d}"
        
        logger.info(f"Inquiry {reference_id} processed successfully")
        
        return APIResponse(
            success=True,
            message="Thank you for your inquiry! We have received your message and will get back to you soon.",
            data={
                "reference_id": reference_id,
                "submitted_at": datetime.now().isoformat(),
                "status": "received"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing inquiry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process your inquiry at the moment. Please try again later."
        )

@router.get("/contact/test", tags=["Testing"])
async def test_email_service():
    """
    Test endpoint to verify email service configuration.
    This endpoint is for testing purposes only.
    """
    try:
        # Test email data
        test_inquiry = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone_number": "+1234567890",
            "subject": "Test Inquiry",
            "message": "This is a test inquiry to verify the email service is working properly.",
            "subscribe_newsletter": False,
            "submitted_at": datetime.now().isoformat()
        }
        
        # Try to send test emails
        email_sent = email_service.send_inquiry_notification(test_inquiry)
        
        if email_sent:
            return APIResponse(
                success=True,
                message="Email service is working correctly!",
                data={"test_completed": True, "timestamp": datetime.now().isoformat()}
            )
        else:
            return APIResponse(
                success=False,
                message="Email service test failed. Please check email configuration.",
                data={"test_completed": False, "timestamp": datetime.now().isoformat()}
            )
            
    except Exception as e:
        logger.error(f"Email service test failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email service test failed: {str(e)}"
        )

@router.get("/subjects", tags=["Inquiry"])
async def get_inquiry_subjects():
    """
    Get predefined inquiry subjects for the contact form dropdown.
    """
    subjects = [
        "General Inquiry",
        "Custom Order Request", 
        "Product Information",
        "Technical Support",
        "Bulk Order Inquiry",
        "Collaboration Opportunity",
        "Complaint",
        "Feedback",
        "Other"
    ]
    
    return APIResponse(
        success=True,
        message="Inquiry subjects retrieved successfully",
        data={"subjects": subjects}
    )
