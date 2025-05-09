import axios from &apos;axios&apos;;

const apiClient = axios.create({
  baseURL: 'http://localhost:8005',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,  // Increased timeout
});

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with a status code outside of 2xx range
      console.error('Server Error:', error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Something happened in setting up the request
      console.error('Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient; 