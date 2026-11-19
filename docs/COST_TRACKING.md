# Cost Tracking & Infrastructure Resource Log — TripSync AI

**Project Policy:** Strict ₹0.00 (Zero Cost) Constraint  
**Auditor:** Principal DevOps & Infrastructure Engineer  
**Last Updated:** Day 1 Architecture Review  

---

## 1. Zero-Cost Infrastructure Matrix

| Service Provider | Role in Architecture | Free-Tier Quota & Limits | Operational Strategy for Limits | Potential Suspension Trigger | Fallback Alternative | Cost to Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Render** | FastAPI Backend Web Service | 512 MB RAM, 0.1 vCPU, 750 free instance hours/month. Spindown after 15 min idle. | Lightweight Docker image (<300 MB); memory optimization to keep RSS <350 MB; client-side warm-up loading screen. | Exceeding 512 MB RAM triggers instant Linux OOM kill. | Koyeb Free Tier / Hugging Face Spaces | **₹0.00** |
| **Cloudflare Pages** | React 18 SPA Hosting & Edge CDN | Unlimited requests, unlimited bandwidth, 500 builds/month, custom domain support. | Static Vite production build (`dist/`) deployed via Git integration or direct upload. | Exceeding build concurrency limits. | Vercel Free / Netlify Free | **₹0.00** |
| **Supabase** | Managed PostgreSQL 15 Database | 500 MB database storage, 2 active projects, direct & pooled connection strings. | Strict index optimization; periodic cleaning of orphan test data. | Projects pause after 7 days of inactivity. | Neon.tech Serverless Postgres | **₹0.00** |
| **GitHub** | Version Control & CI/CD Actions | Unlimited public repository storage; 2,000 Action build minutes/month. | Optimized CI workflow using cache actions for `pip` wheels and `npm` modules. | Exceeding 2,000 monthly action minutes. | Local pre-commit hook runs | **₹0.00** |
| **OpenStreetMap** | Interactive Map Tiles (GIS) | Free tile service under Open Database License (ODbL). | Client-side tile caching; valid descriptive HTTP `User-Agent` headers in Leaflet. | Excessive automated bulk scraping of raw tile servers. | CARTO free basemaps | **₹0.00** |

---

## 2. Cumulative Expenditure Ledger

| Entry Date | Service | Description | Currency | Amount Charged | Invoice / Reference |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **2026-11-20** | All Infrastructure | Architecture initialization & local toolchain | INR (₹) | **₹0.00** | Free Tier Baseline |

**Total Project Expenditure to Date: ₹0.00 ($0.00 USD)**

---

## 3. Rules of Engagement for Zero-Cost Enforcement
1. **Never enter credit card details for trial upgrades** that auto-convert to paid tiers.
2. **Never deploy unverified external APIs** with usage-metered billing models.
3. Every external service integration must be preceded by a formal entry in this document validating that free allowances can support our expected workload.
