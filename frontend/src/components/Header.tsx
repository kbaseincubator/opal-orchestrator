'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Header() {
  const pathname = usePathname();

  // Don't show header on landing page (it has its own)
  if (pathname === '/') {
    return null;
  }

  return (
    <header className="bg-opal-navy text-white px-6 py-3 shadow-lg">
      <div className="flex items-center justify-between max-w-[1920px] mx-auto">
        <Link href="/" className="flex items-center gap-4 hover:opacity-90 transition-opacity">
          <Image
            src="/opal-logo.jpg"
            alt="OPAL Logo"
            width={140}
            height={50}
            className="h-12 w-auto object-contain bg-white rounded px-2 py-1"
            priority
          />
          <div className="border-l border-opal-navy-light pl-4">
            <h1 className="text-lg font-semibold tracking-tight">
              Orchestrator
            </h1>
            <p className="text-opal-200 text-xs">
              Cross-Lab Research Planning
            </p>
          </div>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link
            href="/chat"
            className={`hover:text-opal-teal-light transition-colors ${
              pathname === '/chat' ? 'text-opal-gold font-medium' : ''
            }`}
          >
            Chat
          </Link>
          <Link
            href="/capabilities"
            className={`hover:text-opal-teal-light transition-colors ${
              pathname === '/capabilities' ? 'text-opal-gold font-medium' : ''
            }`}
          >
            Capabilities
          </Link>
          <Link
            href="/sources"
            className={`hover:text-opal-teal-light transition-colors ${
              pathname === '/sources' ? 'text-opal-gold font-medium' : ''
            }`}
          >
            Sources
          </Link>
          <a
            href="https://opal-doe.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-opal-gold hover:text-opal-gold-light transition-colors flex items-center gap-1"
          >
            OPAL Project
            <svg
              className="w-3 h-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </nav>
      </div>
    </header>
  );
}
