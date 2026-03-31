import React from "react";

export type WorkboardCardType = "current" | "done" | "next" | "backlog" | "milestone" | "note";

interface WorkboardCardProps {
  type: WorkboardCardType;
  title: string;
  items: string[];
  kicker?: string;
}

export function WorkboardCard({ type, title, items, kicker }: WorkboardCardProps) {
  const getCardStyle = (): React.CSSProperties => {
    switch (type) {
      case "current":
        return {
          background: "linear-gradient(180deg, rgba(14, 25, 46, 0.96) 0%, rgba(9, 15, 28, 0.9) 100%)",
          borderColor: "rgba(96, 165, 250, 0.28)",
        };
      case "done":
        return {
          background: "linear-gradient(180deg, rgba(10, 24, 20, 0.94) 0%, rgba(6, 16, 13, 0.86) 100%)",
          borderColor: "rgba(52, 211, 153, 0.18)",
        };
      case "next":
        return {
          background: "linear-gradient(180deg, rgba(28, 18, 9, 0.94) 0%, rgba(18, 12, 6, 0.86) 100%)",
          borderColor: "rgba(251, 146, 60, 0.18)",
        };
      default:
        return {
          background: "linear-gradient(180deg, rgba(10, 16, 30, 0.94) 0%, rgba(7, 11, 22, 0.86) 100%)",
        };
    }
  };

  const Icon = () => {
    switch (type) {
      case "current":
        return (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
        );
      case "done":
        return (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        );
      case "next":
        return (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fb923c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14"></path>
            <path d="m12 5 7 7-7 7"></path>
          </svg>
        );
      case "milestone":
        return (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m8 3 4 8 5-5 5 15H2L8 3z"></path>
          </svg>
        );
      case "backlog":
      case "note":
      default:
        return (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        );
    }
  };

  if (!items || items.length === 0) return null;

  return (
    <article className="dashboard-card promptops-card workboard-card" style={getCardStyle()}>
      <div className="dashboard-section__header" style={{ marginBottom: "16px" }}>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <div className="workboard-icon-wrapper" style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "36px", height: "36px", borderRadius: "10px", background: "rgba(255, 255, 255, 0.05)" }}>
            <Icon />
          </div>
          <div>
            {kicker && <span className="dashboard-kicker">{kicker}</span>}
            <h2 className="dashboard-section__title" style={{ margin: 0 }}>{title}</h2>
          </div>
        </div>
      </div>
      <ul className="promptops-list workboard-list" style={{ paddingLeft: "4px" }}>
        {items.map((item, index) => (
          <li key={index} className="workboard-list-item" style={{ display: "flex", gap: "10px", alignItems: "flex-start", marginBottom: "8px" }}>
            <span style={{ 
              color: type === "done" ? "#34d399" : "rgba(255,255,255,0.3)", 
              fontSize: "10px", 
              marginTop: "6px" 
            }}>
              ●
            </span>
            <span style={{ 
              color: type === "done" ? "rgba(215, 224, 238, 0.6)" : "rgba(234, 240, 248, 0.9)",
              textDecoration: type === "done" ? "line-through" : "none",
              lineHeight: "1.6",
              flex: 1,
              minWidth: 0,
              wordBreak: "break-word"
            }}>
              {item}
            </span>
          </li>
        ))}
      </ul>
    </article>
  );
}
