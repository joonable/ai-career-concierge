import fs from "fs/promises";
import path from "path";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";
import { notFound } from "next/navigation";

export default async function InternalMarkdownViewer({ params }: { params: Promise<{ slug: string[] }> }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;
  if (!slug || slug.length === 0) {
    return notFound();
  }

  const filename = slug.join("/");
  
  // Resolve paths in possible doc locations
  const possiblePaths = [
    path.resolve(process.cwd(), "..", "..", "docs", "internal", filename),
    path.resolve(process.cwd(), "..", "..", "docs", filename),
    path.resolve(process.cwd(), "..", "..", filename),
  ];

  let rawContent = "";
  let resolvedLocation = "";
  
  for (const p of possiblePaths) {
    try {
      rawContent = await fs.readFile(p, "utf-8");
      resolvedLocation = p;
      break;
    } catch (e) {
      continue;
    }
  }

  if (!rawContent) {
    return (
      <main className="dashboard-page promptops-page" style={{ padding: "40px" }}>
        <div className="dashboard-shell promptops-shell">
          <Link href="/internal" style={{ color: "#60a5fa", marginBottom: "20px", display: "inline-block" }}>
            ← Back to Operations Panel
          </Link>
          <div className="dashboard-card" style={{ padding: "40px", textAlign: "center" }}>
            <h1>Document Not Found</h1>
            <p>Could not find <code>{filename}</code> in the repository docs.</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="dashboard-page promptops-page" style={{ minHeight: "100vh", backgroundColor: "#020610", paddingBottom: "100px" }}>
      <div className="dashboard-shell promptops-shell" style={{ maxWidth: "800px", margin: "0 auto", padding: "40px 20px" }}>
        <Link 
          href="/internal" 
          style={{ 
            color: "#94a3b8", 
            marginBottom: "30px", 
            display: "inline-flex", 
            alignItems: "center",
            gap: "8px",
            textDecoration: "none",
            fontSize: "0.95rem"
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
          Back to Internal Dashboard
        </Link>
        <article 
          className="dashboard-card promptops-card markdown-viewer" 
          style={{ 
            padding: "40px", 
            lineHeight: "1.7",
            color: "#d1d5db",
            fontSize: "1.05rem",
            wordBreak: "break-word"
          }}
        >
          <div style={{ paddingBottom: "24px", marginBottom: "24px", borderBottom: "1px solid rgba(255,255,255,0.1)", color: "#60a5fa", fontSize: "0.85rem" }}>
            Viewing: {filename}
          </div>
          <style dangerouslySetInnerHTML={{ __html: `
            .markdown-viewer h1 { font-size: 2rem; color: #f3f4f6; margin-top: 2rem; margin-bottom: 1rem; }
            .markdown-viewer h2 { font-size: 1.5rem; color: #e5e7eb; margin-top: 1.8rem; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 6px; }
            .markdown-viewer h3 { font-size: 1.25rem; color: #e5e7eb; margin-top: 1.5rem; margin-bottom: 0.8rem; }
            .markdown-viewer p { margin-bottom: 1rem; }
            .markdown-viewer ul { list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1rem; }
            .markdown-viewer ol { list-style-type: decimal; padding-left: 1.5rem; margin-bottom: 1rem; }
            .markdown-viewer li { margin-bottom: 0.25rem; }
            .markdown-viewer code { background: rgba(96, 165, 250, 0.15); color: #93c5fd; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }
            .markdown-viewer pre { background: #0b1120; padding: 16px; border-radius: 8px; overflow-x: auto; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.05); }
            .markdown-viewer pre code { background: transparent; color: inherit; padding: 0; }
            .markdown-viewer a { color: #60a5fa; text-decoration: underline; text-underline-offset: 4px; }
            .markdown-viewer blockquote { border-left: 4px solid #3b82f6; padding-left: 1rem; color: #9ca3af; margin: 1.5rem 0; background: rgba(59, 130, 246, 0.05); padding: 1rem; border-radius: 0 8px 8px 0; }
          `}} />
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {rawContent}
          </ReactMarkdown>
        </article>
      </div>
    </main>
  );
}
