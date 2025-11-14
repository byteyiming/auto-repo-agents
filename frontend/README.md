# OmniDoc Frontend

Next.js 15 frontend for OmniDoc 2.0 - AI-powered documentation generation system.

## Getting Started

### Install Dependencies

```bash
pnpm install
```

### Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Development

```bash
pnpm dev
```

The frontend will be available at `http://localhost:3000`.

### Build

```bash
pnpm build
pnpm start
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx                    # Home page with project creation form
│   ├── project/
│   │   └── [id]/
│   │       ├── page.tsx            # Project status page with WebSocket
│   │       └── results/
│   │           └── page.tsx        # Document viewer workspace
│   ├── layout.tsx                  # Root layout
│   └── globals.css                 # Global styles
├── components/
│   ├── DocumentSelector.tsx        # Document selection component
│   ├── ProgressTimeline.tsx        # Real-time progress display
│   └── DocumentViewer.tsx          # Two-column document viewer
└── lib/
    ├── api.ts                      # API client utilities
    └── useProjectStatus.ts         # SWR hook for status polling
```

## Features

- ✅ Document template selection with category grouping
- ✅ Real-time progress updates via WebSocket
- ✅ Fallback polling when WebSocket unavailable
- ✅ Markdown document rendering with syntax highlighting
- ✅ Document download and copy functionality
- ✅ LocalStorage persistence for document selections
- ✅ Responsive design with Tailwind CSS

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000` (configurable via `NEXT_PUBLIC_API_BASE`).

### Endpoints Used

- `GET /api/document-templates` - Fetch available document templates
- `POST /api/projects` - Create a new project
- `GET /api/projects/{id}/status` - Get project status
- `GET /api/projects/{id}/documents` - List generated documents
- `GET /api/projects/{id}/documents/{doc_id}` - Get document content
- `GET /api/projects/{id}/documents/{doc_id}/download` - Download document
- `WebSocket /ws/{project_id}` - Real-time progress updates

## Development Notes

- Uses Next.js 15 App Router
- TypeScript for type safety
- Tailwind CSS for styling
- SWR for data fetching and polling
- WebSocket for real-time updates with automatic reconnection
- React Markdown for document rendering
