# Day 20: GraphQL with Node.js

## 🎯 Learning Objectives
- Build GraphQL APIs with Apollo Server
- Define schemas, resolvers, and data loaders
- Implement authentication and authorization in GraphQL
- Understand performance optimization (N+1, caching, batching)

---

## 📚 GraphQL Fundamentals

### Apollo Server Setup

```javascript
const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');
const express = require('express');

const app = express();

// Type definitions (schema)
const typeDefs = `#graphql
  type User {
    id: ID!
    name: String!
    email: String!
    role: Role!
    posts: [Post!]!
    createdAt: String!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
    comments: [Comment!]!
    published: Boolean!
    createdAt: String!
  }

  type Comment {
    id: ID!
    text: String!
    author: User!
    post: Post!
  }

  enum Role {
    USER
    ADMIN
    MODERATOR
  }

  type Query {
    users(page: Int, limit: Int): UserConnection!
    user(id: ID!): User
    posts(published: Boolean): [Post!]!
    post(id: ID!): Post
    me: User
  }

  type Mutation {
    createUser(input: CreateUserInput!): User!
    updateUser(id: ID!, input: UpdateUserInput!): User!
    createPost(input: CreatePostInput!): Post!
    deletePost(id: ID!): Boolean!
    addComment(postId: ID!, text: String!): Comment!
  }

  input CreateUserInput {
    name: String!
    email: String!
    password: String!
  }

  input UpdateUserInput {
    name: String
    email: String
  }

  input CreatePostInput {
    title: String!
    content: String!
    published: Boolean
  }

  type UserConnection {
    nodes: [User!]!
    totalCount: Int!
    hasNextPage: Boolean!
  }

  type Subscription {
    postCreated: Post!
    commentAdded(postId: ID!): Comment!
  }
`;

// Resolvers
const resolvers = {
  Query: {
    users: async (_, { page = 1, limit = 20 }, { dataSources }) => {
      return dataSources.userAPI.getUsers(page, limit);
    },
    user: async (_, { id }, { dataSources }) => {
      return dataSources.userAPI.getUser(id);
    },
    posts: async (_, { published }, { dataSources }) => {
      return dataSources.postAPI.getPosts({ published });
    },
    me: async (_, __, { user, dataSources }) => {
      if (!user) throw new AuthenticationError('Not authenticated');
      return dataSources.userAPI.getUser(user.id);
    }
  },
  
  Mutation: {
    createPost: async (_, { input }, { user, dataSources }) => {
      if (!user) throw new AuthenticationError('Not authenticated');
      return dataSources.postAPI.createPost({ ...input, authorId: user.id });
    },
    deletePost: async (_, { id }, { user, dataSources }) => {
      const post = await dataSources.postAPI.getPost(id);
      if (post.authorId !== user.id && user.role !== 'ADMIN') {
        throw new ForbiddenError('Not authorized');
      }
      return dataSources.postAPI.deletePost(id);
    }
  },
  
  // Field resolvers (resolve nested data)
  User: {
    posts: async (parent, _, { dataSources }) => {
      return dataSources.postAPI.getPostsByAuthor(parent.id);
    }
  },
  
  Post: {
    author: async (parent, _, { loaders }) => {
      // DataLoader batches and caches
      return loaders.userLoader.load(parent.authorId);
    },
    comments: async (parent, _, { dataSources }) => {
      return dataSources.commentAPI.getCommentsByPost(parent.id);
    }
  }
};

// Server setup
const server = new ApolloServer({ typeDefs, resolvers });

await server.start();
app.use('/graphql', express.json(), expressMiddleware(server, {
  context: async ({ req }) => {
    const token = req.headers.authorization?.split(' ')[1];
    const user = token ? verifyToken(token) : null;
    return {
      user,
      dataSources: { userAPI: new UserAPI(), postAPI: new PostAPI() },
      loaders: createLoaders()
    };
  }
}));
```

---

## 🔄 DataLoader (N+1 Solution)

```javascript
const DataLoader = require('dataloader');

function createLoaders() {
  return {
    userLoader: new DataLoader(async (userIds) => {
      // Batch: fetch ALL users in one query
      const users = await User.find({ _id: { $in: userIds } });
      // Must return in same order as input IDs
      const userMap = new Map(users.map(u => [u.id.toString(), u]));
      return userIds.map(id => userMap.get(id.toString()) || null);
    }),
    
    postLoader: new DataLoader(async (postIds) => {
      const posts = await Post.find({ _id: { $in: postIds } });
      const postMap = new Map(posts.map(p => [p.id.toString(), p]));
      return postIds.map(id => postMap.get(id.toString()) || null);
    })
  };
}

// Without DataLoader: 100 posts → 100 separate user queries
// With DataLoader: 100 posts → 1 batch user query (SELECT * WHERE id IN [...])
```

---

## 🔐 Authentication & Authorization

```javascript
const { AuthenticationError, ForbiddenError } = require('apollo-server-express');

// Directive-based authorization
const { mapSchema, getDirective, MapperKind } = require('@graphql-tools/utils');

function authDirective(schema) {
  return mapSchema(schema, {
    [MapperKind.OBJECT_FIELD]: (fieldConfig) => {
      const authDir = getDirective(schema, fieldConfig, 'auth');
      if (authDir) {
        const { requires } = authDir[0];
        const originalResolve = fieldConfig.resolve;
        
        fieldConfig.resolve = async (source, args, context, info) => {
          if (!context.user) throw new AuthenticationError('Not authenticated');
          if (requires && !requires.includes(context.user.role)) {
            throw new ForbiddenError(`Requires role: ${requires.join(', ')}`);
          }
          return originalResolve(source, args, context, info);
        };
      }
      return fieldConfig;
    }
  });
}

// Schema directive usage:
// type Mutation {
//   deleteUser(id: ID!): Boolean! @auth(requires: [ADMIN])
//   updateProfile(input: ProfileInput!): User! @auth
// }
```

---

## ⚡ Performance Optimization

```javascript
// Query complexity limiting
const { createComplexityLimitRule } = require('graphql-validation-complexity');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [createComplexityLimitRule(1000)], // Max complexity score
});

// Query depth limiting
const depthLimit = require('graphql-depth-limit');
const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(5)] // Max 5 levels deep
});

// Persisted queries (prevent arbitrary queries in production)
const server = new ApolloServer({
  typeDefs,
  resolvers,
  persistedQueries: { ttl: 900 } // Cache queries for 15 min
});

// Response caching
const responseCachePlugin = require('@apollo/server-plugin-response-cache');
const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [responseCachePlugin.default()],
});

// Add cache hints in resolvers
const resolvers = {
  Query: {
    posts: async (_, args, { dataSources }, info) => {
      info.cacheControl.setCacheHint({ maxAge: 300 }); // 5 min
      return dataSources.postAPI.getPosts(args);
    }
  }
};
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is GraphQL and how does it differ from REST?**

GraphQL is a query language for APIs where clients specify exactly what data they need. Differences: REST has multiple endpoints, GraphQL has one. REST over/under-fetches, GraphQL returns exactly requested fields. REST uses HTTP verbs for semantics, GraphQL uses Query/Mutation/Subscription types. GraphQL has a type system and introspection.

**Q2: What are resolvers in GraphQL?**

Resolvers are functions that return data for each field in the schema. Query resolvers fetch root data. Field resolvers resolve nested types (e.g., `Post.author` resolves the author for a post). They receive: parent (previous resolver's result), args, context (shared data like auth), and info (query metadata).

**Q3: What is the N+1 problem in GraphQL?**

When querying a list (e.g., 50 posts) with nested fields (e.g., each post's author), the parent resolver runs once (1 query), then the nested resolver runs per item (50 queries) = 51 total queries. Solution: DataLoader batches all nested requests into a single query using the pattern `WHERE id IN (...)`.

### Intermediate

**Q4: How do you handle authentication and authorization in GraphQL?**

Authentication: extract token from headers in context function, attach user to context. Authorization: check `context.user` in resolvers, or use schema directives (`@auth(requires: ADMIN)`). For field-level: resolver checks before returning data. For type-level: filter in resolver. Never expose unauthorized data in errors.

**Q5: Compare GraphQL subscriptions vs WebSockets vs SSE.**

Subscriptions: GraphQL-specific real-time feature, uses WebSocket transport, type-safe, follows GraphQL schema. Raw WebSockets: more flexible, lower overhead, any data format. SSE: server → client only, simpler. Use subscriptions when your app already uses GraphQL and needs type-safe real-time. Use raw WS for custom protocols.

**Q6: How do you prevent abuse of deeply nested GraphQL queries?**

(1) Query depth limiting (reject queries > N levels deep). (2) Query complexity analysis (assign cost per field, reject if total exceeds limit). (3) Persisted queries (only allow pre-approved queries in production). (4) Timeout per query. (5) Rate limiting per user/IP. Essential because one query can be arbitrarily expensive.

### Advanced

**Q7: How would you implement a federated GraphQL architecture?**

Apollo Federation: each service defines a subgraph (partial schema with `@key` directives). A gateway (Apollo Router) composes subgraphs into a unified supergraph. Services reference external types with `extend type`. Gateway handles query planning — splits queries across services. Benefits: team independence, per-service scaling.

**Q8: Compare code-first vs schema-first GraphQL development.**

Schema-first: write `.graphql` files, generate resolvers. Pros: design-first, readable, tooling (IDE support). Cons: duplication between schema and types. Code-first (Nexus, TypeGraphQL): generate schema from code. Pros: type-safety, no duplication, easier refactoring. Cons: schema harder to read for non-developers. Schema-first is more common in teams.

**Q9: How do you handle file uploads and large mutations in GraphQL?**

File uploads: multipart request spec (graphql-upload), or pre-signed URL pattern (get URL via mutation, upload directly to S3, confirm via second mutation). Large mutations: separate into smaller mutations, use input types with validation. Batch mutations: custom batch resolver or DataLoader for writes. Always validate and sanitize inputs server-side.

---

## 🛠️ Hands-on Exercise

Build a complete GraphQL API:
1. Schema with Users, Posts, Comments (relations)
2. DataLoader for N+1 prevention
3. Authentication via context
4. Role-based authorization
5. Pagination (cursor-based)
6. Query depth and complexity limiting
