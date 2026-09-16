# Agni-Netra Environment Setup

## Backend Environment

1. Copy `.env.example` to `.env` in the `backend/` directory or project root.
2. Ensure you have the dev credentials populated for local testing.

```env
AUTH_DEV_USERNAME=Dax
AUTH_DEV_PASSWORD=Dax@1707
SECRET_KEY=generate_a_secure_random_key_here
```

**CRITICAL:** These credentials (`Dax` / `Dax@1707`) are exclusively for LOCAL DEVELOPMENT. Do NOT use them in production or commit them to the repository. The `.env` file must be ignored by `.gitignore`.

## Frontend Environment

1. Create `.env.local` in the `frontend/` directory.
2. Add your API URL and Mapbox access token.

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
```

Without the `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN`, the Live Map will display a "Map provider is not configured" fallback instead of rendering tiles.
