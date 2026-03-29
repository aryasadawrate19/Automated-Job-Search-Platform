import type { Metadata } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'JobIntel — Intelligent Job Matching Platform',
  description:
    'AI-powered job matching platform that aggregates listings, parses resumes, and delivers explainable job recommendations with hybrid scoring.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-surface text-content">
        <div id="app-root">{children}</div>
        <div id="modal-root" />
      </body>
    </html>
  );
}
