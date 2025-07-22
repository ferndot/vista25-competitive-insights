import { Suspense } from 'react'
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Link from "next/link";

export default function Home() {
  return (
    <>
      <Suspense>
        <Header />
      </Suspense>
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

          <div className="flex flex-col w-full lg:w-auto">
            {/* Demo Dashboard Preview */}
            <div className="mockup-window border border-base-300 bg-base-200 shadow-2xl max-w-lg">
              <div className="flex justify-center bg-base-200 px-4 py-16">
                <div className="w-full space-y-4">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-lg">Competitor Intelligence</h3>
                    <div className="badge badge-success gap-2">
                      <div className="w-2 h-2 rounded-full bg-current animate-pulse"></div>
                      Live
                    </div>
                  </div>
                  
                  {/* Sample competitor cards */}
                  <div className="space-y-3">
                    <div className="card bg-base-100 shadow-sm">
                      <div className="card-body p-4">
                        <div className="flex justify-between items-center">
                          <div>
                            <h4 className="font-semibold">Acme Corp</h4>
                            <p className="text-sm opacity-70">ACME</p>
                          </div>
                          <div className="flex gap-2">
                            <div className="badge badge-error badge-sm">3 Important</div>
                            <div className="badge badge-neutral badge-sm">12 Total</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="card bg-base-100 shadow-sm">
                      <div className="card-body p-4">
                        <div className="flex justify-between items-center">
                          <div>
                            <h4 className="font-semibold">Globex Inc</h4>
                            <p className="text-sm opacity-70">GLOB</p>
                          </div>
                          <div className="flex gap-2">
                            <div className="badge badge-error badge-sm">1 Important</div>
                            <div className="badge badge-neutral badge-sm">8 Total</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Sample alert */}
                  <div className="alert alert-error shadow-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <div className="text-sm">
                      <div className="font-semibold">Acme Corp announces layoffs</div>
                      <div className="opacity-80">2 minutes ago</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="bg-base-200">
          <div className="py-24 px-8 max-w-7xl mx-auto">
            <div className="flex flex-col text-center gap-12">
              <div className="flex flex-col gap-4">
                <h2 className="font-black text-3xl lg:text-5xl tracking-tight">
                  Built for the 24-Hour Hackathon
                </h2>
                <p className="text-lg opacity-80 leading-relaxed">
                  A complete competitor intelligence platform from idea to deployment
                </p>
              </div>
              
              <div className="flex flex-col md:flex-row gap-12 md:gap-8">
                <div className="flex flex-col gap-4 md:gap-6 items-center text-center bg-base-100 p-8 rounded-box shadow-sm">
                  <div className="bg-primary/10 p-4 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-primary">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="font-bold text-xl">Real-Time Monitoring</h3>
                  <p className="text-base-content/80 leading-relaxed">
                    NewsAPI integration with smart classification. Get notified instantly when competitors make important moves.
                  </p>
                </div>

                <div className="flex flex-col gap-4 md:gap-6 items-center text-center bg-base-100 p-8 rounded-box shadow-sm">
                  <div className="bg-secondary/10 p-4 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-secondary">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="font-bold text-xl">Smart Classification</h3>
                  <p className="text-base-content/80 leading-relaxed">
                    AI-powered detection of important events: layoffs, acquisitions, funding rounds, executive changes.
                  </p>
                </div>

                <div className="flex flex-col gap-4 md:gap-6 items-center text-center bg-base-100 p-8 rounded-box shadow-sm">
                  <div className="bg-accent/10 p-4 rounded-full">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-accent">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                    </svg>
                  </div>
                  <h3 className="font-bold text-xl">Modern Stack</h3>
                  <p className="text-base-content/80 leading-relaxed">
                    Next.js 14, Supabase realtime, DaisyUI components. Built for speed and scalability.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Tech Stack */}
        <section className="py-24 px-8 max-w-7xl mx-auto">
          <div className="text-center">
            <p className="text-sm uppercase font-semibold opacity-50 mb-8">Powered by</p>
            <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
              <div className="font-bold text-lg">Next.js 14</div>
              <div className="font-bold text-lg">Supabase</div>
              <div className="font-bold text-lg">DaisyUI</div>
              <div className="font-bold text-lg">NewsAPI</div>
              <div className="font-bold text-lg">React Hot Toast</div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-primary text-primary-content">
          <div className="py-24 px-8 max-w-7xl mx-auto text-center">
            <div className="flex flex-col gap-8 items-center">
              <h2 className="font-black text-3xl lg:text-5xl tracking-tight">
                Ready to Monitor Your Competition?
              </h2>
              <p className="text-lg opacity-90 leading-relaxed max-w-2xl">
                This MVP demonstrates real-time competitor intelligence with automated news scraping, smart classification, and instant notifications. Perfect for startups who need to stay ahead.
              </p>
              <div className="flex gap-4">
                <Link 
                  href="/competitors" 
                  className="btn btn-secondary btn-lg gap-2"
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
                  Launch Dashboard
                </Link>
                <a 
                  href="/api/scrape" 
                  target="_blank"
                  className="btn btn-outline btn-lg gap-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                  </svg>
                  Run Scraper
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}