import { Suspense } from 'react'
import Link from "next/link";

export default function Home() {
  return (
    <>
      <main>
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto bg-base-100 flex flex-col lg:flex-row items-center justify-center gap-16 lg:gap-20 px-8 py-8 lg:py-20">
          <div className="flex flex-col gap-10 lg:gap-14 items-center justify-center text-center lg:text-left lg:items-start">
            <h1 className="font-extrabold text-4xl lg:text-6xl tracking-tight md:-mb-4">
              Monitor Your{" "}
              <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Competition
              </span>{" "}
              in Real-Time
            </h1>
            <p className="text-lg opacity-80 leading-relaxed max-w-md">
              Get instant alerts on competitor activities including layoffs, acquisitions, funding rounds, and executive changes. Stay ahead with automated intelligence.
            </p>
            <Link 
              href="/competitors" 
              className="btn btn-primary btn-wide gap-2"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="w-5 h-5"
              >
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
              </svg>
              View Intelligence Dashboard
            </Link>
          </div>
        </section>
      </main>
    </>
  );
}