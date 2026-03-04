# Flutter Quick Start - AI Chat App (3-4 Days)

## Why Flutter?
- Build iOS + Android from one codebase
- Fast development with hot reload
- Great for building an AI chat mobile app
- Shows full-stack completeness on your resume

---

## 1. Setup (Day 1)

```bash
# Install Flutter (Linux)
sudo snap install flutter --classic
flutter doctor

# Create project
flutter create ai_chat_app
cd ai_chat_app
```

### Project Structure
```
ai_chat_app/
├── lib/
│   ├── main.dart              # Entry point
│   ├── models/
│   │   └── message.dart       # Data models
│   ├── services/
│   │   └── api_service.dart   # Flask API client
│   ├── screens/
│   │   ├── chat_screen.dart   # Main chat UI
│   │   └── settings_screen.dart
│   └── widgets/
│       ├── message_bubble.dart
│       └── typing_indicator.dart
├── pubspec.yaml               # Dependencies (like package.json)
└── ...
```

## 2. Flutter vs React (Quick Comparison)

| Concept | React | Flutter |
|---------|-------|---------|
| Language | JavaScript/TypeScript | Dart |
| Component | Function/Class | Widget |
| State | useState/Redux | setState/Provider |
| Styling | CSS/Tailwind | Widget properties |
| Layout | Flexbox | Row/Column/Stack |
| Navigation | React Router | Navigator |
| HTTP | fetch/axios | http/dio |
| Build | npm build | flutter build |

## 3. Dart Basics (Familiar from TypeScript)

```dart
// Variables (like TypeScript)
String name = "Bharath";
int age = 30;
double score = 95.5;
bool isActive = true;
var inferred = "I'm a string";  // Type inferred

// Null safety (like TypeScript strict mode)
String? nullableName;  // Can be null
String nonNullName = "Required";  // Cannot be null

// Functions
String greet(String name, {int? age}) {
  return "Hello $name${age != null ? ', age $age' : ''}";
}

// Classes
class User {
  final String name;
  final String role;
  
  User({required this.name, this.role = "user"});
  
  @override
  String toString() => "User($name, $role)";
}

// Async/await (exactly like JS!)
Future<String> fetchData() async {
  await Future.delayed(Duration(seconds: 1));
  return "Data loaded";
}

// Lists, maps (like arrays, objects)
List<String> skills = ["Flutter", "React", "Python"];
Map<String, dynamic> config = {"model": "gpt-4", "temp": 0.7};

// String interpolation
print("Name: $name, Skills: ${skills.length}");
```

## 4. Main App (Day 1-2)

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'screens/chat_screen.dart';

void main() {
  runApp(const AIChartApp());
}

class AIChartApp extends StatelessWidget {
  const AIChartApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Chat',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      darkTheme: ThemeData.dark(useMaterial3: true),
      home: const ChatScreen(),
    );
  }
}
```

### Message Model
```dart
// lib/models/message.dart
class Message {
  final String id;
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final List<Source>? sources;

  Message({
    required this.id,
    required this.content,
    required this.isUser,
    DateTime? timestamp,
    this.sources,
  }) : timestamp = timestamp ?? DateTime.now();

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      content: json['content'],
      isUser: json['is_user'] ?? false,
      sources: json['sources'] != null
          ? (json['sources'] as List).map((s) => Source.fromJson(s)).toList()
          : null,
    );
  }
}

class Source {
  final String document;
  final double score;
  final String preview;

  Source({required this.document, required this.score, required this.preview});

  factory Source.fromJson(Map<String, dynamic> json) {
    return Source(
      document: json['document'] ?? '',
      score: (json['score'] ?? 0).toDouble(),
      preview: json['preview'] ?? '',
    );
  }
}
```

### API Service
```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/message.dart';

class ApiService {
  // Change to your Flask API URL
  static const String baseUrl = 'http://10.0.2.2:5000/api'; // Android emulator
  // static const String baseUrl = 'http://localhost:5000/api'; // iOS/web

  static Future<Map<String, dynamic>> query(String question) async {
    final response = await http.post(
      Uri.parse('$baseUrl/query'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'question': question, 'top_k': 5}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get response: ${response.statusCode}');
    }
  }

  static Future<bool> healthCheck() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
```

### Chat Screen (Day 2-3)
```dart
// lib/screens/chat_screen.dart
import 'package:flutter/material.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import '../widgets/message_bubble.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Message> _messages = [];
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add(Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: text,
        isUser: true,
      ));
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    try {
      final response = await ApiService.query(text);
      
      setState(() {
        _messages.add(Message(
          id: '${DateTime.now().millisecondsSinceEpoch}_ai',
          content: response['answer'] ?? 'No response',
          isUser: false,
          sources: response['sources'] != null
              ? (response['sources'] as List)
                  .map((s) => Source.fromJson(s))
                  .toList()
              : null,
        ));
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(Message(
          id: '${DateTime.now().millisecondsSinceEpoch}_error',
          content: 'Error: ${e.toString()}',
          isUser: false,
        ));
        _isLoading = false;
      });
    }
    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Knowledge Assistant'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: () => setState(() => _messages.clear()),
          ),
        ],
      ),
      body: Column(
        children: [
          // Messages list
          Expanded(
            child: _messages.isEmpty
                ? const Center(
                    child: Text('Ask me anything!',
                        style: TextStyle(fontSize: 18, color: Colors.grey)),
                  )
                : ListView.builder(
                    controller: _scrollController,
                    itemCount: _messages.length,
                    padding: const EdgeInsets.all(16),
                    itemBuilder: (context, index) {
                      return MessageBubble(message: _messages[index]);
                    },
                  ),
          ),
          
          // Loading indicator
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: Row(
                children: [
                  SizedBox(width: 16),
                  SizedBox(
                    width: 20, height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 8),
                  Text('Thinking...', style: TextStyle(color: Colors.grey)),
                ],
              ),
            ),
          
          // Input field
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              boxShadow: [
                BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, -2)),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Ask a question...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                    textInputAction: TextInputAction.send,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  icon: const Icon(Icons.send),
                  color: Theme.of(context).primaryColor,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

### Message Bubble Widget
```dart
// lib/widgets/message_bubble.dart
import 'package:flutter/material.dart';
import '../models/message.dart';

class MessageBubble extends StatelessWidget {
  final Message message;

  const MessageBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: isUser
              ? Theme.of(context).primaryColor
              : Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16).copyWith(
            bottomRight: isUser ? const Radius.circular(0) : null,
            bottomLeft: !isUser ? const Radius.circular(0) : null,
          ),
          boxShadow: [
            BoxShadow(color: Colors.black12, blurRadius: 2, offset: Offset(0, 1)),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.content,
              style: TextStyle(
                color: isUser ? Colors.white : null,
                fontSize: 15,
              ),
            ),
            // Show sources for AI responses
            if (!isUser && message.sources != null && message.sources!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Divider(),
                    Text('Sources:', style: TextStyle(
                      fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey[600],
                    )),
                    ...message.sources!.map((s) => Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        '• ${s.document} (${(s.score * 100).toStringAsFixed(0)}%)',
                        style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                      ),
                    )),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
```

### pubspec.yaml dependencies
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.0.0
```

## 5. Run the App

```bash
# Run on connected device/emulator
flutter run

# Run on Chrome (web)
flutter run -d chrome

# Build APK
flutter build apk

# Build for iOS
flutter build ios
```

---

## Key Takeaways
1. Flutter uses **Dart** (very similar to TypeScript)
2. Everything is a **Widget** (like components)
3. **StatefulWidget** = component with state (like useState)
4. HTTP calls use **http** package (like fetch)
5. 3-4 days is enough for a functional chat app
6. Shows **full-stack completeness** on resume
