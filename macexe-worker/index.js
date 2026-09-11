export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });

    const json = (data, status = 200) =>
      new Response(JSON.stringify(data), { status, headers: { ...cors, "Content-Type": "application/json" } });

    // POST /waitlist — add email
    if (req.method === "POST" && url.pathname === "/waitlist") {
      const { email, product } = await req.json();
      if (!email?.includes("@")) return json({ error: "Invalid email" }, 400);

      const key = `email:${email.toLowerCase().trim()}`;
      const existing = await env.WAITLIST.get(key);
      if (existing) return json({ ok: true, already: true });

      await env.WAITLIST.put(key, JSON.stringify({ email, product: product || "macexe", joinedAt: Date.now() }));
      return json({ ok: true });
    }

    // GET /waitlist — list all (requires owner key)
    if (req.method === "GET" && url.pathname === "/waitlist") {
      if (req.headers.get("X-Owner-Key") !== env.OWNER_KEY) return json({ error: "Forbidden" }, 403);
      const list = await env.WAITLIST.list({ prefix: "email:" });
      const entries = await Promise.all(list.keys.map(k => env.WAITLIST.get(k.name, "json")));
      return json(entries);
    }

    // GET /waitlist/:email — check approval status (public)
    if (req.method === "GET" && url.pathname.startsWith("/waitlist/")) {
      const email = decodeURIComponent(url.pathname.split("/waitlist/")[1]);
      const entry = await env.WAITLIST.get(`email:${email.toLowerCase().trim()}`, "json");
      if (!entry) return json({ error: "Not found" }, 404);
      return json({ approved: entry.approved ?? false });
    }

    // PATCH /waitlist/:email — approve/revoke (owner only)
    if (req.method === "PATCH" && url.pathname.startsWith("/waitlist/")) {
      if (req.headers.get("X-Owner-Key") !== env.OWNER_KEY) return json({ error: "Forbidden" }, 403);
      const email = decodeURIComponent(url.pathname.split("/waitlist/")[1]);
      const key = `email:${email.toLowerCase().trim()}`;
      const entry = await env.WAITLIST.get(key, "json");
      if (!entry) return json({ error: "Not found" }, 404);
      const body = await req.json();
      await env.WAITLIST.put(key, JSON.stringify({ ...entry, ...body }));
      return json({ ok: true });
    }

    return json({ error: "Not found" }, 404);
  }
};
