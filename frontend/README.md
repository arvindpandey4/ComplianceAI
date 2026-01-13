# ComplianceAI - Frontend

Enterprise-grade AI-powered regulatory compliance and audit intelligence platform.

## Features

- **AI-Powered Analysis**: Advanced natural language processing for compliance document analysis
- **Real-time Chat Interface**: Professional chat UI for interactive compliance queries
- **Document Ingestion**: Upload and process PDF compliance documents
- **Source Attribution**: Detailed citations and references for all compliance insights
- **Session Management**: Persistent conversation history across sessions
- **Responsive Design**: Optimized for desktop and mobile devices
- **Enterprise UI**: Professional, modern interface built with React and Tailwind CSS

## Tech Stack

- **Framework**: React 19 with Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Build Tool**: Vite

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment

The frontend connects to the backend API at `http://localhost:8000/api/v1` by default.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ChatInterface.jsx    # Main chat interface component
│   ├── services/
│   │   └── api.js                # API client configuration
│   ├── App.jsx                   # Root application component
│   ├── main.jsx                  # Application entry point
│   └── index.css                 # Global styles and Tailwind config
├── public/                       # Static assets
├── index.html                    # HTML template
└── package.json                  # Dependencies and scripts
```

## Features in Detail

### Chat Interface
- Real-time message streaming
- Typing indicators
- Message timestamps
- Copy to clipboard functionality
- Status badges for compliance results

### Document Management
- Drag-and-drop file upload
- PDF document processing
- Active document indicator
- Upload progress feedback

### Quick Actions
- Pre-defined compliance queries
- One-click question templates
- Contextual suggestions

### Sidebar Navigation
- Session management
- Quick action shortcuts
- Settings and help access
- Responsive mobile menu

## Development

```bash
# Run linter
npm run lint

# Format code
npm run format
```

## License

Proprietary - All rights reserved

## Support

For support and inquiries, please contact the development team.
