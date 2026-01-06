
import { TextRegion } from "../types";

/**
 * SERVICE LAYER - Backend Integration
 * 
 * This service communicates with the Python FastAPI backend at http://localhost:8000
 * The backend handles all Gemini API calls securely on the server side.
 */

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Phase 1: Layout Analysis via Backend
 * Sends image to backend which uses Gemini Vision API to detect text blocks
 */
export const detectRegions = async (base64Image: string): Promise<TextRegion[]> => {
  try {
    const response = await fetch(`${API_URL}/api/detect-regions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        imageBase64: base64Image,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to detect regions");
    }

    const data = await response.json();
    return data.regions;
  } catch (error: any) {
    console.error("Error detecting regions:", error);
    throw error;
  }
};

/**
 * Phase 2: High-Precision OCR via Backend
 * Sends image and regions to backend which uses Gemini OCR API for text extraction
 */
export const extractTextFromRegions = async (
  base64Image: string,
  regions: TextRegion[]
): Promise<string> => {
  // Filter active regions and sort by order
  const activeRegions = [...regions]
    .filter((r) => r.isActive)
    .sort((a, b) => a.order - b.order);

  if (activeRegions.length === 0) return "";

  try {
    const response = await fetch(`${API_URL}/api/extract-text`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        imageBase64: base64Image,
        regions: activeRegions,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to extract text");
    }

    const data = await response.json();
    return data.extractedText;
  } catch (error: any) {
    console.error("Error extracting text:", error);
    throw error;
  }
};
