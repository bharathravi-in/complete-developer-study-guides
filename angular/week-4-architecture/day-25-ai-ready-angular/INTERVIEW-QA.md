# Day 25: AI-Ready Angular - Interview Questions & Answers

## Basic Level

### Q1: How do you structure an AI service in Angular?

**Answer:**
```typescript
// Abstract interface for flexibility
interface AIService {
  generateText(prompt: string): Observable<string>;
  streamText(prompt: string): Observable<string>;
}

// OpenAI implementation
@Injectable()
export class OpenAIService implements AIService {
  private http = inject(HttpClient);
  private apiKey = inject(AI_CONFIG).apiKey;

  generateText(prompt: string): Observable<string> {
    return this.http.post<any>(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4',
        messages: [{ role: 'user', content: prompt }]
      },
      { headers: { Authorization: `Bearer ${this.apiKey}` }}
    ).pipe(
      map(res => res.choices[0].message.content)
    );
  }

  streamText(prompt: string): Observable<string> {
    // Server-Sent Events for streaming
    return new Observable(subscriber => {
      const eventSource = new EventSource(`/api/ai/stream?prompt=${prompt}`);
      eventSource.onmessage = e => subscriber.next(JSON.parse(e.data).text);
      eventSource.onerror = () => subscriber.complete();
      return () => eventSource.close();
    });
  }
}

// Provider setup (swap implementations easily)
providers: [
  { provide: AIService, useClass: OpenAIService }
]
```

---

### Q2: How do you display streaming AI responses?

**Answer:**
```typescript
@Component({
  template: `
    <div class="response">
      {{ streamedText() }}
      @if (isStreaming()) {
        <span class="cursor">|</span>
      }
    </div>
  `
})
export class StreamingComponent {
  private ai = inject(AIService);
  streamedText = signal('');
  isStreaming = signal(false);

  generate(prompt: string) {
    this.streamedText.set('');
    this.isStreaming.set(true);

    this.ai.streamText(prompt).pipe(
      finalize(() => this.isStreaming.set(false))
    ).subscribe({
      next: chunk => this.streamedText.update(text => text + chunk)
    });
  }
}
```

---

### Q3: How do you implement a chat interface?

**Answer:**
```typescript
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

@Injectable()
export class ChatStore extends ComponentStore<{ messages: ChatMessage[] }> {
  private ai = inject(AIService);

  messages = this.selectSignal(state => state.messages);

  sendMessage(content: string): void {
    // Add user message
    this.patchState(state => ({
      messages: [...state.messages, { role: 'user', content, timestamp: new Date() }]
    }));

    // Get AI response
    const context = this.buildContext();
    this.ai.generateText(context).subscribe(response => {
      this.patchState(state => ({
        messages: [...state.messages, { role: 'assistant', content: response, timestamp: new Date() }]
      }));
    });
  }

  private buildContext(): string {
    return this.get().messages
      .map(m => `${m.role}: ${m.content}`)
      .join('\n');
  }
}

@Component({
  template: `
    <div class="chat">
      @for (msg of store.messages(); track msg.timestamp) {
        <div [class]="msg.role">{{ msg.content }}</div>
      }
    </div>
    <input [(ngModel)]="input" (keyup.enter)="send()">
  `
})
export class ChatComponent {
  store = inject(ChatStore);
  input = '';

  send() {
    if (this.input.trim()) {
      this.store.sendMessage(this.input);
      this.input = '';
    }
  }
}
```

---

## Intermediate Level

### Q4: How do you add AI suggestions to forms?

**Answer:**
```typescript
@Component({
  template: `
    <mat-form-field>
      <textarea matInput [(ngModel)]="description"></textarea>
      <button mat-icon-button matSuffix (click)="improve()" [disabled]="improving()">
        <mat-icon>auto_fix_high</mat-icon>
      </button>
    </mat-form-field>

    <div class="tags">
      @for (tag of tags(); track tag) {
        <mat-chip>{{ tag }}</mat-chip>
      }
      <button mat-button (click)="suggestTags()">Suggest Tags</button>
    </div>

    @if (suggestedTags().length) {
      <div class="suggestions">
        @for (tag of suggestedTags(); track tag) {
          <mat-chip (click)="addTag(tag)">+ {{ tag }}</mat-chip>
        }
      </div>
    }
  `
})
export class AIFormComponent {
  private ai = inject(AIService);

  description = '';
  tags = signal<string[]>([]);
  suggestedTags = signal<string[]>([]);
  improving = signal(false);

  improve() {
    this.improving.set(true);
    this.ai.generateText(`Improve: ${this.description}`).pipe(
      finalize(() => this.improving.set(false))
    ).subscribe(improved => this.description = improved);
  }

  suggestTags() {
    this.ai.generateText(`Suggest 5 tags for: ${this.description}`).pipe(
      map(result => result.split(',').map(t => t.trim()))
    ).subscribe(tags => this.suggestedTags.set(tags));
  }

  addTag(tag: string) {
    this.tags.update(t => [...t, tag]);
    this.suggestedTags.update(t => t.filter(x => x !== tag));
  }
}
```

---

### Q5: How do you implement semantic search?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class SemanticSearchService {
  private http = inject(HttpClient);
  private ai = inject(AIService);

  search(query: string): Observable<SearchResult[]> {
    // Convert natural language to search parameters
    return this.ai.generateText(
      `Convert to search: "${query}". Return JSON: {keywords: [], filters: {}}`
    ).pipe(
      map(response => JSON.parse(response)),
      switchMap(params => this.http.post<SearchResult[]>('/api/search', params))
    );
  }
}

@Component({
  template: `
    <input [formControl]="searchControl" placeholder="Ask anything...">
    
    @if (loading()) {
      <mat-progress-bar mode="indeterminate" />
    }

    @if (summary()) {
      <div class="ai-summary">
        <mat-icon>auto_awesome</mat-icon>
        {{ summary() }}
      </div>
    }

    @for (result of results(); track result.id) {
      <app-search-result [result]="result" />
    }
  `
})
export class SmartSearchComponent {
  private search = inject(SemanticSearchService);
  private ai = inject(AIService);

  searchControl = new FormControl('');
  results = signal<SearchResult[]>([]);
  summary = signal('');
  loading = signal(false);

  constructor() {
    this.searchControl.valueChanges.pipe(
      debounceTime(500),
      filter(q => q!.length > 3),
      tap(() => this.loading.set(true)),
      switchMap(q => this.search.search(q!))
    ).subscribe(results => {
      this.results.set(results);
      this.loading.set(false);
      this.generateSummary(results);
    });
  }

  private generateSummary(results: SearchResult[]) {
    const context = results.slice(0, 5).map(r => r.title).join(', ');
    this.ai.generateText(`Summarize: ${context}`)
      .subscribe(s => this.summary.set(s));
  }
}
```

---

### Q6: How do you handle rate limiting for AI APIs?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class AIRequestManager {
  private requestsThisMinute = 0;
  private readonly limit = 60;
  private queue: (() => void)[] = [];

  execute<T>(request: () => Observable<T>): Observable<T> {
    return new Observable(subscriber => {
      const executeRequest = () => {
        this.requestsThisMinute++;
        setTimeout(() => {
          this.requestsThisMinute--;
          this.processQueue();
        }, 60000);

        request().pipe(
          retry({
            count: 3,
            delay: (error) => {
              if (error.status === 429) {
                return timer(5000); // Rate limit retry
              }
              return throwError(() => error);
            }
          })
        ).subscribe(subscriber);
      };

      if (this.requestsThisMinute >= this.limit) {
        this.queue.push(executeRequest);
      } else {
        executeRequest();
      }
    });
  }

  private processQueue() {
    if (this.queue.length > 0 && this.requestsThisMinute < this.limit) {
      const next = this.queue.shift()!;
      next();
    }
  }
}

// Usage
@Injectable()
export class SafeAIService {
  private ai = inject(AIService);
  private manager = inject(AIRequestManager);

  generate(prompt: string): Observable<string> {
    return this.manager.execute(() => this.ai.generateText(prompt));
  }
}
```

---

## Advanced Level

### Q7: How do you build a content generation system?

**Answer:**
```typescript
interface ContentGeneratorOptions {
  type: 'blog' | 'social' | 'email';
  tone: 'professional' | 'casual' | 'friendly';
  length: number;
}

@Injectable({ providedIn: 'root' })
export class ContentGeneratorService {
  private ai = inject(AIService);

  generateBlogPost(topic: string, options: ContentGeneratorOptions): Observable<BlogPost> {
    const prompt = `
      Write a ${options.tone} blog post about: ${topic}
      Length: ~${options.length} words
      
      Return JSON: {
        title: string,
        introduction: string,
        sections: [{heading: string, content: string}],
        conclusion: string,
        metaDescription: string
      }
    `;

    return this.ai.generateText(prompt).pipe(
      map(response => JSON.parse(response)),
      catchError(() => of(null))
    );
  }

  generateSocialPosts(content: string): Observable<{twitter: string, linkedin: string}> {
    const prompt = `
      Create social media posts from:
      ${content}
      
      Return JSON:
      { twitter: "...(max 280)", linkedin: "..." }
    `;

    return this.ai.generateText(prompt).pipe(
      map(response => JSON.parse(response))
    );
  }

  rewriteForTone(text: string, tone: string): Observable<string> {
    return this.ai.generateText(`Rewrite in ${tone} tone:\n${text}`);
  }
}
```

---

### Q8: How do you implement AI-powered code assistance?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class CodeAssistService {
  private ai = inject(AIService);

  explainCode(code: string, language: string): Observable<string> {
    return this.ai.generateText(`
      Explain this ${language} code:
      \`\`\`${language}
      ${code}
      \`\`\`
    `);
  }

  suggestRefactoring(code: string): Observable<RefactoringSuggestion[]> {
    const prompt = `
      Suggest refactoring for this code.
      Return JSON array: [{issue: string, suggestion: string, improvedCode: string}]
      
      Code:
      ${code}
    `;

    return this.ai.generateText(prompt).pipe(
      map(response => JSON.parse(response))
    );
  }

  generateTests(code: string, framework: string): Observable<string> {
    return this.ai.generateText(`
      Generate ${framework} unit tests for:
      ${code}
    `);
  }

  fixError(code: string, error: string): Observable<string> {
    return this.ai.generateText(`
      Fix this error: ${error}
      
      Code:
      ${code}
      
      Return only the corrected code.
    `);
  }
}
```

---

## Quick Reference

```
AI Integration Patterns:
────────────────────────
Abstract Service    - Swap AI providers easily
Streaming           - Real-time response display
Chat Context        - Maintain conversation history
Form Assistance     - Auto-complete, suggestions
Semantic Search     - Natural language queries
Content Generation  - Automated content creation

Error Handling:
───────────────
Rate Limits (429)   - Queue requests, exponential backoff
Timeouts            - Set reasonable limits
Empty Responses     - Retry or fallback
Invalid JSON        - Parse errors gracefully

Performance:
────────────
Rate Limiting       - Track requests per minute
Request Queuing     - Buffer during limits
Caching             - Cache common queries
Debouncing          - Avoid rapid API calls

Security:
─────────
Server-side Keys    - Never expose API keys
Input Sanitization  - Clean user prompts
Output Validation   - Validate AI responses
Content Filtering   - Filter inappropriate content

Streaming Setup:
────────────────
Backend: SSE (Server-Sent Events)
Frontend: EventSource or fetch with ReadableStream
Display: Signal updates for reactive rendering
```
