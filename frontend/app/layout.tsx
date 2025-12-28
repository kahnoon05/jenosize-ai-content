/**
 * Root Layout Component
 *
 * Main layout for the Jenosize AI Content Generation application.
 * Configures fonts, metadata, and provides React Query context.
 */

import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Jenosize AI Content Generator',
  description:
    'Generate high-quality business trend and future ideas articles powered by AI',
  keywords: [
    'AI content generation',
    'business trends',
    'future ideas',
    'Jenosize',
    'article generator',
    'content creation',
  ],
  authors: [{ name: 'Jenosize' }],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0ea5e9',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
