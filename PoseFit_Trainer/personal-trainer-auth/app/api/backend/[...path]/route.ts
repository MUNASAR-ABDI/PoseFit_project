import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8002";

/**
 * This is a proxy endpoint to forward requests to the backend server.
 * It helps overcome CORS issues and network connectivity problems.
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const path = params.path.join("/");
    console.log(`[API Proxy] Forwarding GET request to: ${path}`);

    // Get query parameters
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    
    // Get headers except host and connection
    const headers: HeadersInit = {};
    request.headers.forEach((value, key) => {
      if (key !== 'host' && key !== 'connection') {
        headers[key] = value;
      }
    });

    // Forward the request to the backend
    const response = await fetch(
      `${BACKEND_URL}/${path}${queryString ? `?${queryString}` : ''}`,
      {
        method: "GET",
        headers,
        credentials: "include",
      }
    );

    // Get response data
    const data = await response.json();

    // Return the response
    return NextResponse.json(data, {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  } catch (error) {
    console.error("[API Proxy] Error forwarding GET request:", error);
    return NextResponse.json(
      { error: "Failed to connect to backend server" },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const path = params.path.join("/");
    console.log(`[API Proxy] Forwarding POST request to: ${path}`);

    // Get request body
    let body;
    try {
      body = await request.json();
    } catch (e) {
      console.warn("[API Proxy] Could not parse request body as JSON");
      body = null;
    }

    // Get headers except host and connection
    const headers: HeadersInit = {};
    request.headers.forEach((value, key) => {
      if (key !== 'host' && key !== 'connection') {
        headers[key] = value;
      }
    });

    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/${path}`, {
      method: "POST",
      headers,
      body: body ? JSON.stringify(body) : null,
      credentials: "include",
    });

    // Get response data
    const data = await response.json();

    // Return the response
    return NextResponse.json(data, {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  } catch (error) {
    console.error("[API Proxy] Error forwarding POST request:", error);
    return NextResponse.json(
      { error: "Failed to connect to backend server" },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
} 