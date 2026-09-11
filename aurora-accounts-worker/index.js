export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname;
    const method = req.method;

    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type,X-Owner-Key,X-Username,X-Password-Hash",
    };
    if (method === "OPTIONS") return new Response(null, { headers: cors });

    const json = (data, status = 200) =>
      new Response(JSON.stringify(data), { status, headers: { ...cors, "Content-Type": "application/json" } });

    // Helper: get authenticated account from headers
    const getAuthedAccount = async () => {
      const username = req.headers.get("X-Username");
      const hash = req.headers.get("X-Password-Hash");
      if (!username || !hash) return null;
      const raw = await env.ACCOUNTS.get(username);
      if (!raw) return null;
      const profile = JSON.parse(raw);
      if (profile.password_hash !== hash) return null;
      return profile;
    };

    // POST /accounts — create
    if (method === "POST" && path === "/accounts") {
      const { username, password_hash, installed, plugins, header, header_mode } = await req.json();
      if (!username || !password_hash) return json({ error: "Missing fields" }, 400);
      const existing = await env.ACCOUNTS.get(username);
      if (existing) return json({ error: "Username taken" }, 409);
      const profile = { username, password_hash, installed: installed || "", plugins: plugins || [], linked: {}, header: header || "Aurora-Shell", header_mode: header_mode || "BLOCK", is_owner: false };
      await env.ACCOUNTS.put(username, JSON.stringify(profile));
      return json({ ok: true });
    }

    // POST /accounts/login — verify, return profile (strip hash)
    if (method === "POST" && path === "/accounts/login") {
      const { username, password_hash } = await req.json();
      const raw = await env.ACCOUNTS.get(username);
      if (!raw) return json({ error: "Not found" }, 404);
      const profile = JSON.parse(raw);
      if (profile.password_hash !== password_hash) return json({ error: "Wrong password" }, 401);
      const { password_hash: _, ...safe } = profile;
      return json(safe);
    }

    // POST /accounts/set-owner — bootstrap: set is_owner on an account (requires X-Owner-Key, one-time use)
    if (method === "POST" && path === "/accounts/set-owner") {
      if (req.headers.get("X-Owner-Key") !== env.OWNER_KEY) return json({ error: "Forbidden" }, 403);
      const { username } = await req.json();
      const raw = await env.ACCOUNTS.get(username);
      if (!raw) return json({ error: "Not found" }, 404);
      const profile = JSON.parse(raw);
      profile.is_owner = true;
      await env.ACCOUNTS.put(username, JSON.stringify(profile));
      return json({ ok: true });
    }

    // PATCH /accounts/:user — update own profile (auth via headers) or owner
    if (method === "PATCH" && path.startsWith("/accounts/")) {
      const username = path.split("/")[2];
      const raw = await env.ACCOUNTS.get(username);
      if (!raw) return json({ error: "Not found" }, 404);
      const profile = JSON.parse(raw);
      const body = await req.json();
      const authed = await getAuthedAccount();

      const isOwner = authed?.is_owner === true;
      const isSelf = authed?.username === username;

      if (!isOwner && !isSelf) return json({ error: "Forbidden" }, 403);

      // Nobody can change password_hash or is_owner via this endpoint
      delete body.password_hash;
      delete body.is_owner;

      const updated = { ...profile, ...body };
      await env.ACCOUNTS.put(username, JSON.stringify(updated));
      return json({ ok: true });
    }

    // GET /accounts — list all users (owner only)
    if (method === "GET" && path === "/accounts") {
      const authed = await getAuthedAccount();
      if (!authed?.is_owner) return json({ error: "Forbidden" }, 403);
      const list = await env.ACCOUNTS.list();
      const users = await Promise.all(list.keys.map(async k => {
        const raw = await env.ACCOUNTS.get(k.name);
        const { password_hash, linked, ...safe } = JSON.parse(raw);
        return safe;
      }));
      return json(users);
    }

    // DELETE /accounts/:user — owner only
    if (method === "DELETE" && path.startsWith("/accounts/")) {
      const authed = await getAuthedAccount();
      if (!authed?.is_owner) return json({ error: "Forbidden" }, 403);
      const username = path.split("/")[2];
      await env.ACCOUNTS.delete(username);
      return json({ ok: true });
    }

    return json({ error: "Not found" }, 404);
  }
};
