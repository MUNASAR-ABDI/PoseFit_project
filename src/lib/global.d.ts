// Global TypeScript declarations

interface Window {
  // Clerk auth related
  Clerk?: {
    signOut: () => Promise<void>;
    isAuthenticated: boolean;
  };
  
  // Global auth state
  globalIsAuthenticated?: boolean;
  globalAuthChecked?: boolean;
  
  // Method to stop all pending network requests
  stop?: () => void;
} 