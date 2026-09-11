# 🍷 MACEXE Worker API

<p align="center>
  <strong>Cloudflare Worker API for MACEXE waitlist management and feature requests.</strong>
</p>

<p align="center>
  <img src="https://img.shields.io/badge/Platform-Cloudflare%20Workers-orange?style=flat-square&logo=cloudflare" alt="Cloudflare" />
  <img src="https://img.shields.io/badge/Language-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
</p>

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [CORS Headers](#cors-headers)
- [Prerequisites](#prerequisites)
- [Development](#development)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

This Cloudflare Worker handles waitlist management for MACEXE, the macOS Windows executable runner. It provides endpoints for users to join the waitlist and for admins to manage approvals.

## Features

- 📋 **Waitlist Management** - Add, view, and manage waitlist entries
- 👤 **Approval System** - Admin endpoints for user approval/rejection
- 🔐 **Secure Authentication** - Header-based owner verification
- 🌐 **CORS Support** - Cross-origin requests enabled for web clients

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/waitlist` | Add email to waitlist | ❌ |
| `GET` | `/waitlist` | List all waitlist entries | ✅ Owner only |
| `GET` | `/waitlist/:email` | Check approval status | ❌ |
| `PATCH` | `/waitlist/:email` | Approve/revoke access | ✅ Owner only |

## CORS Headers

All endpoints support CORS with the following headers:

- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET,POST,PATCH,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

## Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [Wrangler](https://developers.cloudflare.com/workers/wrangler/)
- Cloudflare account

## Development

### Install Dependencies

```bash
# Install Wrangler globally
npm install -g wrangler

# Install project dependencies
npm install
```

### Local Development

```bash
# Start local development server
npx wrangler dev
```

The worker will be available at `http://localhost:8787`.

## Deployment

```bash
# Deploy to Cloudflare
npx wrangler deploy
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OWNER_KEY` | Secret key for admin operations | ✅ |
| `KV_NAMESPACE` | KV binding for waitlist storage | ✅ |

## Repository Structure

```
macexe-worker/
├── index.js               # Main worker code
├── package.json           # Node dependencies
├── wrangler.toml          # Wrangler configuration
├── .wrangler/             # Wrangler cache
└── README.md              # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

© 2026 Seaus Tech. All rights reserved.