# Day 5-6: Layout System

## 📋 Topics Covered
- Container Widget
- Row & Column
- Stack & Positioned
- Expanded & Flexible
- MediaQuery
- SafeArea
- Responsive Design
- Constraints

---

## 📐 Part 1: Understanding Flutter Layout

### The Layout Rule

**Constraints go down. Sizes go up. Parent sets position.**

```dart
// Every widget gets constraints from parent:
// - Minimum width/height
// - Maximum width/height

// Widget returns its size to parent (within constraints)
// Parent positions the widget
```

### Container - The Swiss Army Knife

```dart
import 'package:flutter/material.dart';

class ContainerDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Container Demo')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Basic Container
            Container(
              width: 200,
              height: 100,
              color: Colors.blue,
              child: Center(child: Text('Basic Container')),
            ),
            
            SizedBox(height: 20),
            
            // Container with Decoration
            Container(
              width: 200,
              height: 100,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.purple, Colors.blue],
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black26,
                    blurRadius: 10,
                    offset: Offset(0, 5),
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  'Gradient Container',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ),
            
            SizedBox(height: 20),
            
            // Container with Margin and Padding
            Container(
              margin: EdgeInsets.all(16),
              padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.green[100],
                border: Border.all(color: Colors.green, width: 2),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text('Margin & Padding'),
            ),
            
            SizedBox(height: 20),
            
            // Constrained Container
            Container(
              constraints: BoxConstraints(
                minWidth: 100,
                maxWidth: 300,
                minHeight: 50,
                maxHeight: 150,
              ),
              decoration: BoxDecoration(
                color: Colors.orange[100],
                border: Border.all(color: Colors.orange),
              ),
              child: Text('This container has size constraints'),
            ),
            
            SizedBox(height: 20),
            
            // Transform Container
            Container(
              width: 150,
              height: 150,
              transform: Matrix4.rotationZ(0.1),
              decoration: BoxDecoration(
                color: Colors.red,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Center(
                child: Text(
                  'Rotated',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 📊 Part 2: Row & Column Layouts

### Row - Horizontal Layout

```dart
class RowDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Row Demo')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Basic Row
            Text('Basic Row:', style: TextStyle(fontWeight: FontWeight.bold)),
            Row(
              children: [
                Container(width: 50, height: 50, color: Colors.red),
                Container(width: 50, height: 50, color: Colors.green),
                Container(width: 50, height: 50, color: Colors.blue),
              ],
            ),
            
            SizedBox(height: 20),
            
            // MainAxisAlignment
            Text('MainAxisAlignment - Center:', 
                 style: TextStyle(fontWeight: FontWeight.bold)),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildBox(Colors.red),
                _buildBox(Colors.green),
                _buildBox(Colors.blue),
              ],
            ),
            
            SizedBox(height: 20),
            
            Text('MainAxisAlignment - SpaceBetween:', 
                 style: TextStyle(fontWeight: FontWeight.bold)),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildBox(Colors.red),
                _buildBox(Colors.green),
                _buildBox(Colors.blue),
              ],
            ),
            
            SizedBox(height: 20),
            
            Text('MainAxisAlignment - SpaceAround:', 
                 style: TextStyle(fontWeight: FontWeight.bold)),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildBox(Colors.red),
                _buildBox(Colors.green),
                _buildBox(Colors.blue),
              ],
            ),
            
            SizedBox(height: 20),
            
            // CrossAxisAlignment
            Text('CrossAxisAlignment - Start:', 
                 style: TextStyle(fontWeight: FontWeight.bold)),
            Container(
              height: 100,
              color: Colors.grey[200],
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildBox(Colors.red),
                  _buildBox(Colors.green, height: 70),
                  _buildBox(Colors.blue),
                ],
              ),
            ),
            
            SizedBox(height: 20),
            
            Text('CrossAxisAlignment - Center:', 
                 style: TextStyle(fontWeight: FontWeight.bold)),
            Container(
              height: 100,
              color: Colors.grey[200],
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  _buildBox(Colors.red),
                  _buildBox(Colors.green, height: 70),
                  _buildBox(Colors.blue),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildBox(Color color, {double height = 50}) {
    return Container(
      width: 50,
      height: height,
      color: color,
      margin: EdgeInsets.all(4),
    );
  }
}
```

### Column - Vertical Layout

```dart
class ColumnDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Column Demo')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            // Column 1
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  Text('Start'),
                  _buildBox(Colors.red),
                  _buildBox(Colors.green),
                  _buildBox(Colors.blue),
                ],
              ),
            ),
            
            // Column 2
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Center'),
                  _buildBox(Colors.red),
                  _buildBox(Colors.green),
                  _buildBox(Colors.blue),
                ],
              ),
            ),
            
            // Column 3
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('SpaceBetween'),
                  _buildBox(Colors.red),
                  _buildBox(Colors.green),
                  _buildBox(Colors.blue),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildBox(Color color) {
    return Container(
      width: 50,
      height: 50,
      color: color,
      margin: EdgeInsets.symmetric(vertical: 4),
    );
  }
}
```

---

## 📚 Part 3: Stack & Positioned

### Stack - Overlapping Widgets

```dart
class StackDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Stack Demo')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Basic Stack
            Container(
              height: 200,
              child: Stack(
                children: [
                  Container(
                    width: 200,
                    height: 200,
                    color: Colors.blue,
                  ),
                  Container(
                    width: 150,
                    height: 150,
                    color: Colors.green,
                  ),
                  Container(
                    width: 100,
                    height: 100,
                    color: Colors.red,
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 20),
            
            // Positioned Widgets
            Text('Positioned Widgets:', 
                 style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 10),
            Container(
              height: 200,
              child: Stack(
                children: [
                  // Background
                  Container(color: Colors.grey[200]),
                  
                  // Top Left
                  Positioned(
                    top: 10,
                    left: 10,
                    child: _buildPositionedBox('Top Left', Colors.red),
                  ),
                  
                  // Top Right
                  Positioned(
                    top: 10,
                    right: 10,
                    child: _buildPositionedBox('Top Right', Colors.green),
                  ),
                  
                  // Bottom Left
                  Positioned(
                    bottom: 10,
                    left: 10,
                    child: _buildPositionedBox('Bottom Left', Colors.blue),
                  ),
                  
                  // Bottom Right
                  Positioned(
                    bottom: 10,
                    right: 10,
                    child: _buildPositionedBox('Bottom Right', Colors.orange),
                  ),
                  
                  // Center
                  Positioned.fill(
                    child: Align(
                      alignment: Alignment.center,
                      child: _buildPositionedBox('Center', Colors.purple),
                    ),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 20),
            
            // Profile Card with Stack
            ProfileCardWithStack(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildPositionedBox(String text, Color color) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        text,
        style: TextStyle(color: Colors.white, fontSize: 12),
      ),
    );
  }
}

// Practical Example: Profile Card
class ProfileCardWithStack extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 250,
      child: Stack(
        children: [
          // Cover Image
          Container(
            height: 150,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.blue, Colors.purple],
              ),
            ),
          ),
          
          // Profile Image
          Positioned(
            top: 100,
            left: 20,
            child: Container(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 4),
              ),
              child: CircleAvatar(
                radius: 50,
                backgroundImage: NetworkImage(
                  'https://via.placeholder.com/150',
                ),
              ),
            ),
          ),
          
          // Edit Button
          Positioned(
            top: 110,
            right: 20,
            child: ElevatedButton.icon(
              onPressed: () {},
              icon: Icon(Icons.edit, size: 16),
              label: Text('Edit'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.blue,
              ),
            ),
          ),
          
          // Name and Bio
          Positioned(
            top: 200,
            left: 20,
            right: 20,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'John Doe',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Flutter Developer',
                  style: TextStyle(color: Colors.grey[600]),
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

---

## 🔄 Part 4: Expanded & Flexible

### Expanded - Fill Available Space

```dart
class ExpandedDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Expanded Demo')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Without Expanded
            Text('Without Expanded:'),
            Row(
              children: [
                Container(width: 100, height: 50, color: Colors.red),
                Container(width: 100, height: 50, color: Colors.green),
                Container(width: 100, height: 50, color: Colors.blue),
              ],
            ),
            
            SizedBox(height: 20),
            
            // With Expanded
            Text('With Expanded (Equal distribution):'),
            Row(
              children: [
                Expanded(
                  child: Container(height: 50, color: Colors.red),
                ),
                Expanded(
                  child: Container(height: 50, color: Colors.green),
                ),
                Expanded(
                  child: Container(height: 50, color: Colors.blue),
                ),
              ],
            ),
            
            SizedBox(height: 20),
            
            // With Flex Factor
            Text('With Flex Factor (1:2:3):'),
            Row(
              children: [
                Expanded(
                  flex: 1,
                  child: Container(
                    height: 50,
                    color: Colors.red,
                    child: Center(child: Text('1')),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Container(
                    height: 50,
                    color: Colors.green,
                    child: Center(child: Text('2')),
                  ),
                ),
                Expanded(
                  flex: 3,
                  child: Container(
                    height: 50,
                    color: Colors.blue,
                    child: Center(child: Text('3')),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 20),
            
            // Mixed: Fixed + Expanded
            Text('Mixed (Fixed + Expanded):'),
            Row(
              children: [
                Container(width: 80, height: 50, color: Colors.red),
                Expanded(
                  child: Container(
                    height: 50,
                    color: Colors.green,
                    child: Center(child: Text('Flexible')),
                  ),
                ),
                Container(width: 80, height: 50, color: Colors.blue),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

### Flexible - Soft Constraint

```dart
class FlexibleDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Flexible Demo')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Expanded vs Flexible
            Text('Expanded (Must fill):'),
            Row(
              children: [
                Expanded(
                  child: Container(
                    height: 50,
                    color: Colors.red,
                    child: Text('Expanded fills all available space'),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 20),
            
            Text('Flexible (Can shrink):'),
            Row(
              children: [
                Flexible(
                  child: Container(
                    height: 50,
                    color: Colors.green,
                    child: Text('Flexible: takes needed space but can shrink'),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 20),
            
            // Practical Example
            Text('Chat Message Layout:'),
            ChatMessageLayout(),
          ],
        ),
      ),
    );
  }
}

class ChatMessageLayout extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          // Avatar (fixed size)
          CircleAvatar(
            radius: 20,
            backgroundImage: NetworkImage('https://via.placeholder.com/40'),
          ),
          SizedBox(width: 8),
          
          // Message (flexible)
          Flexible(
            child: Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'This is a flexible message that adapts to content length',
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ),
          SizedBox(width: 8),
          
          // Timestamp (fixed size)
          Text(
            '12:30',
            style: TextStyle(fontSize: 12, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}
```

---

## 📱 Part 5: MediaQuery & Responsive Design

### MediaQuery - Screen Information

```dart
class MediaQueryDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final padding = MediaQuery.of(context).padding;
    final orientation = MediaQuery.of(context).orientation;
    final devicePixelRatio = MediaQuery.of(context).devicePixelRatio;
    
    return Scaffold(
      appBar: AppBar(title: Text('MediaQuery Demo')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoRow('Screen Width', '${size.width.toStringAsFixed(0)} px'),
            _buildInfoRow('Screen Height', '${size.height.toStringAsFixed(0)} px'),
            _buildInfoRow('Top Padding', '${padding.top.toStringAsFixed(0)} px'),
            _buildInfoRow('Bottom Padding', '${padding.bottom.toStringAsFixed(0)} px'),
            _buildInfoRow('Orientation', orientation.toString()),
            _buildInfoRow('Pixel Ratio', devicePixelRatio.toString()),
            
            SizedBox(height: 20),
            
            // Responsive Container
            Container(
              width: size.width * 0.9, // 90% of screen width
              height: size.width * 0.5, // 50% of screen width (keeps aspect ratio)
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Center(
                child: Text(
                  'Responsive Container\n90% width, 50% width height',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: FontWeight.bold)),
          Text(value),
        ],
      ),
    );
  }
}
```

### Responsive Design Patterns

```dart
class ResponsiveLayout extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Responsive Layout')),
      body: LayoutBuilder(
        builder: (context, constraints) {
          // Use LayoutBuilder for dynamic layouts
          if (constraints.maxWidth > 600) {
            return _buildTabletLayout();
          } else {
            return _buildMobileLayout();
          }
        },
      ),
    );
  }
  
  Widget _buildMobileLayout() {
    return ListView(
      padding: EdgeInsets.all(16),
      children: [
        _buildCard('Item 1'),
        _buildCard('Item 2'),
        _buildCard('Item 3'),
        _buildCard('Item 4'),
      ],
    );
  }
  
  Widget _buildTabletLayout() {
    return GridView.count(
      crossAxisCount: 2,
      padding: EdgeInsets.all(16),
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      children: [
        _buildCard('Item 1'),
        _buildCard('Item 2'),
        _buildCard('Item 3'),
        _buildCard('Item 4'),
      ],
    );
  }
  
  Widget _buildCard(String title) {
    return Card(
      child: Container(
        height: 150,
        child: Center(
          child: Text(
            title,
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }
}

// Responsive helper class
class Responsive {
  static bool isMobile(BuildContext context) =>
      MediaQuery.of(context).size.width < 600;
  
  static bool isTablet(BuildContext context) =>
      MediaQuery.of(context).size.width >= 600 &&
      MediaQuery.of(context).size.width < 1200;
  
  static bool isDesktop(BuildContext context) =>
      MediaQuery.of(context).size.width >= 1200;
  
  static double width(BuildContext context) =>
      MediaQuery.of(context).size.width;
  
  static double height(BuildContext context) =>
      MediaQuery.of(context).size.height;
}
```

---

## 🛡️ Part 6: SafeArea

### SafeArea - Avoid System UI

```dart
class SafeAreaDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Without SafeArea
          Expanded(
            child: Container(
              color: Colors.red,
              child: Center(
                child: Text(
                  'Without SafeArea\n(May go under notch/status bar)',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ),
          ),
          
          // With SafeArea
          Expanded(
            child: SafeArea(
              child: Container(
                color: Colors.green,
                child: Center(
                  child: Text(
                    'With SafeArea\n(Safe from system UI)',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.white),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## 🎨 Practice Project: Login UI

```dart
import 'package:flutter/material.dart';

void main() => runApp(MaterialApp(home: LoginScreen()));

class LoginScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(height: size.height * 0.1),
              
              // Logo
              Icon(
                Icons.flutter_dash,
                size: 80,
                color: Colors.blue,
              ),
              
              SizedBox(height: 20),
              
              // Title
              Text(
                'Welcome Back!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              
              Text(
                'Sign in to continue',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
              
              SizedBox(height: 40),
              
              // Email Field
              TextField(
                decoration: InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Icons.email),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
              
              SizedBox(height: 16),
              
              // Password Field
              TextField(
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Password',
                  prefixIcon: Icon(Icons.lock),
                  suffixIcon: Icon(Icons.visibility_off),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
              
              SizedBox(height: 8),
              
              // Forgot Password
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () {},
                  child: Text('Forgot Password?'),
                ),
              ),
              
              SizedBox(height: 24),
              
              // Login Button
              ElevatedButton(
                onPressed: () {},
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                child: Text(
                  'LOGIN',
                  style: TextStyle(fontSize: 16),
                ),
              ),
              
              SizedBox(height: 16),
              
              // OR Divider
              Row(
                children: [
                  Expanded(child: Divider()),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16),
                    child: Text('OR'),
                  ),
                  Expanded(child: Divider()),
                ],
              ),
              
              SizedBox(height: 16),
              
              // Social Login Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildSocialButton(Icons.g_mobiledata, Colors.red),
                  SizedBox(width: 16),
                  _buildSocialButton(Icons.facebook, Colors.blue),
                  SizedBox(width: 16),
                  _buildSocialButton(Icons.apple, Colors.black),
                ],
              ),
              
              SizedBox(height: 24),
              
              // Sign Up Link
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("Don't have an account? "),
                  TextButton(
                    onPressed: () {},
                    child: Text('Sign Up'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildSocialButton(IconData icon, Color color) {
    return Container(
      width: 50,
      height: 50,
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Icon(icon, color: color, size: 30),
    );
  }
}
```

---

## 📌 Key Takeaways

1. **Constraints go down, sizes go up, parent sets position**
2. **Container** is versatile - use for styling, spacing, constraints
3. **Row/Column** for linear layouts - use mainAxis and crossAxis alignment
4. **Stack** for overlapping - use Positioned for precise placement
5. **Expanded** fills available space - use flex for proportions
6. **Flexible** allows shrinking - good for adaptive content
7. **MediaQuery** for screen info - build responsive layouts
8. **SafeArea** protects from system UI overlays

---

## 🔗 Next Steps

Continue to [Day 7: Navigation](./day-7-navigation.md)

---

## 📚 Additional Resources

- [Layout Widgets](https://flutter.dev/docs/development/ui/widgets/layout)
- [Responsive Design](https://flutter.dev/docs/development/ui/layout/responsive)
- [BoxConstraints](https://api.flutter.dev/flutter/rendering/BoxConstraints-class.html)
