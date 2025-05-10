"use client";

export default function LogoutRedirect() {
  // Forcefully reload the page and redirect to login page
  window.location.href = "/login?force=true";
  return null;
} 