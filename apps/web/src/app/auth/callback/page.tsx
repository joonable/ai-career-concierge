export default function AuthCallbackPage() {
  return (
    <main>
      <div className="shell">
        <section className="panel" style={{ padding: 32 }}>
          <span className="eyebrow">Auth callback</span>
          <h1>OAuth hand-off</h1>
          <p className="lead">
            Wire this route to Supabase Google OAuth redirect handling. The scaffold keeps
            the route in place so the auth flow can be connected without reshaping the app.
          </p>
        </section>
      </div>
    </main>
  );
}
