# Day 3-4: Flutter Architecture Basics

## 📋 Topics Covered
- Flutter Engine & Skia
- Widget Tree
- Element Tree  
- Render Tree
- Everything is a Widget
- BuildContext
- Widget Lifecycle

---

## 🏗️ Part 1: Flutter Architecture Overview

### Flutter Layers

```
┌─────────────────────────────────────┐
│     Dart Framework (Material/      │
│        Cupertino Widgets)           │
├─────────────────────────────────────┤
│     Rendering Layer (RenderObject)  │
├─────────────────────────────────────┤
│     Widgets Layer                   │
├─────────────────────────────────────┤
│     Foundation Layer                │
├─────────────────────────────────────┤
│     Flutter Engine (C++)            │
├─────────────────────────────────────┤
│     Skia (Graphics Rendering)       │
├─────────────────────────────────────┤
│     Platform (Android/iOS/Web)      │
└─────────────────────────────────────┘
```

### What is Flutter Engine?

Flutter Engine is written in C++ and provides:
- **Low-level rendering** using Skia graphics library
- **Dart runtime** for executing Dart code
- **Platform channels** for native communication
- **Text layout** and font rendering
- **Accessibility** support
- **Plugin architecture**

### Skia Graphics

```dart
// Skia is used under the hood for rendering
// When you write this Flutter code:
Container(
  width: 100,
  height: 100,
  decoration: BoxDecoration(
    color: Colors.blue,
    borderRadius: BorderRadius.circular(10),
  ),
)

// Flutter converts it to Skia drawing commands:
// 1. Create rounded rectangle path
// 2. Set blue color
// 3. Draw to canvas
// This happens at 60fps (or 120fps on some devices)
```

---

## 🌳 Part 2: The Three Trees

### Understanding Widget, Element, and RenderObject Trees

```dart
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Three Trees Demo')),
        body: ThreeTreesDemo(),
      ),
    );
  }
}

class ThreeTreesDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // WIDGET TREE (Configuration)
    //   ThreeTreesDemo
    //   └── Container
    //       └── Text
    
    // ELEMENT TREE (Lifecycle Management)
    //   StatelessElement (ThreeTreesDemo)
    //   └── SingleChildElement (Container)
    //       └── StatelessElement (Text)
    
    // RENDER TREE (Layout & Paint)
    //   RenderDecoratedBox
    //   └── RenderParagraph
    
    return Container(
      padding: EdgeInsets.all(16),
      color: Colors.blue[50],
      child: Text(
        'Widget creates Element, Element creates RenderObject',
        style: TextStyle(fontSize: 18),
      ),
    );
  }
}
```

### Deep Dive: The Three Trees

```dart
// 1. WIDGET TREE - Immutable Configuration
class MyWidget extends StatelessWidget {
  final String title;
  
  const MyWidget({required this.title});
  
  @override
  Widget build(BuildContext context) {
    // Widgets are rebuilt frequently
    // They are cheap to create
    return Text(title);
  }
}

// 2. ELEMENT TREE - Mutable, Long-lived
// Element manages the lifecycle
// Maps Widget to RenderObject
// Manages state location
// Element.widget points to current widget
// Element.renderObject points to render object

// 3. RENDER TREE - Handles Layout and Painting
// RenderObject:
// - Performs layout
// - Handles painting
// - Hit testing
// - Expensive to create
```

### Widget Lifecycle Visualization

```dart
import 'package:flutter/material.dart';

class LifecycleDemo extends StatefulWidget {
  @override
  _LifecycleDemoState createState() {
    print('1. createState() called');
    return _LifecycleDemoState();
  }
}

class _LifecycleDemoState extends State<LifecycleDemo> {
  int counter = 0;
  
  // Called once when State object created
  @override
  void initState() {
    super.initState();
    print('2. initState() called');
  }
  
  // Called when dependencies change (InheritedWidget)
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    print('3. didChangeDependencies() called');
  }
  
  // Called every time widget rebuilds
  @override
  Widget build(BuildContext context) {
    print('4. build() called');
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('Counter: $counter'),
        ElevatedButton(
          onPressed: () {
            setState(() {
              counter++;
              print('5. setState() called - triggers rebuild');
            });
          },
          child: Text('Increment'),
        ),
      ],
    );
  }
  
  // Called when widget configuration changes
  @override
  void didUpdateWidget(LifecycleDemo oldWidget) {
    super.didUpdateWidget(oldWidget);
    print('6. didUpdateWidget() called');
  }
  
  // Called when widget removed temporarily
  @override
  void deactivate() {
    super.deactivate();
    print('7. deactivate() called');
  }
  
  // Called when widget removed permanently
  @override
  void dispose() {
    print('8. dispose() called');
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    print('build() called - Counter: $counter');
    return Column(
      children: [
        Text('Counter: $counter'),
        ElevatedButton(
          onPressed: () => setState(() => counter++),
          child: Text('Increment'),
        ),
      ],
    );
  }
}
```

---

## 🧩 Part 3: Everything is a Widget

### Widget Types

```dart
import 'package:flutter/material.dart';

// 1. STATELESS WIDGET - Immutable
class WelcomeWidget extends StatelessWidget {
  final String name;
  
  const WelcomeWidget({required this.name});
  
  @override
  Widget build(BuildContext context) {
    return Text('Welcome, $name!');
  }
}

// 2. STATEFUL WIDGET - Mutable State
class CounterWidget extends StatefulWidget {
  @override
  _CounterWidgetState createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _count = 0;
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_count'),
        ElevatedButton(
          onPressed: () => setState(() => _count++),
          child: Text('Increment'),
        ),
      ],
    );
  }
}

// 3. INHERITED WIDGET - Share Data Down the Tree
class ThemeData {
  final Color primaryColor;
  final double fontSize;
  
  ThemeData({required this.primaryColor, required this.fontSize});
}

class MyTheme extends InheritedWidget {
  final ThemeData theme;
  
  MyTheme({
    required this.theme,
    required Widget child,
  }) : super(child: child);
  
  static MyTheme? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<MyTheme>();
  }
  
  @override
  bool updateShouldNotify(MyTheme oldWidget) {
    return theme != oldWidget.theme;
  }
}

// Using InheritedWidget
class ThemedText extends StatelessWidget {
  final String text;
  
  const ThemedText(this.text);
  
  @override
  Widget build(BuildContext context) {
    final theme = MyTheme.of(context)?.theme;
    
    return Text(
      text,
      style: TextStyle(
        color: theme?.primaryColor,
        fontSize: theme?.fontSize,
      ),
    );
  }
}
```

### BuildContext Explained

```dart
import 'package:flutter/material.dart';

class BuildContextDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // BuildContext is a handle to the location of a widget in the tree
    // It's actually the Element itself!
    
    // Common uses of BuildContext:
    
    // 1. Get theme data
    final theme = Theme.of(context);
    final primaryColor = theme.primaryColor;
    
    // 2. Get media query (screen size)
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    
    // 3. Navigate
    // Navigator.of(context).push(...);
    
    // 4. Show dialogs/snackbars
    // ScaffoldMessenger.of(context).showSnackBar(...);
    
    // 5. Access InheritedWidgets
    final myTheme = MyTheme.of(context);
    
    return Container(
      width: screenWidth * 0.8,
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: primaryColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text('Screen Width: ${screenWidth.toStringAsFixed(0)}'),
          Text('Screen Height: ${screenHeight.toStringAsFixed(0)}'),
          Text('Primary Color: $primaryColor'),
        ],
      ),
    );
  }
}

// IMPORTANT: Context of Current Widget vs Parent
class ContextScaffoldExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Context Demo')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            // ❌ This will fail! Context doesn't have Scaffold ancestor
            // ScaffoldMessenger.of(context).showSnackBar(
            //   SnackBar(content: Text('Hello')),
            // );
          },
          child: Text('Show Snackbar (Fails)'),
        ),
      ),
    );
  }
}

// FIX: Use Builder to get correct context
class ContextFixExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Context Demo')),
      body: Builder(
        builder: (BuildContext scaffoldContext) {
          // ✅ Now scaffoldContext has Scaffold ancestor
          return Center(
            child: ElevatedButton(
              onPressed: () {
                ScaffoldMessenger.of(scaffoldContext).showSnackBar(
                  SnackBar(content: Text('Hello!')),
                );
              },
              child: Text('Show Snackbar (Works)'),
            ),
          );
        },
      ),
    );
  }
}
```

---

## 🎨 Part 4: Building the Counter App (Modified)

### Enhanced Counter with Architecture Understanding

```dart
import 'package:flutter/material.dart';

void main() {
  runApp(EnhancedCounterApp());
}

class EnhancedCounterApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Enhanced Counter',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: CounterHomePage(),
    );
  }
}

class CounterHomePage extends StatefulWidget {
  @override
  _CounterHomePageState createState() => _CounterHomePageState();
}

class _CounterHomePageState extends State<CounterHomePage> {
  int _counter = 0;
  List<int> _history = [];
  
  void _incrementCounter() {
    setState(() {
      _counter++;
      _history.add(_counter);
    });
  }
  
  void _decrementCounter() {
    setState(() {
      if (_counter > 0) {
        _counter--;
        _history.add(_counter);
      }
    });
  }
  
  void _resetCounter() {
    setState(() {
      _counter = 0;
      _history.clear();
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Enhanced Counter'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _resetCounter,
            tooltip: 'Reset',
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Current Count:',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.displayLarge?.copyWith(
                color: _counter > 10 ? Colors.green : Colors.blue,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 30),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CustomButton(
                  icon: Icons.remove,
                  onPressed: _decrementCounter,
                  color: Colors.red,
                  label: 'Decrement',
                ),
                SizedBox(width: 20),
                CustomButton(
                  icon: Icons.add,
                  onPressed: _incrementCounter,
                  color: Colors.green,
                  label: 'Increment',
                ),
              ],
            ),
            SizedBox(height: 30),
            CounterStats(counter: _counter, history: _history),
          ],
        ),
      ),
    );
  }
}

// Custom Widget - Reusable Button
class CustomButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;
  final Color color;
  final String label;
  
  const CustomButton({
    required this.icon,
    required this.onPressed,
    required this.color,
    required this.label,
  });
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        FloatingActionButton(
          onPressed: onPressed,
          backgroundColor: color,
          child: Icon(icon),
        ),
        SizedBox(height: 8),
        Text(label, style: TextStyle(fontSize: 12)),
      ],
    );
  }
}

// Custom Widget - Stats Display
class CounterStats extends StatelessWidget {
  final int counter;
  final List<int> history;
  
  const CounterStats({
    required this.counter,
    required this.history,
  });
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      margin: EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(
            'Statistics',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              StatItem(label: 'Current', value: '$counter'),
              StatItem(label: 'Changes', value: '${history.length}'),
              StatItem(
                label: 'Average',
                value: history.isEmpty
                    ? '0'
                    : (history.reduce((a, b) => a + b) / history.length)
                        .toStringAsFixed(1),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class StatItem extends StatelessWidget {
  final String label;
  final String value;
  
  const StatItem({required this.label, required this.value});
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.blue,
          ),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }
}
```

---

## 🔍 Part 5: Widget Inspector & DevTools

### How to Use Flutter DevTools

```bash
# Run your app
flutter run

# Open DevTools in browser
# Press 'w' in terminal or use:
flutter pub global activate devtools
flutter pub global run devtools

# Features to explore:
# 1. Widget Inspector - See widget tree
# 2. Timeline - Performance profiling
# 3. Memory - Memory usage
# 4. Network - Network calls
# 5. Logging - Debug logs
```

### Debug Painting

```dart
import 'package:flutter/rendering.dart';

void main() {
  // Enable debug painting
  debugPaintSizeEnabled = true; // Shows layout boundaries
  debugPaintBaselinesEnabled = true; // Shows text baselines
  debugPaintPointersEnabled = true; // Shows tap targets
  
  runApp(MyApp());
}
```

---

## 🎯 Practice Exercises

### Exercise 1: Create Custom Widgets

```dart
// Create a ProfileCard widget that displays:
// - Avatar (CircleAvatar)
// - Name and email
// - Follow button
// Make it reusable with parameters

class ProfileCard extends StatelessWidget {
  final String name;
  final String email;
  final String imageUrl;
  final VoidCallback onFollow;
  
  const ProfileCard({
    required this.name,
    required this.email,
    required this.imageUrl,
    required this.onFollow,
  });
  
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.all(16),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              radius: 30,
              backgroundImage: NetworkImage(imageUrl),
            ),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    email,
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            ElevatedButton(
              onPressed: onFollow,
              child: Text('Follow'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Exercise 2: Understand Widget Lifecycle

```dart
// Create a widget that:
// 1. Fetches data in initState
// 2. Updates when data changes
// 3. Cleans up in dispose

class DataWidget extends StatefulWidget {
  final String dataId;
  
  const DataWidget({required this.dataId});
  
  @override
  _DataWidgetState createState() => _DataWidgetState();
}

class _DataWidgetState extends State<DataWidget> {
  String? data;
  bool isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  @override
  void didUpdateWidget(DataWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.dataId != widget.dataId) {
      _loadData();
    }
  }
  
  Future<void> _loadData() async {
    setState(() => isLoading = true);
    
    // Simulate API call
    await Future.delayed(Duration(seconds: 2));
    
    setState(() {
      data = 'Data for ${widget.dataId}';
      isLoading = false;
    });
  }
  
  @override
  void dispose() {
    // Clean up resources
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return CircularProgressIndicator();
    }
    
    return Text(data ?? 'No data');
  }
}
```

---

## 📌 Key Takeaways

1. **Flutter Engine** uses Skia for high-performance graphics rendering
2. **Three Trees**: Widget (config) → Element (lifecycle) → RenderObject (layout/paint)
3. **Widgets are immutable** - state changes create new widget instances
4. **BuildContext** is your handle to the widget's location in the tree
5. **Stateless** for static, **Stateful** for dynamic widgets
6. Widget lifecycle: `initState` → `build` → `setState` → `dispose`

---

## 🔗 Next Steps

Continue to [Day 5-6: Layout System](./day-5-6-layouts.md)

---

## 📚 Additional Resources

- [Flutter Architecture Overview](https://flutter.dev/docs/resources/architectural-overview)
- [Widget, Element, and RenderObject](https://api.flutter.dev/flutter/widgets/Widget-class.html)
- [BuildContext Deep Dive](https://api.flutter.dev/flutter/widgets/BuildContext-class.html)
