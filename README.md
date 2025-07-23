# Vista 2025 Hackathon - Competitive Insights

Company: Gainsight

Team:

- @graemerycyk (lead)
- @ferndot
- @itaim
- @Tianaye02

Problem statement:

> In highly competitive markets, detecting subtle “signals” in public communications; such as product-launch hints in press releases, executive interviews, or social-media chatter can yield critical strategic insight. We plan to build an AI agent that autonomously scours open-web sources via deep research to assemble concise, up-to-date profiles of key competitors (covering their products, roadmap clues, hiring trends, partnerships, and financial posture), and continuously monitors new public communications to flag deviations or emerging patterns that might indicate shifts in strategy, impending launches, or other actionable events. Solutions should emphasise automated discovery, real-time updates, and explainable alerts so that business analysts can quickly understand both what was spotted and why it matters.

## Quick Start

**System Requirements:**

- Docker & Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

**Run the Project:**

1. Create a new .env file following the structure of .env.example
2. Run the local servers using docker compose

```bash
docker-compose up
```

**Links:**

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs: http://localhost:8000/docs

## Deployment

This project is configured for automatic deployment to Heroku (backend) and Vercel (frontend).
