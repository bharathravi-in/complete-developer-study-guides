# 📅 Day 30 – Mock Interview & Wrap-up

## 🎯 Learning Goals
- Practice complete interview simulation
- Review 30-day journey
- Plan continued learning
- Build interview confidence

---

## 📚 Mock Interview Format

### Round 1: Technical Screening (30 min)

```
Interviewer questions - Answer aloud, then check answers below

1. "Explain how React's reconciliation works"
2. "What are the rules of hooks and why do they exist?"
3. "How would you optimize a component that re-renders too often?"
4. "Explain the difference between useEffect and useLayoutEffect"
5. "What's the purpose of keys in lists?"
```

<details>
<summary>✅ Sample Answers</summary>

1. **Reconciliation:** React compares Virtual DOM trees using a diffing algorithm. It uses element type and keys to determine what changed, then batches minimal DOM updates.

2. **Rules of hooks:** Call at top level (no conditionals/loops), only in React functions. React tracks hooks by call order - conditionals would break the state mapping.

3. **Optimization:** Use React.memo for component, useMemo for values, useCallback for functions. Profile first to identify actual bottleneck.

4. **useEffect vs useLayoutEffect:** useEffect runs asynchronously after paint (non-blocking). useLayoutEffect runs synchronously before paint (for DOM measurements).

5. **Keys:** Help React identify which items changed in lists. Without stable keys, React can't efficiently update/reorder items.

</details>

---

### Round 2: Code Exercise (45 min)

**Task: Build a searchable, paginated table component**

Requirements:
- Fetch data from API
- Search/filter functionality
- Pagination
- Loading/error states
- TypeScript

```tsx
// Implement this component

interface User {
  id: number;
  name: string;
  email: string;
  department: string;
}

interface UserTableProps {
  apiEndpoint: string;
}

function UserTable({ apiEndpoint }: UserTableProps) {
  // Your implementation here
}

// API returns:
// { data: User[], total: number, page: number, pageSize: number }
```

<details>
<summary>✅ Sample Implementation</summary>

```tsx
interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

function UserTable({ apiEndpoint }: UserTableProps) {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading, error } = useQuery({
    queryKey: ['users', page, debouncedSearch],
    queryFn: () => 
      fetch(`${apiEndpoint}?page=${page}&search=${debouncedSearch}`)
        .then(r => r.json()) as Promise<PaginatedResponse<User>>,
  });

  if (error) return <div>Error loading users</div>;

  const totalPages = data ? Math.ceil(data.total / data.pageSize) : 0;

  return (
    <div>
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search users..."
        aria-label="Search users"
      />

      {isLoading ? (
        <TableSkeleton rows={10} />
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Department</th>
            </tr>
          </thead>
          <tbody>
            {data?.data.map((user) => (
              <tr key={user.id}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.department}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <Pagination
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  );
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

</details>

---

### Round 3: System Design (45 min)

**Task: Design a dashboard for a SaaS analytics platform**

Requirements:
- Real-time metrics updates
- Multiple widget types (charts, tables, KPIs)
- Customizable layout (drag & drop)
- Performance with 50+ widgets
- Mobile responsive

```
Cover:
1. Component architecture
2. State management approach
3. Data fetching strategy
4. Performance optimizations
5. Key trade-offs
```

<details>
<summary>✅ Sample Design</summary>

```
ARCHITECTURE:

┌─────────────────────────────────────────────────────┐
│                  Dashboard Shell                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           Grid Layout (react-grid-layout)    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │ Widget   │ │ Widget   │ │ Widget   │    │   │
│  │  │ (Lazy)   │ │ (Lazy)   │ │ (Lazy)   │    │   │
│  │  └──────────┘ └──────────┘ └──────────┘    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

STATE MANAGEMENT:
- Layout config: Zustand (persisted to API)
- Widget data: TanStack Query (cached, refetch intervals)
- Real-time: WebSocket for live metrics

DATA FETCHING:
- Initial: Parallel fetch all visible widgets
- Real-time: Single WebSocket, fan out to widgets
- Stale-while-revalidate for dashboard switches

PERFORMANCE:
- Lazy load widgets below fold
- Virtualize for many widgets
- Web Workers for data processing
- Debounce layout saves
- Skeleton loading per widget

TRADE-OFFS:
- WebSocket vs polling: WS for <5s updates, polling simpler
- SSR vs CSR: CSR for highly interactive dashboard
- Shared vs per-widget fetch: Shared reduces connections
```

</details>

---

### Round 4: Behavioral (30 min)

Prepare stories for:

1. **Technical challenge:** Bug you solved, optimization you made
2. **Collaboration:** Working with difficult teammate/stakeholder
3. **Leadership:** Mentoring, driving technical decisions
4. **Failure:** Something that went wrong, what you learned
5. **Impact:** Measurable improvement you delivered

**STAR Format:**
- **S**ituation: Context
- **T**ask: Your responsibility
- **A**ction: What you did
- **R**esult: Outcome + learnings

---

## 🎉 30-Day Journey Recap

### Week 1: Foundations
- ✅ React fundamentals, Virtual DOM
- ✅ JSX, Components, Props
- ✅ State, Lifecycle, Hooks
- ✅ Built Todo App

### Week 2: Advanced React
- ✅ Rendering behavior, Fiber
- ✅ Performance optimization
- ✅ Error boundaries, Context
- ✅ State management libraries
- ✅ Routing, Testing

### Week 3: Modern React 2026
- ✅ TypeScript integration
- ✅ Forms with RHF + Zod
- ✅ API layer (TanStack Query)
- ✅ Server Components
- ✅ Next.js App Router
- ✅ Auth & Security
- ✅ Micro Frontends

### Week 4: Senior Level
- ✅ Architecture patterns
- ✅ Performance at scale
- ✅ Accessibility
- ✅ Animations
- ✅ React Native
- ✅ AI + React
- ✅ System Design
- ✅ Interview Prep

---

## 📈 Next Steps

### Continue Learning
1. **Build projects** - Apply knowledge to real apps
2. **Contribute to OSS** - Read React source, contribute to libraries
3. **Stay current** - Follow React team, read RFCs
4. **Teach others** - Blog, mentor, speak

### Resources
- [React Docs](https://react.dev)
- [Next.js Docs](https://nextjs.org/docs)
- [TanStack](https://tanstack.com)
- [Epic React by Kent C. Dodds](https://epicreact.dev)
- [React Newsletter](https://reactnewsletter.com)

### Practice
- [Frontend Mentor](https://www.frontendmentor.io)
- [LeetCode](https://leetcode.com) - JS problems
- [GreatFrontEnd](https://www.greatfrontend.com)

---

## ✅ Final Checklist

Before your interview:

- [ ] Can explain React concepts clearly
- [ ] Comfortable coding live
- [ ] Have system design approach
- [ ] Prepared STAR stories
- [ ] Reviewed this curriculum
- [ ] Rested and confident!

---

## 🏆 Congratulations!

You've completed the **30 Days React Mastery Plan 2026**!

You now have:
- Deep understanding of React internals
- Modern React 2026 best practices
- Performance optimization skills
- System design knowledge
- Interview preparation

**Go ace that interview! 🚀**

---

**Previous:** [Day 29 - Interview Questions](../day-29/README.md)  
**Back to:** [Main README](../../README.md)
