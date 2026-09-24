import "./InfrastructureFlow.css";
import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  ArrowRight,
  Check,
  Circle,
  LoaderCircle,
  RotateCcw,
  Send,
} from "lucide-react";

type StageStatus = "pending" | "active" | "complete";

type Stage = {
  id: string;
  name: string;
  description: string;
};


const commonStages: Stage[] = [
  {
    id: "request",
    name: "Application",
    description: "Receive incoming request",
  },
  {
    id: "guard",
    name: "TokenGuard",
    description: "Estimate usage and check budget",
  },
  {
    id: "router",
    name: "SmartRouter",
    description: "Select an appropriate model",
  },
  {
    id: "cache",
    name: "Semantic cache",
    description: "Search for a reusable response",
  },
];

const cacheHitStages: Stage[] = [
  ...commonStages,
  {
    id: "cached",
    name: "Cached response",
    description: "Reuse the cached result; skip provider execution",
  },
  {
    id: "telemetry",
    name: "Cost telemetry",
    description: "Record the simulated cache-hit outcome",
  },
];

const cacheMissStages: Stage[] = [
  ...commonStages,
  {
    id: "provider",
    name: "AI provider",
    description: "Execute the request using the selected model",
  },
  {
    id: "telemetry",
    name: "Cost telemetry",
    description: "Record the simulated provider cost",
  },
];

const STEP_DELAY = 850;

export default function InfrastructureFlow() {
  const [prompt, setPrompt] = useState(
    "Summarize the benefits of semantic caching."
  );

  const [cacheHit, setCacheHit] = useState(false);
  const stages = cacheHit ? cacheHitStages : cacheMissStages;
  const [activeIndex, setActiveIndex] = useState(-1);
  const [finished, setFinished] = useState(false);

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null
  );

  const running = activeIndex >= 0 && !finished;

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  function startSimulation() {
    if (!prompt.trim() || running) return;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setFinished(false);
    setActiveIndex(0);

    let step = 0;

    const advance = () => {
      if (step < stages.length - 1) {
        step += 1;
        setActiveIndex(step);
        timeoutRef.current = setTimeout(advance, STEP_DELAY);
      } else {
        setFinished(true);
        timeoutRef.current = null;
      }
    };

    timeoutRef.current = setTimeout(advance, STEP_DELAY);
  }

  function resetSimulation() {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    setActiveIndex(-1);
    setFinished(false);
  }

  function getStatus(index: number): StageStatus {
    if (finished || (activeIndex >= 0 && index < activeIndex)) {
      return "complete";
    }

    if (index === activeIndex) {
      return "active";
    }

    return "pending";
  }

  return (
    <section className="infrastructure-flow">
      <div className="flow-header">
        <span className="section-label">
          INTERACTIVE INFRASTRUCTURE
        </span>

        <h3>Follow every request.</h3>

        <p>
          Explore how Frugal processes an AI request,
          from initial validation to cost telemetry.
        </p>
      </div>

      <div className="flow-controls">
        <label htmlFor="flow-prompt">
          SAMPLE REQUEST
        </label>

        <div className="flow-input-row">
          <input
            id="flow-prompt"
            value={prompt}
            onChange={(event) =>
              setPrompt(event.target.value)
            }
            disabled={running}
            placeholder="Enter a sample AI request"
          />

          <button
            type="button"
            onClick={startSimulation}
            disabled={running || !prompt.trim()}
            className="flow-run-button"
          >
            <Send size={15} />
            {running ? "Processing" : "Run simulation"}
          </button>
        </div>

        <div className="flow-options">
          <span>SIMULATED CACHE RESULT</span>

          <div className="flow-option-buttons">
            <button
              type="button"
              className={cacheHit ? "selected" : ""}
              onClick={() => {
                resetSimulation();
                setCacheHit(true);
              }}
              disabled={running}
              aria-pressed={cacheHit}
            >
              Cache hit
            </button>

            <button
              type="button"
              className={!cacheHit ? "selected" : ""}
              onClick={() => {
                resetSimulation();
                setCacheHit(false);
              }}
              disabled={running}
              aria-pressed={!cacheHit}
            >
              Cache miss
            </button>
          </div>
        </div>
      </div>

      <div
        className="flow-stages"
        aria-label="Simulated request processing stages"
      >
        {stages.map((stage, index) => {
          const status = getStatus(index);

          return (
            <div className="flow-stage-wrapper" key={stage.id}>
              <motion.div
                className={`flow-stage flow-stage-${status}`}
                animate={{
                  opacity: status === "pending" ? 0.55 : 1,
                  scale: status === "active" ? 1.025 : 1,
                }}
                transition={{ duration: 0.3 }}
              >
                <div className="flow-stage-icon">
                  {status === "complete" ? (
                    <Check size={19} />
                  ) : status === "active" ? (
                    <LoaderCircle
                      size={19}
                      className="flow-spinner"
                    />
                  ) : (
                    <Circle size={19} />
                  )}
                </div>

                <div className="flow-stage-content">
                  <span className="flow-stage-number">
                    {String(index + 1).padStart(2, "0")}
                  </span>

                  <h4>{stage.name}</h4>

                  <p>
                    {stage.description}
                  </p>
                </div>

                <span className="flow-stage-status">
                  {status === "complete"
                    ? "COMPLETE"
                    : status === "active"
                    ? "PROCESSING"
                    : "PENDING"}
                </span>
              </motion.div>

              {index < stages.length - 1 && (
                <div className="flow-connector">
                  <ArrowRight size={19} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        {finished && (
          <motion.div
            className="flow-result"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div>
              <span className="flow-result-label">
                SIMULATION COMPLETE
              </span>

              <h4>
                {cacheHit
                  ? "Response served from cache"
                  : "Request sent to an AI provider"}
              </h4>

              <p>
                {cacheHit
                  ? "A reusable response was found. The simulated provider call was skipped."
                  : "No reusable response was found. The simulated request proceeded to provider execution."}
              </p>
            </div>

            <button
              type="button"
              onClick={resetSimulation}
              className="flow-reset"
            >
              <RotateCcw size={15} />
              Reset
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <p className="flow-disclaimer">
        Demonstration only. This visualization does not
        submit requests to AI providers or modify live
        analytics.
      </p>
    </section>
  );
}