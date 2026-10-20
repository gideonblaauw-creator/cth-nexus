import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CTH Idea Browser — CleantechHUB',
  description: '233 cleantech startup ideas from ClimateLaunchpad 2026',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        <link rel="stylesheet" href="/nexus-assets/nexus-brand.css" />
      </head>
      <body className="font-sans antialiased" data-nexus-page="ideas">
        {children}
        <script src="/nexus-assets/nexus-nav.js" defer />
      </body>
    </html>
  );
}
