import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ColorSchemeScript, MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import { ModalsProvider } from '@mantine/modals'
import { theme } from '@/lib/theme'
import { AppProvider } from '@/providers/AppProvider'

import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'
import '@mantine/dates/styles.css'
import '@mantine/dropzone/styles.css'
import '@mantine/charts/styles.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Stock Research Tool - Claude-Powered Analysis',
  description: 'AI-powered stock research and analysis using Claude AI with Yahoo Finance MCP',
  keywords: 'ai, stock research, analysis, claude, finance, yahoo finance, mcp, watchlist',
  authors: [{ name: 'AI Stock Research Tool' }],
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#1a1b1e' }
  ],
  viewport: 'width=device-width, initial-scale=1',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png'
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ColorSchemeScript />
      </head>
      <body className={inter.className}>
        <MantineProvider theme={theme}>
          <ModalsProvider>
            <Notifications position="top-right" />
            <AppProvider>
              {children}
            </AppProvider>
          </ModalsProvider>
        </MantineProvider>
      </body>
    </html>
  )
}
