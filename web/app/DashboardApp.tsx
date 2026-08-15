"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type MetricSet = {
  revenue: number;
  gross_profit: number;
  gross_margin: number;
  receipts: number;
  units_sold: number;
  average_receipt: number;
};

type DailyPoint = MetricSet & { date: string };
type ProductPoint = {
  id: string;
  name: string;
  category: string;
  units_sold: number;
  revenue: number;
  gross_profit: number;
  gross_margin: number;
};

type Dashboard = {
  cafe: { id: string; name: string; currency: string; timezone: string };
  period: { from: string; to: string };
  metrics: MetricSet;
  changes: Record<"revenue" | "gross_profit" | "average_receipt" | "receipts", number>;
  daily: DailyPoint[];
  top_products: ProductPoint[];
  focus: { title: string; body: string };
};

const demoDashboard: Dashboard = {
  cafe: { id: "ugol", name: "Угол × Лесная, 14", currency: "RUB", timezone: "Europe/Moscow" },
  period: { from: "2026-08-01", to: "2026-08-14" },
  metrics: { revenue: 2480000, gross_profit: 1310000, gross_margin: 52.82, receipts: 3864, units_sold: 5442, average_receipt: 642 },
  changes: { revenue: 12.4, gross_profit: 8.7, average_receipt: 4.1, receipts: 7.9 },
  daily: [54, 64, 48, 76, 68, 82, 57, 72, 89, 78, 94, 73, 86, 100].map((value, index) => ({
    date: `2026-08-${String(index + 1).padStart(2, "0")}`,
    revenue: value * 2050,
    gross_profit: value * 1070,
    gross_margin: 52,
    receipts: value * 3,
    units_sold: value * 4,
    average_receipt: 640,
  })),
  top_products: [
    { id: "cappuccino", name: "Капучино", category: "Кофе с молоком", units_sold: 842, revenue: 261020, gross_profit: 183556, gross_margin: 70.3 },
    { id: "flat-white", name: "Флэт уайт", category: "Кофе с молоком", units_sold: 690, revenue: 241500, gross_profit: 161460, gross_margin: 66.9 },
    { id: "syrniki", name: "Сырники", category: "Завтраки", units_sold: 438, revenue: 210240, gross_profit: 120450, gross_margin: 57.3 },
    { id: "latte", name: "Латте", category: "Кофе с молоком", units_sold: 584, revenue: 198560, gross_profit: 135488, gross_margin: 68.2 },
  ],
  focus: {
    title: "Утреннее окно может приносить больше",
    body: "С 08:00 до 10:00 трафик вырос на 21%, но средний чек снизился. Комбо с выпечкой может увеличить выручку.",
  },
};

const apiUrl = process.env.NEXT_PUBLIC_CUPIT_API_URL ?? "http://localhost:5050/api/v1";

const money = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

const compactMoney = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  notation: "compact",
  maximumFractionDigits: 2,
});

function formatDateRange(period: Dashboard["period"]) {
  const from = new Date(`${period.from}T00:00:00`);
  const to = new Date(`${period.to}T00:00:00`);
  const fromText = from.toLocaleDateString("ru-RU", { day: "2-digit" });
  const toText = to.toLocaleDateString("ru-RU", { day: "2-digit", month: "long" });
  return `${fromText}–${toText}`;
}

export function DashboardApp() {
  const [dashboard, setDashboard] = useState<Dashboard>(demoDashboard);
  const [source, setSource] = useState<"loading" | "api" | "demo">("loading");
  const [periodDays, setPeriodDays] = useState(14);
  const [advisorOpen, setAdvisorOpen] = useState(false);
  const [question, setQuestion] = useState("Какие три действия сильнее всего повысят прибыль?");
  const [answer, setAnswer] = useState("");
  const [aiState, setAiState] = useState<"idle" | "loading" | "error">("idle");

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch(`${apiUrl}/dashboard`, { signal: controller.signal });
        if (!response.ok) throw new Error("API unavailable");
        setDashboard(await response.json() as Dashboard);
        setSource("api");
      } catch (error) {
        if ((error as Error).name !== "AbortError") setSource("demo");
      }
    }
    load();
    return () => controller.abort();
  }, []);

  const maxRevenue = useMemo(
    () => Math.max(...dashboard.daily.map((point) => point.revenue), 1),
    [dashboard.daily],
  );

  async function changePeriod(days: number) {
    setPeriodDays(days);
    if (source !== "api") return;
    const end = new Date(`${dashboard.period.to}T00:00:00Z`);
    const start = new Date(end);
    start.setUTCDate(end.getUTCDate() - days + 1);
    const query = new URLSearchParams({
      from: start.toISOString().slice(0, 10),
      to: dashboard.period.to,
    });
    try {
      const response = await fetch(`${apiUrl}/dashboard?${query}`);
      if (!response.ok) throw new Error("Period request failed");
      setDashboard(await response.json() as Dashboard);
    } catch {
      setSource("demo");
    }
  }

  async function askAi(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setAiState("loading");
    setAnswer("");
    try {
      const response = await fetch(`${apiUrl}/ai/insights`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, from: dashboard.period.from, to: dashboard.period.to }),
      });
      const payload = await response.json() as { answer?: string; error?: { message?: string } };
      if (!response.ok || !payload.answer) throw new Error(payload.error?.message ?? "AI unavailable");
      setAnswer(payload.answer);
      setAiState("idle");
    } catch {
      setAnswer("Локальная AI-модель сейчас недоступна. Обычная аналитика продолжает работать — запустите Ollama и повторите запрос.");
      setAiState("error");
    }
  }

  const kpis = [
    { key: "revenue" as const, label: "Выручка", value: compactMoney.format(dashboard.metrics.revenue), tone: "lime" },
    { key: "gross_profit" as const, label: "Валовая прибыль", value: compactMoney.format(dashboard.metrics.gross_profit), tone: "paper" },
    { key: "average_receipt" as const, label: "Средний чек", value: money.format(dashboard.metrics.average_receipt), tone: "paper" },
    { key: "receipts" as const, label: "Чеки", value: dashboard.metrics.receipts.toLocaleString("ru-RU"), tone: "paper" },
  ];

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand-row">
          <div className="brand-mark">C</div>
          <div><div className="brand">CupIT</div><div className="brand-note">LOCAL INTELLIGENCE</div></div>
        </div>
        <button className="location-card" type="button">
          <span className="location-icon">У</span>
          <span><strong>{dashboard.cafe.name}</strong><small>Основная кофейня</small></span>
          <span className="chevron">⌄</span>
        </button>
        <nav aria-label="Основная навигация">
          <a className="nav-item active" href="#overview"><span>01</span>Обзор</a>
          <a className="nav-item" href="#sales"><span>02</span>Продажи</a>
          <a className="nav-item" href="#products"><span>03</span>Меню</a>
          <button className="nav-item nav-button" onClick={() => setAdvisorOpen(true)} type="button"><span>04</span>AI-советник</button>
          <a className="nav-item" href="#reports"><span>05</span>Отчёты</a>
          <a className="nav-item" href="#imports"><span>06</span>Импорт данных</a>
        </nav>
        <div className="local-status">
          <span className={`status-dot ${source}`} />
          <div>
            <strong>{source === "api" ? "Локальный API подключён" : source === "loading" ? "Подключаем данные" : "Демонстрационный режим"}</strong>
            <small>{source === "api" ? "Данные остаются на устройстве" : "Запустите API для живых данных"}</small>
          </div>
        </div>
      </aside>

      <section className="workspace" id="overview">
        <header className="topbar">
          <div><p className="eyebrow">СУББОТА, 15 АВГУСТА</p><h1>Добрый день, Михаил</h1></div>
          <div className="top-actions">
            <div className="period-switch" aria-label="Период отчёта">
              {[7, 14, 30].map((days) => (
                <button className={periodDays === days ? "selected" : ""} onClick={() => changePeriod(days)} type="button" key={days}>{days}д</button>
              ))}
            </div>
            <button className="avatar" type="button" aria-label="Профиль Михаила">М</button>
          </div>
        </header>

        <div className="signal-strip">
          <span>{formatDateRange(dashboard.period)}</span>
          <strong>Маржа {dashboard.metrics.gross_margin.toFixed(1)}%</strong><i />
          <strong>{dashboard.metrics.units_sold.toLocaleString("ru-RU")} позиций</strong><i />
          <strong>{source === "api" ? "Рассчитано из JSON" : "Предпросмотр интерфейса"}</strong>
        </div>

        <section className="kpi-grid" aria-label="Основные показатели">
          {kpis.map((item) => (
            <article className={`kpi-card ${item.tone}`} key={item.key}>
              <div className="kpi-top"><span>{item.label}</span><em>{dashboard.changes[item.key] >= 0 ? "+" : ""}{dashboard.changes[item.key].toFixed(1)}%</em></div>
              <strong>{item.value}</strong><small>к прошлому периоду</small>
            </article>
          ))}
        </section>

        <section className="dashboard-grid">
          <article className="panel revenue-panel" id="sales">
            <div className="panel-heading">
              <div><p className="eyebrow">ДИНАМИКА</p><h2>Выручка по дням</h2></div>
              <span className="data-label">{dashboard.daily.length} дней</span>
            </div>
            <div className="chart-summary"><strong>{money.format(dashboard.daily.at(-1)?.revenue ?? 0)}</strong><span>последний день периода</span></div>
            <div className="bar-chart" aria-label="График выручки по дням">
              {dashboard.daily.map((point, index) => (
                <div className="bar-wrap" key={point.date} title={`${point.date}: ${money.format(point.revenue)}`}>
                  <div className={index === dashboard.daily.length - 1 ? "bar current" : "bar"} style={{ height: `${Math.max(5, point.revenue / maxRevenue * 100)}%` }} />
                </div>
              ))}
            </div>
            <div className="chart-axis"><span>{dashboard.period.from.slice(5)}</span><span>выручка / день</span><span>{dashboard.period.to.slice(5)}</span></div>
          </article>

          <article className="panel advisor-panel" id="advisor">
            <div className="advisor-orbit"><span>✦</span></div>
            <p className="eyebrow">CUPIT AI · ФОКУС ПЕРИОДА</p>
            <h2>{dashboard.focus.title}</h2>
            <p className="advisor-copy">{dashboard.focus.body}</p>
            <button className="primary-button" onClick={() => setAdvisorOpen(true)} type="button">Обсудить с AI <span>→</span></button>
            <small>AI получает только агрегаты, без исходных чеков</small>
          </article>
        </section>

        <section className="panel products-panel" id="products">
          <div className="panel-heading">
            <div><p className="eyebrow">МЕНЮ</p><h2>Лидеры по выручке</h2></div>
            <span className="data-label">{formatDateRange(dashboard.period)}</span>
          </div>
          <div className="product-table" role="table" aria-label="Лидеры меню">
            <div className="product-row table-head" role="row"><span>Товар</span><span>Продано</span><span>Выручка</span><span>Маржа</span></div>
            {dashboard.top_products.map((product, index) => (
              <div className="product-row" role="row" key={product.id}>
                <span className="product-name"><i>{String(index + 1).padStart(2, "0")}</i><b>{product.name}</b><small>{product.category}</small></span>
                <span>{product.units_sold.toLocaleString("ru-RU")} шт.</span>
                <span>{money.format(product.revenue)}</span>
                <span><em>{product.gross_margin.toFixed(1)}%</em></span>
              </div>
            ))}
          </div>
        </section>
      </section>

      {advisorOpen && (
        <div className="drawer-backdrop" onMouseDown={() => setAdvisorOpen(false)}>
          <aside className="advisor-drawer" aria-label="AI-советник" onMouseDown={(event) => event.stopPropagation()}>
            <div className="drawer-heading"><div><p className="eyebrow">ЛОКАЛЬНАЯ МОДЕЛЬ</p><h2>CupIT AI-советник</h2></div><button onClick={() => setAdvisorOpen(false)} type="button" aria-label="Закрыть">×</button></div>
            <div className="context-chip"><span>✦</span><div><strong>Контекст готов</strong><small>{formatDateRange(dashboard.period)} · {dashboard.top_products.length} лидеров меню</small></div></div>
            <form onSubmit={askAi}>
              <label htmlFor="ai-question">Что вы хотите узнать?</label>
              <textarea id="ai-question" maxLength={1000} onChange={(event) => setQuestion(event.target.value)} value={question} />
              <button className="primary-button dark" disabled={aiState === "loading"} type="submit">
                {aiState === "loading" ? "Анализируем…" : "Получить рекомендации"}<span>→</span>
              </button>
            </form>
            {answer && <div className={`ai-answer ${aiState === "error" ? "error" : ""}`}><p className="eyebrow">ОТВЕТ</p><p>{answer}</p></div>}
            <p className="privacy-note">CupIT передаёт модели только структурированные показатели этого периода. Исходные файлы и чеки остаются недоступны AI.</p>
          </aside>
        </div>
      )}
    </main>
  );
}
