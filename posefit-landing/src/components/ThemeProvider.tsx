"use client"

import { ThemeProvider as NextThemesProvider } from "next-themes"
import type { ReactNode } from "react"

export function ThemeProvider({ children, ...props }: { children: ReactNode }) {
  return (
    <NextThemesProvider {...props} attribute="data-theme" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  )
} 