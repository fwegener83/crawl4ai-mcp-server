## FEATURE:

- React-basiertes Frontend für crawl4ai-mcp-server
- Web Crawling Interface mit konfigurierbaren Optionen (einfach und deep crawling)
- Markdown Viewer/Editor für Crawl-Ergebnisse mit Live-Vorschau
- Collection Management System mit CRUD-Operationen
- Suchfunktionalität für gespeicherte Collections
- Monorepo Setup mit Frontend und Backend

## USER FLOWS:

### Flow 1: Simple Website Crawling
1. User gibt URL in Crawl-Form ein
2. Wählt "Simple Crawl" Option
3. System ruft `web_content_extract` auf
4. Markdown wird im Editor/Preview angezeigt
5. User kann Inhalt bearbeiten
6. User speichert in Collection über Save Dialog

### Flow 2: Deep Website Crawling
1. User gibt Domain URL ein
2. Konfiguriert Deep Crawl Optionen (depth, strategy, patterns)
3. System ruft `domain_deep_crawl_tool` auf
4. Ergebnisse werden als Liste angezeigt
5. User wählt spezifische Seiten zur Bearbeitung
6. Markdown Editor für gewählte Inhalte
7. Speichern in Collection

### Flow 3: Collection Management
1. User navigiert zu Collections Page
2. `list_collections` zeigt alle verfügbaren Collections
3. User kann Collections durchsuchen mit Suchfunktion
4. Search nutzt `search_knowledge_base` für Inhaltssuche
5. User kann Collections löschen mit `delete_collection`

## TECHNICAL STACK:

- **Frontend**: React 18+ mit TypeScript
- **Styling**: Tailwind CSS für responsive Design
- **Editor**: Monaco Editor für Markdown-Bearbeitung
- **Markdown Rendering**: react-markdown mit Syntax-Highlighting
- **State Management**: Zustand oder React Context
- **HTTP Client**: Axios für API Communication
- **UI Components**: Headless UI oder Radix UI

## REPOSITORY STRUCTURE:

```
crawl4ai-mcp-server/
├── backend/                    # Bestehender MCP Server Code + API Layer
│   ├── src/
│   ├── api/                    # HTTP API Wrapper für MCP Tools
│   ├── requirements.txt
│   └── ...
├── frontend/                   # Neues React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   ├── vite.config.ts
│   └── ...
├── README.md                   # Gesamtprojekt Setup
└── docker-compose.yml          # Lokale Entwicklung
```

## COMPONENT STRUCTURE:

```
src/
├── components/
│   ├── Crawler/
│   │   ├── CrawlForm.tsx           # URL input & configuration
│   │   ├── CrawlResults.tsx        # Display crawl results
│   │   └── LinkPreview.tsx         # Quick link overview
│   ├── Editor/
│   │   ├── MarkdownEditor.tsx      # Monaco-based editor
│   │   ├── MarkdownPreview.tsx     # Rendered markdown
│   │   └── SplitView.tsx           # Editor + Preview layout
│   ├── Collections/
│   │   ├── CollectionList.tsx      # List all collections
│   │   ├── CollectionSearch.tsx    # Search interface
│   │   └── SaveDialog.tsx          # Save to collection modal
│   └── Layout/
│       ├── Header.tsx              # App header with navigation
│       └── Layout.tsx              # Main layout wrapper
├── pages/
│   ├── CrawlPage.tsx               # Main crawling interface
│   ├── CollectionsPage.tsx         # Collection management
│   └── SearchPage.tsx              # Search interface
├── services/
│   └── api.ts                      # API wrapper functions
└── types/
    └── index.ts                    # TypeScript type definitions
```

## API INTEGRATION:

```typescript
// API Service Interface
interface APIService {
  extractWebContent(url: string): Promise<string>
  deepCrawlDomain(config: DeepCrawlConfig): Promise<CrawlResult[]>
  previewDomainLinks(url: string, includeExternal?: boolean): Promise<LinkPreview>
  storeInCollection(content: string, collectionName: string): Promise<void>
  searchCollections(query: string, collection?: string): Promise<SearchResult[]>
  listCollections(): Promise<Collection[]>
  deleteCollection(name: string): Promise<void>
}
```

## TESTING:

- **End-to-End Tests**: Playwright für User Flow Testing
- **Test Coverage**: Alle drei User Flows als E2E Tests implementiert
- **Local Testing**: Tests lokal ausführbar vor Commits
- **Test Structure**: 
  ```
  tests/
  ├── e2e/
  │   ├── crawling.spec.ts        # Flow 1: Simple Website Crawling
  │   ├── deep-crawl.spec.ts      # Flow 2: Deep Website Crawling  
  │   └── collections.spec.ts     # Flow 3: Collection Management
  └── playwright.config.ts
  ```

## DEVELOPMENT SETUP:

1. **Prerequisites**: Node.js 18+, Python 3.8+
2. **Backend**: HTTP API Layer um bestehende MCP Tools
3. **Frontend**: Vite Template mit TypeScript
4. **Testing**: Playwright für E2E Tests der User Flows
5. **Development**: 
   - Backend auf Port 8000
   - Frontend auf Port 3000 mit API Proxy
6. **Environment**: Shared .env Konfiguration