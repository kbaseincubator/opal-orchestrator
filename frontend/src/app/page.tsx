'use client';

import Image from 'next/image';
import Link from 'next/link';

const MEMBER_LABS = [
  { name: 'Argonne', abbr: 'ANL', focus: 'Synthetic Biology & Automation' },
  { name: 'Lawrence Berkeley', abbr: 'LBNL', focus: 'Genomics & Sequencing' },
  { name: 'Pacific Northwest', abbr: 'PNNL', focus: 'Proteomics & Metabolomics' },
  { name: 'Oak Ridge', abbr: 'ORNL', focus: 'Plant Phenotyping' },
];

const FEATURES = [
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    title: 'Discover Capabilities',
    description: 'Search across all OPAL member labs to find the exact research capabilities you need, from sequencing to phenotyping.',
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
    title: 'Generate Research Plans',
    description: 'Get structured, multi-step research plans that leverage capabilities across multiple labs with clear dependencies.',
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    title: 'Citation-Backed Recommendations',
    description: 'Every recommendation is grounded in source documents from the capability registry, never fabricated.',
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    title: 'Fastest Learning Path',
    description: 'Plans are optimized for the fastest path to scientific insight, identifying what can run in parallel vs. sequential.',
  },
];

const USE_CASES = [
  'Engineer drought-tolerant microbial strains for plant growth promotion',
  'Design high-throughput phenotyping experiments for bioenergy crops',
  'Develop metabolic engineering strategies for biofuel production',
  'Plan multi-omics characterization of plant-microbe interactions',
];

const WORKFLOW_STEPS = [
  {
    step: '1',
    title: 'Describe Your Goal',
    description: 'Tell the assistant about your research objectives, target organisms, and constraints.',
  },
  {
    step: '2',
    title: 'AI Searches Capabilities',
    description: 'The orchestrator searches the OPAL capability registry to find relevant labs and resources.',
  },
  {
    step: '3',
    title: 'Review & Refine',
    description: 'Answer clarifying questions and refine the plan based on your specific needs.',
  },
  {
    step: '4',
    title: 'Get Your Plan',
    description: 'Receive a structured research plan with steps, dependencies, and citations.',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-opal-navy via-opal-navy-light to-opal-purple overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-opal-teal rounded-full filter blur-3xl -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-opal-magenta rounded-full filter blur-3xl translate-x-1/2 translate-y-1/2" />
        </div>

        <div className="relative max-w-7xl mx-auto px-6 py-20 lg:py-28">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-opal-100 text-sm mb-8">
              <span className="w-2 h-2 bg-opal-gold rounded-full animate-pulse" />
              DOE Biological & Environmental Research
            </div>

            {/* Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
              Plan Cross-Lab Research<br />
              <span className="text-opal-gold">Across the OPAL Network</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-opal-200 max-w-3xl mx-auto mb-10">
              The OPAL Orchestrator helps scientists discover capabilities across four DOE national laboratories
              and generate structured research plans with AI-powered assistance.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/chat"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-opal-gold hover:bg-opal-gold-dark text-opal-navy font-semibold rounded-lg transition-colors shadow-lg hover:shadow-xl"
              >
                Start Planning
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <Link
                href="/capabilities"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg transition-colors backdrop-blur-sm"
              >
                Browse Capabilities
              </Link>
            </div>
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="white"/>
          </svg>
        </div>
      </section>

      {/* What is OPAL Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-opal-navy mb-4">
              What is OPAL?
            </h2>
            <p className="text-lg text-opal-600 max-w-3xl mx-auto">
              <strong>OPAL (Orchestrated Platform for Autonomous Laboratories)</strong> is a DOE-funded consortium
              that brings together four national laboratories to advance bioenergy and bioproduct research
              through integrated, AI-orchestrated experimental campaigns.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature, i) => (
              <div
                key={i}
                className="p-6 bg-opal-50 rounded-xl border border-opal-100 hover:border-opal-teal hover:shadow-lg transition-all"
              >
                <div className="w-14 h-14 bg-opal-teal/20 rounded-lg flex items-center justify-center text-opal-teal mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-opal-navy mb-2">{feature.title}</h3>
                <p className="text-opal-600 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 bg-opal-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-opal-navy mb-4">How It Works</h2>
            <p className="text-lg text-opal-600">
              From research goal to actionable plan in four simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {WORKFLOW_STEPS.map((item, i) => (
              <div key={i} className="relative">
                {/* Connector Line */}
                {i < WORKFLOW_STEPS.length - 1 && (
                  <div className="hidden md:block absolute top-8 left-1/2 w-full h-0.5 bg-opal-200" />
                )}

                <div className="relative bg-white rounded-xl p-6 shadow-sm border border-opal-100 text-center">
                  {/* Step Number */}
                  <div className="w-16 h-16 bg-opal-navy text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4 relative z-10">
                    {item.step}
                  </div>
                  <h3 className="text-lg font-semibold text-opal-navy mb-2">{item.title}</h3>
                  <p className="text-opal-600 text-sm">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Vision Section with Infographic */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-opal-navy mb-4">The OPAL Vision</h2>
            <p className="text-lg text-opal-600 max-w-3xl mx-auto">
              AI-powered orchestration of autonomous bio-labs for DOE bioeconomy goals.
              The OPAL Orchestration Agent coordinates experiments across member labs,
              optimizing for scientific impact and resource utilization.
            </p>
          </div>

          {/* Infographic */}
          <div className="bg-opal-50 rounded-2xl p-4 md:p-8 border border-opal-200">
            <Image
              src="/opal-vision.jpg"
              alt="OPAL Orchestration Vision - AI Agent Orchestration of Autonomous Bio-Labs for DOE Bioeconomy Goals"
              width={1200}
              height={700}
              className="w-full h-auto rounded-lg"
              priority
            />
          </div>

          {/* Key Components */}
          <div className="mt-8 grid md:grid-cols-3 gap-6">
            <div className="p-5 bg-opal-teal/10 rounded-lg border border-opal-teal/20">
              <h4 className="font-semibold text-opal-navy mb-2">Research Dialogue</h4>
              <p className="text-sm text-opal-600">
                Natural language interface to describe high-level research objectives and constraints
              </p>
            </div>
            <div className="p-5 bg-opal-purple/10 rounded-lg border border-opal-purple/20">
              <h4 className="font-semibold text-opal-navy mb-2">Staged Campaign Orchestration</h4>
              <p className="text-sm text-opal-600">
                Multi-stage experimental campaigns with iterative refinement based on real data
              </p>
            </div>
            <div className="p-5 bg-opal-gold/10 rounded-lg border border-opal-gold/20">
              <h4 className="font-semibold text-opal-navy mb-2">Autonomous Member Labs</h4>
              <p className="text-sm text-opal-600">
                Protein design, microbial biodesign, plant phenotyping, and more across DOE facilities
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Member Labs Section */}
      <section className="py-16 bg-opal-navy">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">OPAL Member Labs</h2>
            <p className="text-lg text-opal-200">
              Four DOE national laboratories contributing unique capabilities
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {MEMBER_LABS.map((lab, i) => (
              <div
                key={i}
                className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center hover:bg-white/20 transition-colors"
              >
                <div className="text-2xl font-bold text-opal-gold mb-1">{lab.abbr}</div>
                <div className="text-xs text-opal-200 mb-2">{lab.name}</div>
                <div className="text-xs text-opal-300">{lab.focus}</div>
              </div>
            ))}
          </div>

          <div className="text-center mt-8">
            <Link
              href="/sources"
              className="inline-flex items-center gap-2 text-opal-gold hover:text-opal-gold-light font-medium"
            >
              Learn more about member labs
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Example Use Cases */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-opal-navy mb-4">Example Research Goals</h2>
            <p className="text-lg text-opal-600">
              Here are some examples of what you can plan with the OPAL Orchestrator
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            {USE_CASES.map((useCase, i) => (
              <Link
                key={i}
                href={`/chat?goal=${encodeURIComponent(useCase)}`}
                className="flex items-center gap-4 p-5 bg-opal-50 rounded-lg border border-opal-200 hover:border-opal-teal hover:shadow-md transition-all group"
              >
                <div className="w-10 h-10 bg-opal-teal/20 rounded-lg flex items-center justify-center text-opal-teal flex-shrink-0 group-hover:bg-opal-teal group-hover:text-white transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <span className="text-opal-700 group-hover:text-opal-navy transition-colors">{useCase}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-r from-opal-teal to-opal-purple">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Plan Your Research?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Start a conversation with the OPAL Orchestrator and discover how to leverage
            capabilities across the DOE national laboratory network.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center justify-center gap-2 px-10 py-5 bg-white hover:bg-opal-50 text-opal-navy font-semibold rounded-lg transition-colors shadow-lg hover:shadow-xl text-lg"
          >
            Start Planning Now
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-opal-navy-dark py-8">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Image src="/opal-logo.jpg" alt="OPAL" width={32} height={32} className="rounded" />
              <span className="text-opal-200 text-sm">
                OPAL Orchestrator - Orchestrated Platform for Autonomous Laboratories
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm">
              <a
                href="https://opal-doe.org/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-opal-300 hover:text-white transition-colors"
              >
                OPAL Project
              </a>
              <a
                href="https://www.energy.gov/science/ber"
                target="_blank"
                rel="noopener noreferrer"
                className="text-opal-300 hover:text-white transition-colors"
              >
                DOE BER
              </a>
              <Link href="/sources" className="text-opal-300 hover:text-white transition-colors">
                Member Labs
              </Link>
              <Link href="/capabilities" className="text-opal-300 hover:text-white transition-colors">
                Capabilities
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
