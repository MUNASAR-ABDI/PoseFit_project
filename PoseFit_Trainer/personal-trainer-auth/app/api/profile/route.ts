import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET() {
  const session = cookies().get('session');

  if (!session?.value) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const response = await fetch(`${process.env.API_URL || 'http://localhost:8002'}/profile`, {
      headers: {
        'Authorization': `Bearer ${session.value}`,
        'Accept': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json({ error }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching profile:", error);
    return NextResponse.json({ error: 'Failed to fetch profile' }, { status: 500 });
  }
} 