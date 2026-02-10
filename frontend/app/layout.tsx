import type { Metadata } from "next";
import localFont from "next/font/local";
import "../styles/globals.css";
import { ProjectProvider } from "@/context/ProjectContext";
import NavbarWrapper from "@/components/NavbarWrapper";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "NDA Review AI",
  description: "Professional NDA Review & Negotiation Assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-muted text-foreground`}
      >
        <ProjectProvider>
          <div className="flex flex-col h-screen overflow-hidden">
            <NavbarWrapper />
            <main className="flex-1 overflow-y-auto">
              {children}
            </main>
          </div>
        </ProjectProvider>
      </body>
    </html>
  );
}
