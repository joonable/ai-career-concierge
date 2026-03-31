import React from "react";
import Link from "next/link";
import { InternalLinkItem } from "@/lib/internal_docs";

interface CoreDocsCardProps {
  title: string;
  items: InternalLinkItem[];
  kicker?: string;
}

export function CoreDocsCard({ title, items, kicker }: CoreDocsCardProps) {
  if (!items || items.length === 0) return null;

  return (
    <article className="dashboard-card promptops-card coredocs-card" style={{ padding: "20px" }}>
      <div className="dashboard-section__header" style={{ marginBottom: "16px" }}>
        <div>
          {kicker && <span className="dashboard-kicker">{kicker}</span>}
          <h2 className="dashboard-section__title" style={{ margin: 0, fontSize: "1.1rem" }}>{title}</h2>
        </div>
      </div>
      <ul className="promptops-list promptops-list--links" style={{ gap: "10px", paddingLeft: "0" }}>
        {items.map((item, index) => (
          <li key={index} style={{ listStyle: "none", margin: 0 }}>
            <Link 
              href={item.url} 
              rel="noreferrer" 
              target="_blank"
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "10px 14px",
                borderRadius: "12px",
                background: "rgba(255, 255, 255, 0.04)",
                border: "1px solid rgba(255, 255, 255, 0.04)",
                transition: "all 0.2s ease"
              }}
              className="coredocs-link"
            >
              <div style={{
                  display: "flex", alignItems: "center", justifyContent: "center", 
                  width: "28px", height: "28px", borderRadius: "6px", 
                  background: "rgba(147, 197, 253, 0.1)"
              }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#93c5fd" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
              </div>
              <span style={{ 
                color: "#dbeafe", 
                fontWeight: 500, 
                fontSize: "0.95rem",
                flex: 1,
                minWidth: 0,
                wordBreak: "break-word"
              }}>
                {item.label}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </article>
  );
}
