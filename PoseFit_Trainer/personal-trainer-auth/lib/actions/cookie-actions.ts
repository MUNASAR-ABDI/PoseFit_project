'use server'

import { cookies } from 'next/headers'

/**
 * Server action to delete the session cookie
 */
export async function deleteSessionCookie() {
  const cookieStore = cookies()
  cookieStore.delete('session')
  return { success: true }
}

/**
 * Server action to set the session cookie
 */
export async function setSessionCookie(value: string, maxAge: number = 60 * 60 * 24 * 7) {
  const cookieStore = cookies()
  cookieStore.set('session', value, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge,
    path: '/',
  })
  return { success: true }
}

/**
 * Server action to set the next-url cookie for tracking current page
 */
export async function setNextUrlCookie(value: string) {
  const cookieStore = cookies()
  cookieStore.set('next-url', value, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    path: '/',
  })
  return { success: true }
}

/**
 * Server action to get cookie value
 */
export async function getCookieValue(name: string) {
  const cookieStore = cookies()
  const cookie = cookieStore.get(name)
  return cookie?.value || null
} 