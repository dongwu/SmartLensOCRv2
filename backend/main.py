"""
SmartLensOCR Backend Server
Main FastAPI application for handling OCR processing, user management, and credit system.
"""

import os
import json
import base64
import sqlite3
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="SmartLensOCR Backend", version="1.0.0")

# Configure CORS for frontend communication
# Allow only specific frontend URL(s) for security
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")  # Default for local development
allow_origins = [
    url.strip() for url in FRONTEND_URL.split(",") if url.strip()
]  # Support multiple URLs separated by commas

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

print(f"[SmartLensOCR] CORS allowed origins: {allow_origins}", flush=True)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Database configuration
# Use /mnt for persistent storage (mounted Cloud Storage bucket in Cloud Run)
# Fallback to local directory if /mnt is not available (local development)
DB_DIR = "/mnt" if os.path.exists("/mnt") else os.path.dirname(__file__)
DB_PATH = os.path.join(DB_DIR, "smartlensocr.db")

# Ensure DB directory exists
os.makedirs(DB_DIR, exist_ok=True)
print(f"[SmartLensOCR] Database initialized at: {DB_PATH}", flush=True)

# ============================================================================
# MODELS
# ============================================================================

class BoundingBox(BaseModel):
    ymin: float
    xmin: float
    ymax: float
    xmax: float


class TextRegion(BaseModel):
    id: str
    box: BoundingBox
    order: int
    description: str
    extractedText: Optional[str] = None
    isActive: bool


class DetectRegionsRequest(BaseModel):
    """Request model for region detection"""
    imageBase64: str


class ExtractTextRequest(BaseModel):
    """Request model for text extraction"""
    imageBase64: str
    regions: List[TextRegion]


class UserCreateRequest(BaseModel):
    """Request model for user creation"""
    email: str


class UserResponse(BaseModel):
    """Response model for user data"""
    id: str
    email: str
    credits: int
    isPro: bool
    created_at: str


class CreditUpdateRequest(BaseModel):
    """Request model for credit updates"""
    amount: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str


# ============================================================================
# DATABASE INITIALIZATION & MANAGEMENT
# ============================================================================

def init_db():
    """Initialize SQLite database with required tables"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                credits INTEGER DEFAULT 5,
                isPro INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()


@contextmanager
def get_db():
    """Get database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ============================================================================
# GEMINI SERVICE LAYER
# ============================================================================

class GeminiService:
    """Service layer for Gemini API interactions"""
    
    @staticmethod
    def detect_regions(base64_image: str) -> List[dict]:
        """
        Detect text regions in an image using Gemini's vision capabilities.
        
        Args:
            base64_image: Base64 encoded image string
            
        Returns:
            List of detected text regions with bounding boxes
        """
        try:
            # Decode base64 to bytes
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # Initialize model
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = """Identify all major blocks of text in this image.

Grouping Rule: Do not separate individual paragraphs if they are clearly one after another.
Group adjacent paragraphs into a single logical region. Only create separate regions when
there are clear, wide separations.

Coordinates must be in normalized range (0 to 1000).

Return ONLY valid JSON array with objects containing: description, ymin, xmin, ymax, xmax
No markdown, no code blocks, just raw JSON."""

            response = model.generate_content([
                prompt,
                image
            ])
            
            # Parse response as JSON
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            regions_data = json.loads(response_text)
            
            return regions_data
            
        except Exception as e:
            raise Exception(f"Error detecting regions: {str(e)}")
    
    @staticmethod
    def extract_text_from_regions(base64_image: str, regions: List[TextRegion]) -> str:
        """
        Extract text from specified regions using Gemini's OCR capabilities.
        
        Args:
            base64_image: Base64 encoded image string
            regions: List of text regions to extract
            
        Returns:
            Extracted text from all regions
        """
        try:
            # Filter active regions and sort by order
            active_regions = sorted(
                [r for r in regions if r.isActive],
                key=lambda x: x.order
            )
            
            if not active_regions:
                return ""
            
            # Decode base64 to bytes
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # Initialize model
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Build regions description
            regions_description = "\n".join([
                f"Region {r.order}: coordinates [{r.box.ymin}, {r.box.xmin}, {r.box.ymax}, {r.box.xmax}] - {r.description}"
                for r in active_regions
            ])
            
            prompt = f"""Perform OCR on the provided image following the sequence of regions below.
Return ONLY the extracted text, separated by double newlines between regions.
Do not include any explanations, markdown, or metadata.

Regions to process (in order):
{regions_description}

Extract text exactly as it appears, maintaining formatting where possible."""

            response = model.generate_content([
                prompt,
                image
            ])
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")


# ============================================================================
# USER MANAGEMENT
# ============================================================================

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Retrieve user from database by ID"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    """Retrieve user from database by email"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None


def create_user(user_id: str, email: str) -> dict:
    """Create new user in database"""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (id, email, credits, isPro) VALUES (?, ?, ?, ?)",
            (user_id, email, 5, 0)
        )
        conn.commit()
    return get_user_by_id(user_id)


def update_user_credits(user_id: str, amount: int) -> dict:
    """Update user credits (can be positive or negative)"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT credits FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_credits = max(0, user['credits'] + amount)
        
        conn.execute(
            "UPDATE users SET credits = ? WHERE id = ?",
            (new_credits, user_id)
        )
        
        conn.execute(
            "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
            (user_id, amount, "debit" if amount < 0 else "credit", "Credit adjustment")
        )
        
        conn.commit()
    
    return get_user_by_id(user_id)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize database on app startup"""
    init_db()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/api/users", response_model=UserResponse)
async def create_or_get_user(request: UserCreateRequest):
    """
    Create a new user or return existing user.
    
    This endpoint is called during login to get or create a user account.
    """
    email = request.email.strip().lower()
    
    # Check if user exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return UserResponse(
            id=existing_user['id'],
            email=existing_user['email'],
            credits=existing_user['credits'],
            isPro=bool(existing_user['isPro']),
            created_at=existing_user['created_at']
        )
    
    # Create new user
    import uuid
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    user = create_user(user_id, email)
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        credits=user['credits'],
        isPro=bool(user['isPro']),
        created_at=user['created_at']
    )


@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Retrieve user information"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        credits=user['credits'],
        isPro=bool(user['isPro']),
        created_at=user['created_at']
    )


@app.post("/api/users/{user_id}/credits")
async def update_credits(user_id: str, request: CreditUpdateRequest):
    """Update user credits"""
    user = update_user_credits(user_id, request.amount)
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        credits=user['credits'],
        isPro=bool(user['isPro']),
        created_at=user['created_at']
    )


@app.post("/api/detect-regions")
async def detect_regions(request: DetectRegionsRequest):
    """
    Detect text regions in an uploaded image.
    
    This endpoint uses Gemini's vision model to identify all text blocks
    and their bounding boxes in the provided image.
    
    Args:
        request: Contains base64 encoded image
        
    Returns:
        List of detected regions with bounding boxes and descriptions
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    try:
        regions = GeminiService.detect_regions(request.imageBase64)
        
        # Transform response to match frontend expectations
        response_regions = []
        for idx, region in enumerate(regions):
            response_regions.append({
                "id": f"region_{idx}_{int(datetime.now().timestamp() * 1000)}",
                "description": region.get("description", "Untitled"),
                "box": {
                    "ymin": region.get("ymin", 0),
                    "xmin": region.get("xmin", 0),
                    "ymax": region.get("ymax", 1000),
                    "xmax": region.get("xmax", 1000)
                },
                "order": idx + 1,
                "isActive": True
            })
        
        return {"regions": response_regions}
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid response format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting regions: {str(e)}")


@app.post("/api/extract-text")
async def extract_text(request: ExtractTextRequest):
    """
    Extract text from specified regions in an image.
    
    This endpoint performs OCR on the specified regions of the image
    and returns the extracted text in the specified order.
    
    Args:
        request: Contains base64 encoded image and list of regions to extract
        
    Returns:
        Extracted text from all active regions
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    try:
        text = GeminiService.extract_text_from_regions(
            request.imageBase64,
            request.regions
        )
        
        return {"extractedText": text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")


@app.post("/api/process-document")
async def process_document(file: UploadFile = File(...)):
    """
    Process a complete document: detect regions and prepare for extraction.
    
    This is a combined endpoint for processing a complete document in one request.
    
    Args:
        file: Image file upload
        
    Returns:
        Detected regions from the image
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    try:
        # Read file content
        contents = await file.read()
        
        # Convert to base64
        base64_image = base64.b64encode(contents).decode("utf-8")
        
        # Detect regions
        regions = GeminiService.detect_regions(base64_image)
        
        # Transform response
        response_regions = []
        for idx, region in enumerate(regions):
            response_regions.append({
                "id": f"region_{idx}_{int(datetime.now().timestamp() * 1000)}",
                "description": region.get("description", "Untitled"),
                "box": {
                    "ymin": region.get("ymin", 0),
                    "xmin": region.get("xmin", 0),
                    "ymax": region.get("ymax", 1000),
                    "xmax": region.get("xmax", 1000)
                },
                "order": idx + 1,
                "isActive": True,
                "base64Data": base64_image
            })
        
        return {"regions": response_regions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SmartLensOCR Backend API",
        "version": "1.0.0",
        "description": "Backend server for intelligent document OCR processing",
        "endpoints": {
            "health": "/health",
            "users": {
                "create_or_get": "POST /api/users",
                "get": "GET /api/users/{user_id}",
                "update_credits": "POST /api/users/{user_id}/credits"
            },
            "ocr": {
                "detect_regions": "POST /api/detect-regions",
                "extract_text": "POST /api/extract-text",
                "process_document": "POST /api/process-document"
            }
        }
    }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
