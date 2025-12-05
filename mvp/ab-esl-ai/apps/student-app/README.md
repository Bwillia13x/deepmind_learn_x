# ESL Student App

A student-facing Progressive Web App (PWA) for ESL learners.

## Features

- **Join Class**: Enter class code to join teacher's session
- **Reading Practice**: Read aloud passages and get fluency feedback
- **Speaking Practice**: Pronunciation exercises with minimal pairs
- **Vocabulary Flashcards**: Learn key classroom vocabulary
- **Glossary/Translation**: See English text in student's L1 language

## Getting Started

```bash
cd apps/student-app
npm install
npm run dev
```

Open [http://localhost:3001](http://localhost:3001) in your browser.

## PWA Support

The app is designed as a Progressive Web App and can be installed on mobile devices:

1. Open the app in Chrome/Safari
2. Tap "Add to Home Screen"
3. Access offline with cached content

## Supported Languages

- Arabic (العربية)
- Chinese (中文)
- Spanish (Español)
- French (Français)
- Hindi (हिन्दी)
- Korean (한국어)
- Punjabi (ਪੰਜਾਬੀ)
- Somali (Soomaali)
- Tagalog
- Ukrainian (Українська)
- Urdu (اردو)
- Vietnamese (Tiếng Việt)

## Design Principles

- Large touch targets (48px minimum)
- High contrast colors
- Simple, emoji-based navigation
- Works offline with cached content
- Designed for mobile-first use in classrooms
- Reduced motion support for accessibility

## API Endpoints Used

- `POST /auth/join` - Join a class session
- `POST /v1/reading/score_audio` - Score reading fluency
- `POST /v1/speaking/score` - Score pronunciation
- `GET /v1/speaking/exercises` - Get exercises by L1
- `POST /v1/captions/gloss` - Get translations

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- PWA with Service Worker
