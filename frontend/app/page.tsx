"use client";

import React from 'react';
import { FileText } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 max-w-4xl mx-auto w-full h-full bg-muted">
      <div className="flex flex-col items-center text-center space-y-12 w-full max-w-3xl">


        <h1 className="text-4xl md:text-5xl font-bold text-foreground tracking-tighter leading-tight whitespace-nowrap">
          NDA Review & <span className="text-primary">Negotiation AI</span>
        </h1>

        <div className="bg-surface border border-light rounded-2xl p-10 flex flex-col items-center gap-4 w-full shadow-sm">
          <p className="font-semibold text-foreground text-xl">
            Get Started
          </p>
          <p className="text-secondary-text text-center leading-relaxed text-sm">
            Select an existing project from the navbar or create a new one to begin your review process.
          </p>
        </div>
      </div>
    </div>
  );
}
