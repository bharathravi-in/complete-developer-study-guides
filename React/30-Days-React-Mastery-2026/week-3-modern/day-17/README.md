# 📅 Day 17 – API Layer

## 🎯 Learning Goals
- Master TanStack Query (React Query)
- Learn SWR for data fetching
- Understand Axios patterns
- Get introduced to GraphQL

---

## 📚 Theory

### TanStack Query (React Query)

```tsx
import { 
  QueryClient, 
  QueryClientProvider, 
  useQuery, 
  useMutation, 
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query';

// Setup
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000,   // 10 minutes (formerly cacheTime)
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MyApp />
      <ReactQueryDevtools />
    </QueryClientProvider>
  );
}

// Basic query
function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    enabled: !!userId, // Only fetch when userId exists
  });

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {error.message}</div>;

  return <div>{data.name}</div>;
}

// Query with dependencies
function UserPosts({ userId }: { userId: string }) {
  const userQuery = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  const postsQuery = useQuery({
    queryKey: ['posts', userId],
    queryFn: () => fetchUserPosts(userId),
    enabled: !!userQuery.data, // Wait for user data
  });

  // ...
}

// Mutations
function CreatePost() {
  const queryClient = useQueryClient();
  
  const mutation = useMutation({
    mutationFn: (newPost: NewPost) => api.createPost(newPost),
    onMutate: async (newPost) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({ queryKey: ['posts'] });
      
      // Snapshot previous value
      const previousPosts = queryClient.getQueryData(['posts']);
      
      // Optimistic update
      queryClient.setQueryData(['posts'], (old: Post[]) => [
        ...old,
        { id: 'temp', ...newPost },
      ]);
      
      return { previousPosts };
    },
    onError: (err, newPost, context) => {
      // Rollback on error
      queryClient.setQueryData(['posts'], context?.previousPosts);
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });

  const handleSubmit = (data: NewPost) => {
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ... */}
      <button disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  );
}

// Infinite queries (pagination)
function InfiniteList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['posts'],
    queryFn: ({ pageParam = 0 }) => fetchPosts(pageParam),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: 0,
  });

  return (
    <div>
      {data?.pages.map((page) =>
        page.items.map((item) => <PostCard key={item.id} post={item} />)
      )}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        {isFetchingNextPage
          ? 'Loading more...'
          : hasNextPage
          ? 'Load More'
          : 'Nothing more'}
      </button>
    </div>
  );
}
```

### SWR

```tsx
import useSWR, { SWRConfig, useSWRMutation } from 'swr';

// Basic fetcher
const fetcher = (url: string) => fetch(url).then(res => res.json());

// Basic usage
function Profile() {
  const { data, error, isLoading, mutate } = useSWR('/api/user', fetcher);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading user</div>;

  return <div>Hello {data.name}!</div>;
}

// With options
function Posts() {
  const { data } = useSWR('/api/posts', fetcher, {
    refreshInterval: 3000,        // Poll every 3s
    revalidateOnFocus: true,      // Revalidate on window focus
    dedupingInterval: 2000,       // Dedupe requests
    errorRetryCount: 3,
  });
  // ...
}

// Global config
function App() {
  return (
    <SWRConfig 
      value={{
        fetcher,
        refreshInterval: 0,
        revalidateOnFocus: false,
      }}
    >
      <MyApp />
    </SWRConfig>
  );
}

// Mutations
function CreateItem() {
  const { trigger, isMutating } = useSWRMutation(
    '/api/items',
    (url, { arg }: { arg: NewItem }) =>
      fetch(url, {
        method: 'POST',
        body: JSON.stringify(arg),
      }).then(res => res.json())
  );

  const handleCreate = async (data: NewItem) => {
    await trigger(data);
  };

  return <button onClick={handleCreate} disabled={isMutating}>Create</button>;
}

// Conditional fetching
function ConditionalFetch({ shouldFetch }: { shouldFetch: boolean }) {
  const { data } = useSWR(shouldFetch ? '/api/data' : null, fetcher);
  // ...
}
```

### Axios Setup

```tsx
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// Create instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // Handle 401 - refresh token
    if (error.response?.status === 401 && originalRequest) {
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const { data } = await axios.post('/auth/refresh', { refreshToken });
        localStorage.setItem('token', data.accessToken);
        originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// API functions
export const userApi = {
  getAll: () => api.get<User[]>('/users'),
  getById: (id: string) => api.get<User>(`/users/${id}`),
  create: (data: CreateUserDto) => api.post<User>('/users', data),
  update: (id: string, data: UpdateUserDto) => api.put<User>(`/users/${id}`, data),
  delete: (id: string) => api.delete(`/users/${id}`),
};

// Usage with React Query
const useUsers = () => useQuery({
  queryKey: ['users'],
  queryFn: async () => {
    const { data } = await userApi.getAll();
    return data;
  },
});
```

### GraphQL Basics

```tsx
import { gql, useQuery, useMutation, ApolloClient, InMemoryCache } from '@apollo/client';

// Apollo Client setup
const client = new ApolloClient({
  uri: 'https://api.example.com/graphql',
  cache: new InMemoryCache(),
});

// Queries
const GET_USERS = gql`
  query GetUsers($limit: Int) {
    users(limit: $limit) {
      id
      name
      email
      posts {
        id
        title
      }
    }
  }
`;

function UserList() {
  const { loading, error, data } = useQuery(GET_USERS, {
    variables: { limit: 10 },
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data.users.map((user: User) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

// Mutations
const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id
      name
      email
    }
  }
`;

function CreateUser() {
  const [createUser, { loading, error }] = useMutation(CREATE_USER, {
    refetchQueries: [{ query: GET_USERS }],
    update(cache, { data: { createUser } }) {
      cache.modify({
        fields: {
          users(existing = []) {
            const newUserRef = cache.writeFragment({
              data: createUser,
              fragment: gql`
                fragment NewUser on User {
                  id
                  name
                  email
                }
              `,
            });
            return [...existing, newUserRef];
          },
        },
      });
    },
  });

  const handleSubmit = (input: CreateUserInput) => {
    createUser({ variables: { input } });
  };

  return <form onSubmit={handleSubmit}>{/* ... */}</form>;
}
```

---

## ✅ Task: API Service Layer

```tsx
// services/api.ts
import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: (failureCount, error) => {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          return false;
        }
        return failureCount < 3;
      },
    },
  },
});

// services/users.ts
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: string) => [...userKeys.lists(), { filters }] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

export const useUsers = (filters?: string) => {
  return useQuery({
    queryKey: userKeys.list(filters || ''),
    queryFn: () => api.get('/users', { params: { filters } }).then(r => r.data),
  });
};

export const useUser = (id: string) => {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => api.get(`/users/${id}`).then(r => r.data),
    enabled: !!id,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateUserDto) => api.post('/users', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};
```

---

## 🎯 Interview Questions & Answers

### Q1: TanStack Query vs SWR?
**Answer:** Both are data fetching libraries. TanStack Query has more features (mutations, infinite queries, devtools). SWR is simpler, smaller. TanStack Query is preferred for complex apps.

### Q2: What is staleTime vs gcTime?
**Answer:**
- **staleTime:** How long data is "fresh" before refetch on next access
- **gcTime:** How long unused data stays in cache before garbage collection

### Q3: How do you handle optimistic updates?
**Answer:** In `onMutate`: cancel queries, snapshot previous data, apply optimistic update. In `onError`: rollback using snapshot. In `onSettled`: invalidate queries to refetch.

---

## ✅ Completion Checklist

- [ ] Can use TanStack Query
- [ ] Understand SWR basics
- [ ] Set up Axios with interceptors
- [ ] Know GraphQL basics
- [ ] Built API service layer

---

**Previous:** [Day 16 - Forms](../day-16/README.md)  
**Next:** [Day 18 - React Server Components](../day-18/README.md)
