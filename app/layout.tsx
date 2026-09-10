import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'RaceTime Copilot | Ask the race. Follow the evidence.',
  description:
    'Time-range race recaps with timestamped evidence, uncertainty checks, and spoiler boundaries.',
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
