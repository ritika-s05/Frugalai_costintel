import InfrastructureFlow from "./components/InfrastructureFlow";
import { useRef } from "react";
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
} from "motion/react";
import {
  Activity,
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Database,
  Layers3,
  ShieldCheck,
  Zap,
} from "lucide-react";

import AnalyticsDashboard from "./components/AnalyticsDashboard";
import "./App.css";

const features = [
  {
    number: "01",
    icon: <Layers3 size={25} strokeWidth={1.6} />,
    title: "Intelligent routing",
    description:
      "Match every request with a capable, cost-efficient model. Avoid expensive inference when a smaller model can handle the task.",
    tag: "SMART ROUTER",
  },
  {
    number: "02",
    icon: <ShieldCheck size={25} strokeWidth={1.6} />,
    title: "Budget protection",
    description:
      "Estimate token usage before execution and enforce spending limits with a dedicated preflight protection layer.",
    tag: "TOKEN GUARD",
  },
  {
    number: "03",
    icon: <Zap size={25} strokeWidth={1.6} />,
    title: "Semantic caching",
    description:
      "Recognize semantically similar requests and reuse previous responses instead of paying for unnecessary inference.",
    tag: "PERSISTENT CACHE",
  },
  {
    number: "04",
    icon: <Activity size={25} strokeWidth={1.6} />,
    title: "Cost observability",
    description:
      "Track requests, model-routing decisions, cache performance, provider latency and estimated savings.",
    tag: "ANALYTICS",
  },
];

function App() {
  const heroRef = useRef<HTMLElement>(null);
  const reduceMotion = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  });

  const animatedOpacity = useTransform(
    scrollYProgress,
    [0, 0.75],
    [1, 0]
  );

  const animatedScale = useTransform(
    scrollYProgress,
    [0, 1],
    [1, 0.94]
  );

  const heroOpacity = reduceMotion ? 1 : animatedOpacity;
  const heroScale = reduceMotion ? 1 : animatedScale;

  const reveal = {
    initial: reduceMotion
      ? { opacity: 1 }
      : { opacity: 0, y: 35 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, amount: 0.15 },
    transition: { duration: reduceMotion ? 0 : 0.65 },
  };

  return (
    <div className="app">
      {/* NAVIGATION */}

      <header className="navbar">
        <a
          className="brand"
          href="#home"
          aria-label="Frugal AI home"
        >
          <span className="brand-symbol">f.</span>
          <span className="brand-name">frugal</span>
        </a>

        <nav
          className="nav-links"
          aria-label="Main navigation"
        >
          <a href="#platform">Platform</a>
          <a href="#intelligence">Intelligence</a>
          <a href="#analytics">Analytics</a>
        </nav>

        <a className="nav-button" href="#analytics">
          Explore platform
          <ArrowUpRight size={16} strokeWidth={1.8} />
        </a>
      </header>

      <main>
        {/* HERO */}

        <section
          className="hero"
          id="home"
          ref={heroRef}
        >
          <motion.div
            className="hero-content"
            style={{
              opacity: heroOpacity,
              scale: heroScale,
            }}
          >
            <div className="hero-eyebrow">
              <span className="status-dot" />
              INTELLIGENT AI INFRASTRUCTURE
            </div>

            <h1 className="hero-title">
              Every token counts.
              <span>Make yours matter.</span>
            </h1>

            <p className="hero-description">
              Every AI request deserves the right model,
              the right resources, and the right cost.
              Meet the intelligence layer that makes
              it possible.
            </p>

            <div className="hero-actions">
              <a
                className="primary-button"
                href="#platform"
              >
                Discover Frugal
                <ArrowUpRight
                  size={17}
                  strokeWidth={1.8}
                />
              </a>

              <a
                className="text-button"
                href="#analytics"
              >
                View analytics
                <ArrowRight
                  size={16}
                  strokeWidth={1.8}
                />
              </a>
            </div>
          </motion.div>

          <div className="hero-bottom">
            <span>
              DESIGNED FOR EFFICIENT INTELLIGENCE
            </span>

            <a
              href="#platform"
              className="scroll-hint"
            >
              SCROLL TO EXPLORE
              <ArrowDown
                size={15}
                strokeWidth={1.6}
              />
            </a>
          </div>
        </section>

        {/* PLATFORM INTRODUCTION */}

        <section
          className="platform-section"
          id="platform"
        >
          <motion.div
            className="section-intro"
            {...reveal}
          >
            <span className="section-label">
              01 / THE PLATFORM
            </span>

            <h2>
              Built to make every
              <br />
              request count.
            </h2>

            <p>
              Frugal sits between your applications
              and AI providers, intelligently
              orchestrating requests while making
              infrastructure costs visible.
            </p>
          </motion.div>

          {/* INFRASTRUCTURE FLOW */}
          <motion.div {...reveal} className="infrastructure-container">
            <InfrastructureFlow />
          </motion.div>

          <motion.div>
            <div className="architecture-heading">
              <span className="architecture-label">
                HOW FRUGAL WORKS
              </span>

              <span className="architecture-subtitle">
                ONE INTELLIGENT EXECUTION LAYER
              </span>
            </div>

            <div className="architecture-flow">
              <div className="architecture-node">
                <span className="node-icon">
                  <Database
                    size={21}
                    strokeWidth={1.6}
                  />
                </span>

                <strong>Application</strong>
                <small>Incoming AI request</small>
              </div>

              <ArrowRight
                className="flow-arrow"
                size={22}
                strokeWidth={1.4}
              />

              <div className="architecture-node architecture-core">
                <span className="node-icon">
                  <Layers3
                    size={21}
                    strokeWidth={1.6}
                  />
                </span>

                <strong>Frugal gateway</strong>
                <small>
                  Route · Protect · Cache
                </small>
              </div>

              <ArrowRight
                className="flow-arrow"
                size={22}
                strokeWidth={1.4}
              />

              <div className="architecture-node">
                <span className="node-icon">
                  <Zap
                    size={21}
                    strokeWidth={1.6}
                  />
                </span>

                <strong>AI execution</strong>
                <small>
                  Cached response or provider
                </small>
              </div>
            </div>

            <div className="architecture-footer">
              <span className="architecture-pulse" />
              REQUEST TELEMETRY & COST ATTRIBUTION
            </div>
          </motion.div>

          {/* FEATURE CARDS */}

          <div
            className="intelligence-heading"
            id="intelligence"
          >
            <motion.div {...reveal}>
              <span className="section-label">
                THE INTELLIGENCE LAYER
              </span>

              <h2>
                Less overhead.
                <br />
                <em>More intelligence.</em>
              </h2>
            </motion.div>
          </div>

          <div className="feature-grid">
            {features.map((feature, index) => {
              const Icon = feature.icon;

              return (
                <motion.article
                  className="feature-card"
                  key={feature.number}
                  initial={
                    reduceMotion
                      ? { opacity: 1 }
                      : { opacity: 0, y: 35 }
                  }
                  whileInView={{
                    opacity: 1,
                    y: 0,
                  }}
                  viewport={{
                    once: true,
                    amount: 0.15,
                  }}
                  transition={{
                    duration: reduceMotion
                      ? 0
                      : 0.55,
                    delay: reduceMotion
                      ? 0
                      : index * 0.08,
                  }}
                >
                  <div className="feature-top">
                    <span className="feature-icon">
                      {Icon}
                    </span>

                    <span className="feature-number">
                      {feature.number}
                    </span>
                  </div>

                  <div className="feature-content">
                    <span className="feature-tag">
                      {feature.tag}
                    </span>

                    <h3>{feature.title}</h3>

                    <p>{feature.description}</p>
                  </div>
                </motion.article>
              );
            })}
          </div>
        </section>

        {/* LIVE ANALYTICS */}

        <section
          id="analytics"
          className="analytics-section"
        >
          <AnalyticsDashboard />
        </section>

        {/* FOOTER */}

        <footer className="footer">
          <a
            href="#home"
            className="footer-brand"
          >
            frugal.
          </a>

          <span>
            EVERY TOKEN COUNTS.
          </span>

          <a
            href="#home"
            className="footer-back"
          >
            BACK TO TOP
            <ArrowUpRight
              size={15}
              strokeWidth={1.6}
            />
          </a>
        </footer>
      </main>
    </div>
  );
}

export default App;