export const API_BASE_URL = import.meta.env.VITE_API_URL || "https://complianceai-backend-ua6s.onrender.com/api/v1";

// Log the API URL being used (helps with debugging deployment issues)
if (import.meta.env.DEV) {
    console.log('🔗 API Base URL:', API_BASE_URL);
}
