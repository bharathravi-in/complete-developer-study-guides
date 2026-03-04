# 📅 Day 27 – AI + React

## 🎯 Learning Goals
- Integrate AI APIs with React
- Build streaming chat interfaces
- Implement AI-powered features
- Use Vercel AI SDK

---

## 📚 Theory

### Vercel AI SDK

```tsx
// Install: npm install ai openai

// app/api/chat/route.ts (Next.js)
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4-turbo'),
    messages,
    system: 'You are a helpful assistant.',
  });

  return result.toDataStreamResponse();
}

// components/Chat.tsx
'use client';

import { useChat } from 'ai/react';

export function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: '/api/chat',
  });

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.role}`}
          >
            <strong>{message.role === 'user' ? 'You' : 'AI'}:</strong>
            <p>{message.content}</p>
          </div>
        ))}
        {isLoading && <div className="loading">AI is thinking...</div>}
        {error && <div className="error">{error.message}</div>}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
}

// With streaming text generation
import { useCompletion } from 'ai/react';

function TextGenerator() {
  const { completion, input, handleInputChange, handleSubmit, isLoading } = useCompletion({
    api: '/api/completion',
  });

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Enter a prompt..."
        />
        <button type="submit">Generate</button>
      </form>
      
      {completion && (
        <div className="output">
          {completion}
        </div>
      )}
    </div>
  );
}
```

### Building Chat Interfaces

```tsx
// Advanced chat with message actions
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: Date;
}

function AdvancedChat() {
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    reload,
    stop,
    setMessages,
  } = useChat();

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const regenerate = () => {
    // Remove last assistant message and regenerate
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMessage) {
      setMessages(messages.filter(m => m.id !== messages[messages.length - 1].id));
      reload();
    }
  };

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onCopy={() => copyMessage(message.content)}
            onRegenerate={message.role === 'assistant' ? regenerate : undefined}
          />
        ))}
      </div>

      <div className="input-area">
        {isLoading && (
          <button onClick={stop} className="stop-btn">
            Stop generating
          </button>
        )}
        <form onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={handleInputChange}
            placeholder="Message..."
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e as any);
              }
            }}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

// Markdown rendering for AI responses
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

function MessageContent({ content }: { content: string }) {
  return (
    <ReactMarkdown
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              language={match[1]}
              style={oneDark}
              PreTag="div"
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
```

### AI-Powered Features

```tsx
// Smart search with embeddings
// app/api/search/route.ts
import { openai } from '@ai-sdk/openai';
import { embed } from 'ai';

export async function POST(req: Request) {
  const { query } = await req.json();

  // Generate embedding for query
  const { embedding } = await embed({
    model: openai.embedding('text-embedding-3-small'),
    value: query,
  });

  // Search vector database (e.g., Pinecone, Supabase)
  const results = await vectorDb.query({
    vector: embedding,
    topK: 5,
  });

  return Response.json({ results });
}

// components/SmartSearch.tsx
function SmartSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const search = async () => {
    setIsSearching(true);
    const res = await fetch('/api/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    setResults(data.results);
    setIsSearching(false);
  };

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search with natural language..."
      />
      <button onClick={search} disabled={isSearching}>
        Search
      </button>
      <SearchResults results={results} />
    </div>
  );
}

// AI-powered form autofill
function AIFormAssist() {
  const [description, setDescription] = useState('');
  const { complete, completion, isLoading } = useCompletion({
    api: '/api/extract-form-data',
  });

  const extractData = async () => {
    const result = await complete(description);
    const parsed = JSON.parse(result);
    // Auto-fill form fields
    setFormData(parsed);
  };

  return (
    <div>
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Describe your request in natural language..."
      />
      <button onClick={extractData} disabled={isLoading}>
        Auto-fill form
      </button>
    </div>
  );
}

// Content moderation
async function moderateContent(content: string) {
  const response = await fetch('/api/moderate', {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
  const { flagged, categories } = await response.json();
  return { flagged, categories };
}

function CommentForm() {
  const [comment, setComment] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    const { flagged } = await moderateContent(comment);
    if (flagged) {
      setError('Your comment contains inappropriate content.');
      return;
    }
    // Submit comment
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
      {error && <p className="error">{error}</p>}
      <button type="submit">Post Comment</button>
    </form>
  );
}
```

### Streaming and Real-time Updates

```tsx
// Custom streaming hook
function useStreamingResponse(url: string) {
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const stream = async (prompt: string) => {
    setIsStreaming(true);
    setResponse('');

    const res = await fetch(url, {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      setResponse((prev) => prev + chunk);
    }

    setIsStreaming(false);
  };

  return { response, isStreaming, stream };
}

// Server-Sent Events for real-time updates
function useSSE(url: string) {
  const [data, setData] = useState(null);

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, [url]);

  return data;
}
```

---

## ✅ Task: Build AI-Powered App

Create an AI assistant with:
- Streaming chat interface
- Message history
- Code syntax highlighting
- Copy/regenerate actions
- Smart search feature

---

## 🎯 Interview Questions & Answers

### Q1: How do you handle streaming responses in React?
**Answer:** Use ReadableStream API with `getReader()`, decode chunks with TextDecoder, update state incrementally. Libraries like Vercel AI SDK's `useChat` handle this automatically with Server-Sent Events.

### Q2: What are embeddings and how are they used?
**Answer:** Embeddings are vector representations of text. Used for semantic search, similarity matching, and RAG (Retrieval Augmented Generation). Generate with models like text-embedding-3-small, store in vector databases.

### Q3: How do you optimize AI API costs?
**Answer:** Cache responses, use cheaper models for simple tasks, batch requests, implement rate limiting, use embeddings for search instead of LLM calls, truncate context appropriately.

---

## ✅ Completion Checklist

- [ ] Integrate OpenAI/AI SDK
- [ ] Build streaming chat UI
- [ ] Implement AI features
- [ ] Handle errors gracefully
- [ ] Built AI-powered app

---

**Previous:** [Day 26 - React Native](../day-26/README.md)  
**Next:** [Day 28 - System Design](../day-28/README.md)
