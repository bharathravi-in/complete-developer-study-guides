# Day 10: GraphQL Fundamentals

## What Is GraphQL?

GraphQL is a **query language for APIs** and a **runtime** for executing those queries. Created by Facebook (2012), open-sourced (2015).

**Core Principle**: Client specifies exactly what data it needs.

## GraphQL vs REST

| Aspect | REST | GraphQL |
|--------|------|---------|
| Endpoints | Multiple (`/users`, `/posts`) | Single (`/graphql`) |
| Data Shape | Server decides | Client decides |
| Over-fetching | Common | Eliminated |
| Under-fetching | N+1 problem | Single request |
| Caching | HTTP built-in | Custom (Apollo, Relay) |
| Versioning | URL/header | Schema evolution |
| File Upload | Native | Custom (multipart) |
| Real-time | WebSocket/SSE | Subscriptions built-in |

## Schema Definition Language (SDL)

```graphql
# Types
type User {
  id: ID!
  name: String!
  email: String!
  age: Int
  posts: [Post!]!
  role: Role!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  tags: [String!]!
  published: Boolean!
}

type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
}

# Enum
enum Role {
  ADMIN
  USER
  GUEST
}

# Custom scalar
scalar DateTime

# Input types (for mutations)
input CreateUserInput {
  name: String!
  email: String!
  age: Int
  role: Role = USER
}

input UpdateUserInput {
  name: String
  email: String
  age: Int
}

# Query root
type Query {
  user(id: ID!): User
  users(limit: Int = 10, offset: Int = 0, role: Role): [User!]!
  post(id: ID!): Post
  posts(published: Boolean): [Post!]!
  search(term: String!): [SearchResult!]!
}

# Mutation root
type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
  createPost(title: String!, content: String!, authorId: ID!): Post!
}

# Subscription root
type Subscription {
  postCreated: Post!
  commentAdded(postId: ID!): Comment!
}

# Union type
union SearchResult = User | Post | Comment

# Interface
interface Node {
  id: ID!
  createdAt: DateTime!
}
```

## Queries

```graphql
# Simple query
query GetUser {
  user(id: "123") {
    name
    email
  }
}

# Response
{
  "data": {
    "user": {
      "name": "Bharath",
      "email": "bharath@example.com"
    }
  }
}

# Nested query (solve N+1 in single request)
query GetUserWithPosts {
  user(id: "123") {
    name
    posts {
      title
      comments {
        text
        author {
          name
        }
      }
    }
  }
}

# Variables
query GetUser($id: ID!) {
  user(id: $id) {
    name
    email
    role
  }
}
# Variables: { "id": "123" }

# Aliases
query ComparePosts {
  firstPost: post(id: "1") { title }
  secondPost: post(id: "2") { title }
}

# Fragments (reusable field sets)
fragment UserFields on User {
  id
  name
  email
  role
}

query GetUsers {
  admin: user(id: "1") { ...UserFields }
  regular: user(id: "2") { ...UserFields }
}
```

## Mutations

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
    email
    role
  }
}

# Variables
{
  "input": {
    "name": "New User",
    "email": "new@example.com",
    "role": "ADMIN"
  }
}
```

## Resolvers (Node.js / Apollo Server)

```typescript
import { ApolloServer } from '@apollo/server';

const resolvers = {
  Query: {
    user: async (_parent, { id }, context) => {
      return context.dataSources.users.findById(id);
    },
    users: async (_parent, { limit, offset, role }, context) => {
      return context.dataSources.users.findAll({ limit, offset, role });
    },
  },

  Mutation: {
    createUser: async (_parent, { input }, context) => {
      return context.dataSources.users.create(input);
    },
  },

  // Field resolver for nested data
  User: {
    posts: async (parent, _args, context) => {
      // parent = the User object from the parent resolver
      return context.dataSources.posts.findByAuthor(parent.id);
    },
  },

  // Union type resolver
  SearchResult: {
    __resolveType(obj) {
      if (obj.email) return 'User';
      if (obj.title) return 'Post';
      if (obj.text) return 'Comment';
      return null;
    },
  },
};
```

## N+1 Problem — DataLoader Solution

```typescript
import DataLoader from 'dataloader';

// Without DataLoader: N+1 queries
// Query: users(limit: 10) → 1 query for users + 10 queries for posts

// With DataLoader: batch + cache
const postLoader = new DataLoader(async (userIds: string[]) => {
  // Single batch query: SELECT * FROM posts WHERE author_id IN (...)
  const posts = await db.posts.findByAuthorIds(userIds);

  // Map results to match input order
  return userIds.map(id => posts.filter(p => p.authorId === id));
});

const resolvers = {
  User: {
    posts: (parent) => postLoader.load(parent.id), // Batched!
  },
};
```

## Error Handling

```json
{
  "data": {
    "user": null
  },
  "errors": [
    {
      "message": "User not found",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["user"],
      "extensions": {
        "code": "NOT_FOUND",
        "timestamp": "2025-01-01T00:00:00Z"
      }
    }
  ]
}
```

## When to Use GraphQL vs REST

### Use GraphQL When:
- Multiple clients need different data shapes (web, mobile, watch)
- Deep nested data relationships
- Rapid frontend iteration (no backend changes needed)
- Real-time features needed (subscriptions)

### Use REST When:
- Simple CRUD with predictable data shapes
- Heavy caching requirements (HTTP caching)
- File uploads are primary use case
- Public API with wide adoption
- Team is more familiar with REST

### Use Both:
- REST for simple public endpoints + GraphQL for complex internal queries
- BFF (Backend for Frontend) pattern with GraphQL aggregating REST microservices

## Key Takeaways

1. **GraphQL eliminates over/under-fetching** — client gets exactly what it asks for
2. **Single endpoint** simplifies routing but complicates caching
3. **DataLoader** is mandatory for solving N+1 in production
4. **Schema = API contract** — strongly typed, self-documenting
5. **Not a REST replacement** — different trade-offs; use the right tool
