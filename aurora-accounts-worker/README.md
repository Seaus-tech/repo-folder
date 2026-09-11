# 🌌 Aurora Accounts Worker

<p align="center>
  <strong>Cloudflare Worker API for user account management in Aurora-Shell.</strong>
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

This Cloudflare Worker provides a RESTful API for managing Aurora-Shell user accounts. It handles authentication, profile management, and owner-level administrative operations with KV storage.

## Features

- 👤 **Account Management** - Create, read, update, and delete user accounts
- 🔐 **Authentication** - SHA-256 hashed password verification
- 🛡️ **Owner Privileges** - Protected admin endpoints for sensitive operations
- 🌐 **CORS Support** - Cross-origin requests enabled for web clients
- ⚡ **Serverless** - No server management required with Cloudflare Workers

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/accounts` | Create a new account | ❌ |
| `POST` | `/accounts/login` | Authenticate and get profile | ❌ |
| `POST` | `/accounts/set-owner` | Bootstrap owner privileges | ✅ Owner only |
| `PATCH` | `/accounts/:username` | Update account profile | ✅ |
| `GET` | `/accounts` | List all users | ✅ Owner only |
| `DELETE` | `/accounts/:username` | Delete user account | ✅ Owner only |

## CORS Headers

All endpoints support CORS with the following headers:

- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET,POST,PATCH,DELETE,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type,X-Owner-Key,X-Username,X-Password-Hash`

## Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [Wrangler](https://developers.cloudflare.com/workers/wrangler/)
- Cloudflare account

## Development

```bash
# Install dependencies
npm install

# Start local development server
npx wrangler dev
```

## Deployment

```bash
# Deploy to Cloudflare
npx wrangler deploy
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OWNER_KEY` | Secret key for owner operations | ✅ |
| `KV_NAMESPACE` | KV binding for account storage | ✅ |

## Repository Structure

```
aurora-accounts-worker/
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