import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'T1_AD - SageMaker Processing & Feature Engineering',
  description: 'AI/ML Project Dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  )
}
