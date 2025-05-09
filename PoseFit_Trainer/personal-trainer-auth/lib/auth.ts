import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  session: {
    strategy: "jwt",
  },
  pages: {
    signIn: "/login",
  },
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // In development mode, allow any login
          if (process.env.NODE_ENV !== 'production') {
            console.log('Development mode: allowing any login');
            return {
              id: credentials.email,
              email: credentials.email,
              name: credentials.email.split('@')[0], // Use part before @ as name
            };
          }

          // Try to authenticate against the backend API
          try {
            const response = await fetch(`${process.env.BACKEND_URL || "http://localhost:8002"}/token`, {
              method: "POST",
              headers: {
                "Content-Type": "application/x-www-form-urlencoded",
              },
              body: new URLSearchParams({
                username: credentials.email,
                password: credentials.password,
              }),
            });
            
            if (response.ok) {
              const data = await response.json();
              
              // Create a user object with the token
              return {
                id: credentials.email,
                email: credentials.email,
                name: credentials.email.split('@')[0],
                token: data.access_token,
              };
            }
          } catch (apiError) {
            console.error("API authentication error:", apiError);
          }
          
          return null;
        } catch (error) {
          console.error("Auth error:", error);
          return null;
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        // Add token from backend if available
        if ('token' in user) {
          token.backendToken = user.token;
        }
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string;
        session.user.email = token.email as string;
        // Pass token to session if available
        if ('backendToken' in token) {
          session.user.token = token.backendToken as string;
        }
      }
      return session;
    }
  }
}; 