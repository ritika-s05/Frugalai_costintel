import { useCallback, useEffect, useState } from "react";
import { motion } from "motion/react";
import {
  Activity,
  ArrowDownRight,
  Database,
  RefreshCw,
  Route,
  Wallet,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getAnalyticsSummary,
  type AnalyticsSummary,
} from "../services/api";

import "./AnalyticsDashboard.css";

const money = (value: number) => `$${value.toFixed(6)}`;

export default function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await getAnalyticsSummary();
      setData(result);
    } catch {
      setError("Unable to retrieve analytics from Frugal API.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const cards = data
    ? [
        {
          label: "Total requests",
          value: data.total_requests.toLocaleString(),
          icon: <Activity size={19} />,
          detail: "Recorded gateway requests",
        },
        {
          label: "Actual spending",
          value: money(data.total_actual_cost),
          icon: <Wallet size={19} />,
          detail: "Across all recorded requests",
        },
        {
          label: "Attributed savings",
          value: money(data.total_savings),
          icon: <ArrowDownRight size={19} />,
          detail: "Estimated against recorded baselines",
        },
        {
          label: "Provider latency",
          value: `${data.average_provider_latency_ms.toFixed(0)} ms`,
          icon: <Database size={19} />,
          detail: "Average for non-cached requests",
        },
      ]
    : [];

  const chartData = data
    ? [
        {
          name: "Baseline",
          cost: data.total_baseline_cost,
        },
        {
          name: "Actual",
          cost: data.total_actual_cost,
        },
      ]
    : [];

  return (
    <section className="intelligence-dashboard">
      <div className="dashboard-heading">
        <div>
          <span className="section-label">
            LIVE INFRASTRUCTURE INTELLIGENCE
          </span>
          <h2>Every request. Accounted for.</h2>
          <p>
            Understand how your infrastructure consumes,
            routes and optimizes AI resources.
          </p>
        </div>

        <button
          className="dashboard-refresh"
          onClick={() => void refresh()}
          disabled={loading}
        >
          <RefreshCw size={16} />
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="dashboard-error" role="alert">
          {error}
        </div>
      )}

      {!data && loading && (
        <p className="dashboard-loading">Loading live analytics...</p>
      )}

      {data && (
        <>
          <div className="dashboard-kpis">
            {cards.map((card, index) => (
              <motion.article
                className="dashboard-kpi"
                key={card.label}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{
                  duration: 0.5,
                  delay: index * 0.08,
                }}
              >
                <div className="kpi-top">
                  <span>{card.label}</span>
                  {card.icon}
                </div>
                <strong>{card.value}</strong>
                <small>{card.detail}</small>
              </motion.article>
            ))}
          </div>

          <div className="dashboard-detail-grid">
            <motion.article
              className="dashboard-panel"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.65 }}
            >
              <div className="panel-heading">
                <div>
                  <span className="panel-eyebrow">
                    COST INTELLIGENCE
                  </span>
                  <h3>Efficiency in perspective.</h3>
                </div>
                <span className="panel-tag">USD</span>
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    margin={{
                      top: 15,
                      right: 10,
                      left: 10,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid stroke="#E9E2D7" vertical={false} />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} />
                    <YAxis
                      tickFormatter={(value: number) => `$${value.toFixed(4)}`}
                      axisLine={false}
                      tickLine={false}
                      width={85}
                    />
                    <Tooltip
                      formatter={(value) => money(Number(value ?? 0))}
                      contentStyle={{
                        borderRadius: 12,
                        border: "1px solid #E3DCD0",
                        background: "#FFFEFB",
                      }}
                    />
                    <Bar
                      dataKey="cost"
                      fill="#877660"
                      radius={[7, 7, 0, 0]}
                      maxBarSize={90}
                      animationDuration={1100}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <p className="panel-note">
                Baseline represents requests with recorded comparison costs.
                Actual spending includes all recorded requests; these bars
                therefore cover different populations.
              </p>
            </motion.article>

            <motion.article
              className="dashboard-panel"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.65, delay: 0.12 }}
            >
              <div className="panel-heading">
                <div>
                  <span className="panel-eyebrow">
                    OPTIMIZATION
                  </span>
                  <h3>Intelligence at work.</h3>
                </div>
                <Route size={20} />
              </div>

              <div className="optimization-stat">
                <span>Cache hit rate</span>
                <strong>{data.cache_hit_rate.toFixed(1)}%</strong>
                <div className="progress-track">
                  <motion.div
                    className="progress-fill"
                    initial={{ width: 0 }}
                    whileInView={{ width: `${data.cache_hit_rate}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1 }}
                  />
                </div>
                <small>{data.cache_hits} cached requests</small>
              </div>

              <div className="optimization-stat">
                <span>Routing rate</span>
                <strong>{data.routing_rate.toFixed(1)}%</strong>
                <div className="progress-track">
                  <motion.div
                    className="progress-fill progress-olive"
                    initial={{ width: 0 }}
                    whileInView={{ width: `${data.routing_rate}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: 0.2 }}
                  />
                </div>
                <small>{data.routed_requests} routed requests</small>
              </div>

              <div className="savings-highlight">
                <span>Savings against recorded baselines</span>
                <strong>{data.savings_percentage.toFixed(2)}%</strong>
              </div>
            </motion.article>
          </div>

          <p className="dashboard-disclaimer">
            Development test data. Savings are estimates based on recorded
            model-pricing assumptions. Historical requests without baselines are
            excluded from the savings percentage.
          </p>
        </>
      )}
    </section>
  );
}
