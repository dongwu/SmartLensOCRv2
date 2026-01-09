
import { TextRegion } from "../types";

/**
 * SERVICE LAYER - Backend Integration
 * 
 * This service communicates with the Python FastAPI backend.
 * The backend handles all Gemini API calls securely on the server side.
 * 
 * API URL is determined by:
 * 1. Runtime config injected in Docker: window.__APP_CONFIG__.API_URL (Cloud Run)
 * 2. Build-time environment variable: VITE_API_URL (development)
 * 3. Default fallback: http://localhost:8000 (local development)
 */

const getAPIUrl = (): string => {
  // Check if runtime config exists (Docker/Cloud Run environment)
  if (typeof window !== 'undefined' && (window as any).__APP_CONFIG__?.API_URL) {
    const url = (window as any).__APP_CONFIG__.API_URL;
    console.log('[GeminiService] Using API_URL from runtime config:', url);
    return url;
  }
  // Fall back to build-time environment variable or localhost
  const url = import.meta.env.VITE_API_URL || "http://localhost:8000";
  console.log('[GeminiService] Using API_URL from build env:', url);
  return url;
};

// Do not evaluate API URL at module load time. Call `getAPIUrl()` at runtime
// so the value injected by `/config.js` is used when available.

/**
 * Phase 1: Layout Analysis via Backend
 * Sends image to backend which uses Gemini Vision API to detect text blocks
 */
export const detectRegions = async (base64Image: string): Promise<TextRegion[]> => {
  try {
    const apiUrl = getAPIUrl();
    console.log('[GeminiService] detectRegions request to:', `${apiUrl}/api/detect-regions`);
    const response = await fetch(`${apiUrl}/api/detect-regions`, {
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
    const apiUrl = getAPIUrl();
    const response = await fetch(`${apiUrl}/api/extract-text`, {
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
