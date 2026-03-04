# Day 25: AI-Ready Angular

## Overview

Building Angular applications ready for AI integration involves creating flexible architectures that can incorporate LLMs, AI services, and intelligent features while maintaining performance and user experience.

---

## AI Integration Patterns

### Service Architecture for AI

```typescript
// AI Service abstraction
interface AIService {
  generateText(prompt: string, options?: AIOptions): Observable<string>;
  streamText(prompt: string, options?: AIOptions): Observable<string>;
  analyze(input: string, type: AnalysisType): Observable<AnalysisResult>;
}

// Configuration
export interface AIConfig {
  provider: 'openai' | 'anthropic' | 'azure' | 'local';
  apiKey?: string;
  endpoint?: string;
  model: string;
  maxTokens: number;
}

export const AI_CONFIG = new InjectionToken<AIConfig>('AI_CONFIG');

// OpenAI Implementation
@Injectable()
export class OpenAIService implements AIService {
  private http = inject(HttpClient);
  private config = inject(AI_CONFIG);

  generateText(prompt: string, options?: AIOptions): Observable<string> {
    return this.http.post<OpenAIResponse>(
      'https://api.openai.com/v1/chat/completions',
      {
        model: this.config.model,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: options?.maxTokens ?? this.config.maxTokens
      },
      {
        headers: { Authorization: `Bearer ${this.config.apiKey}` }
      }
    ).pipe(
      map(response => response.choices[0].message.content)
    );
  }

  streamText(prompt: string, options?: AIOptions): Observable<string> {
    return new Observable(subscriber => {
      const eventSource = new EventSource(
        `${this.config.endpoint}/stream?prompt=${encodeURIComponent(prompt)}`
      );

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        subscriber.next(data.text);
        if (data.done) {
          subscriber.complete();
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        subscriber.error(new Error('Stream connection failed'));
        eventSource.close();
      };

      return () => eventSource.close();
    });
  }
}
```

---

## Chat Interface

```typescript
// Message model
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status: 'pending' | 'sent' | 'error';
}

// Chat store
@Injectable()
export class ChatStore extends ComponentStore<ChatState> {
  private ai = inject(AIService);

  readonly messages = this.selectSignal(state => state.messages);
  readonly isGenerating = this.selectSignal(state => state.isGenerating);

  readonly sendMessage = this.effect((message$: Observable<string>) => {
    return message$.pipe(
      tap(content => {
        // Add user message
        this.addMessage({
          id: generateId(),
          role: 'user',
          content,
          timestamp: new Date(),
          status: 'sent'
        });
        this.patchState({ isGenerating: true });
      }),
      switchMap(content => {
        const context = this.buildContext();
        return this.ai.streamText(context + '\n\nUser: ' + content).pipe(
          scan((acc, chunk) => acc + chunk, ''),
          tap(response => this.updateAssistantMessage(response)),
          catchError(error => {
            this.handleError(error);
            return EMPTY;
          }),
          finalize(() => this.patchState({ isGenerating: false }))
        );
      })
    );
  });

  private buildContext(): string {
    return this.get().messages
      .slice(-10)
      .map(m => `${m.role}: ${m.content}`)
      .join('\n');
  }
}

// Chat component
@Component({
  selector: 'app-chat',
  template: `
    <div class="chat-container">
      <div class="messages" #messageContainer>
        @for (message of store.messages(); track message.id) {
          <app-chat-message [message]="message" />
        }
        @if (store.isGenerating()) {
          <app-typing-indicator />
        }
      </div>

      <div class="input-container">
        <textarea
          [(ngModel)]="inputText"
          (keydown.enter)="sendMessage($event)"
          placeholder="Type a message..."
          [disabled]="store.isGenerating()"
        ></textarea>
        <button 
          mat-icon-button 
          (click)="sendMessage()"
          [disabled]="!inputText || store.isGenerating()"
        >
          <mat-icon>send</mat-icon>
        </button>
      </div>
    </div>
  `
})
export class ChatComponent {
  store = inject(ChatStore);
  inputText = '';

  sendMessage(event?: KeyboardEvent) {
    if (event && !event.shiftKey) {
      event.preventDefault();
    }
    if (this.inputText.trim()) {
      this.store.sendMessage(this.inputText);
      this.inputText = '';
    }
  }
}
```

---

## Streaming Responses

```typescript
// Streaming text component
@Component({
  selector: 'app-streaming-text',
  template: `
    <div class="streaming-container">
      <div class="text" [innerHTML]="displayText() | markdown"></div>
      @if (isStreaming()) {
        <span class="cursor">|</span>
      }
    </div>
  `
})
export class StreamingTextComponent {
  displayText = signal('');
  isStreaming = signal(false);

  private ai = inject(AIService);

  generateResponse(prompt: string) {
    this.displayText.set('');
    this.isStreaming.set(true);

    this.ai.streamText(prompt).pipe(
      finalize(() => this.isStreaming.set(false))
    ).subscribe({
      next: chunk => this.displayText.update(text => text + chunk),
      error: () => this.displayText.set('Error generating response')
    });
  }
}

// Markdown pipe for formatting
@Pipe({ name: 'markdown', standalone: true })
export class MarkdownPipe implements PipeTransform {
  transform(value: string): string {
    // Simple markdown conversion
    return value
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  }
}
```

---

## Intelligent Form Assistance

```typescript
// Form with AI assistance
@Component({
  selector: 'app-ai-form',
  template: `
    <form [formGroup]="form">
      <mat-form-field>
        <mat-label>Description</mat-label>
        <textarea matInput formControlName="description" rows="4"></textarea>
        <button mat-icon-button matSuffix (click)="improveText()" [disabled]="improving()">
          <mat-icon>auto_fix_high</mat-icon>
        </button>
      </mat-form-field>

      <mat-form-field>
        <mat-label>Tags</mat-label>
        <mat-chip-grid #chipGrid formControlName="tags">
          @for (tag of form.get('tags')?.value; track tag) {
            <mat-chip-row (removed)="removeTag(tag)">
              {{ tag }}
            </mat-chip-row>
          }
        </mat-chip-grid>
        <button mat-icon-button (click)="suggestTags()" [disabled]="suggestingTags()">
          <mat-icon>lightbulb</mat-icon>
        </button>
      </mat-form-field>

      @if (suggestedTags().length) {
        <div class="suggestions">
          <span>Suggested tags:</span>
          @for (tag of suggestedTags(); track tag) {
            <mat-chip (click)="addTag(tag)">{{ tag }}</mat-chip>
          }
        </div>
      }
    </form>
  `
})
export class AIFormComponent {
  private ai = inject(AIService);

  form = inject(FormBuilder).group({
    description: [''],
    tags: [[]]
  });

  improving = signal(false);
  suggestingTags = signal(false);
  suggestedTags = signal<string[]>([]);

  improveText() {
    const description = this.form.get('description')?.value;
    if (!description) return;

    this.improving.set(true);
    this.ai.generateText(
      `Improve this text for clarity and professionalism:\n\n${description}`
    ).pipe(
      finalize(() => this.improving.set(false))
    ).subscribe(improved => {
      this.form.patchValue({ description: improved });
    });
  }

  suggestTags() {
    const description = this.form.get('description')?.value;
    if (!description) return;

    this.suggestingTags.set(true);
    this.ai.generateText(
      `Suggest 5 relevant tags for this content (return as comma-separated list):\n\n${description}`
    ).pipe(
      finalize(() => this.suggestingTags.set(false))
    ).subscribe(result => {
      const tags = result.split(',').map(t => t.trim());
      this.suggestedTags.set(tags);
    });
  }

  addTag(tag: string) {
    const current = this.form.get('tags')?.value || [];
    this.form.patchValue({ tags: [...current, tag] });
    this.suggestedTags.update(tags => tags.filter(t => t !== tag));
  }
}
```

---

## Intelligent Search

```typescript
// Semantic search service
@Injectable({ providedIn: 'root' })
export class SemanticSearchService {
  private http = inject(HttpClient);
  private ai = inject(AIService);

  search(query: string, options: SearchOptions): Observable<SearchResult[]> {
    return this.http.post<SearchResult[]>('/api/search/semantic', {
      query,
      ...options
    });
  }

  // Generate search query from natural language
  naturalLanguageSearch(input: string): Observable<SearchResult[]> {
    return this.ai.generateText(
      `Convert to search query: "${input}"\nOutput JSON: {keywords: [], filters: {}}`
    ).pipe(
      map(response => JSON.parse(response)),
      switchMap(parsed => this.search(parsed.keywords.join(' '), parsed.filters))
    );
  }
}

// Search component
@Component({
  selector: 'app-smart-search',
  template: `
    <div class="search-container">
      <mat-form-field>
        <mat-icon matPrefix>search</mat-icon>
        <input matInput
               [formControl]="searchControl"
               placeholder="Search or ask a question...">
        <button mat-icon-button matSuffix *ngIf="searchControl.value" (click)="clear()">
          <mat-icon>close</mat-icon>
        </button>
      </mat-form-field>

      @if (isSearching()) {
        <mat-progress-bar mode="indeterminate" />
      }

      @if (aiSummary()) {
        <div class="ai-summary">
          <mat-icon>auto_awesome</mat-icon>
          <p>{{ aiSummary() }}</p>
        </div>
      }

      <div class="results">
        @for (result of results(); track result.id) {
          <app-search-result [result]="result" />
        }
      </div>
    </div>
  `
})
export class SmartSearchComponent {
  private searchService = inject(SemanticSearchService);
  private ai = inject(AIService);

  searchControl = new FormControl('');
  results = signal<SearchResult[]>([]);
  aiSummary = signal('');
  isSearching = signal(false);

  constructor() {
    this.searchControl.valueChanges.pipe(
      debounceTime(500),
      distinctUntilChanged(),
      filter(query => query!.length > 2),
      tap(() => this.isSearching.set(true)),
      switchMap(query => this.searchService.naturalLanguageSearch(query!))
    ).subscribe(results => {
      this.results.set(results);
      this.isSearching.set(false);
      this.generateSummary(results);
    });
  }

  private generateSummary(results: SearchResult[]) {
    if (results.length === 0) return;

    const context = results.slice(0, 5).map(r => r.title).join(', ');
    this.ai.generateText(
      `Briefly summarize these search results in one sentence: ${context}`
    ).subscribe(summary => this.aiSummary.set(summary));
  }
}
```

---

## Content Generation

```typescript
// Content generator service
@Injectable({ providedIn: 'root' })
export class ContentGeneratorService {
  private ai = inject(AIService);

  generateBlogPost(topic: string, options: ContentOptions): Observable<BlogPost> {
    const prompt = `
      Write a blog post about: ${topic}
      Style: ${options.style}
      Length: ${options.length} words
      Include: title, introduction, main sections, conclusion
      
      Return as JSON: {
        title: string,
        introduction: string,
        sections: [{heading: string, content: string}],
        conclusion: string
      }
    `;

    return this.ai.generateText(prompt).pipe(
      map(response => JSON.parse(response))
    );
  }

  rewriteForTone(text: string, tone: 'professional' | 'casual' | 'friendly'): Observable<string> {
    return this.ai.generateText(
      `Rewrite this in a ${tone} tone:\n\n${text}`
    );
  }

  generateSocialPosts(content: string): Observable<SocialPosts> {
    const prompt = `
      Create social media posts from this content:
      ${content}
      
      Return JSON:
      {
        twitter: string (max 280 chars),
        linkedin: string,
        instagram: string
      }
    `;

    return this.ai.generateText(prompt).pipe(
      map(response => JSON.parse(response))
    );
  }
}

// Blog post generator component
@Component({
  selector: 'app-blog-generator',
  template: `
    <div class="generator">
      <mat-form-field>
        <mat-label>Topic</mat-label>
        <input matInput [(ngModel)]="topic" placeholder="Enter blog topic">
      </mat-form-field>

      <mat-select [(ngModel)]="style">
        <mat-option value="informative">Informative</mat-option>
        <mat-option value="persuasive">Persuasive</mat-option>
        <mat-option value="storytelling">Storytelling</mat-option>
      </mat-select>

      <button mat-raised-button color="primary" 
              (click)="generate()" 
              [disabled]="!topic || generating()">
        @if (generating()) {
          <mat-spinner diameter="20" />
        } @else {
          Generate
        }
      </button>

      @if (generatedPost()) {
        <article class="preview">
          <h1>{{ generatedPost()?.title }}</h1>
          <p class="intro">{{ generatedPost()?.introduction }}</p>
          
          @for (section of generatedPost()?.sections; track section.heading) {
            <section>
              <h2>{{ section.heading }}</h2>
              <p>{{ section.content }}</p>
            </section>
          }
          
          <p class="conclusion">{{ generatedPost()?.conclusion }}</p>
        </article>
      }
    </div>
  `
})
export class BlogGeneratorComponent {
  private generator = inject(ContentGeneratorService);

  topic = '';
  style: 'informative' | 'persuasive' | 'storytelling' = 'informative';
  generating = signal(false);
  generatedPost = signal<BlogPost | null>(null);

  generate() {
    this.generating.set(true);
    this.generator.generateBlogPost(this.topic, {
      style: this.style,
      length: 500
    }).pipe(
      finalize(() => this.generating.set(false))
    ).subscribe(post => this.generatedPost.set(post));
  }
}
```

---

## Rate Limiting & Error Handling

```typescript
// AI request management
@Injectable({ providedIn: 'root' })
export class AIRequestManager {
  private queue: Array<{ request: () => Observable<any>; resolve: (value: any) => void }> = [];
  private processing = false;
  private requestsThisMinute = 0;
  private readonly maxRequestsPerMinute = 60;

  execute<T>(request: () => Observable<T>): Observable<T> {
    return new Observable(subscriber => {
      if (this.requestsThisMinute >= this.maxRequestsPerMinute) {
        this.queue.push({
          request,
          resolve: value => subscriber.next(value)
        });
      } else {
        this.processRequest(request).subscribe({
          next: value => subscriber.next(value),
          error: err => subscriber.error(err),
          complete: () => subscriber.complete()
        });
      }
    });
  }

  private processRequest<T>(request: () => Observable<T>): Observable<T> {
    this.requestsThisMinute++;
    
    setTimeout(() => {
      this.requestsThisMinute--;
      this.processQueue();
    }, 60000);

    return request().pipe(
      retry({
        count: 3,
        delay: (error, retryCount) => {
          if (error.status === 429) {
            return timer(Math.pow(2, retryCount) * 1000);
          }
          return throwError(() => error);
        }
      })
    );
  }

  private processQueue() {
    if (this.queue.length > 0 && this.requestsThisMinute < this.maxRequestsPerMinute) {
      const { request, resolve } = this.queue.shift()!;
      this.processRequest(request).subscribe(resolve);
    }
  }
}
```

---

## Summary

| Pattern | Use Case |
|---------|----------|
| AI Service Interface | Abstract AI provider |
| Streaming | Real-time text generation |
| Form Assistance | Auto-complete, suggestions |
| Semantic Search | Natural language queries |
| Content Generation | Automated content creation |
| Rate Limiting | API request management |
