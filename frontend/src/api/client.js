import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const client = axios.create({
    baseURL: API_URL,
});

// Interceptors for error handling (optional but good practice)
client.interceptors.response.use(
    response => response,
    error => {
        // Log errors or handle global errors like 401 here
        console.error("API Call Failed:", error);
        return Promise.reject(error);
    }
);

export default client;
