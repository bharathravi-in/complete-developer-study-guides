# Day 7: Navigation

## 📋 Topics Covered
- Navigator 1.0 Basics
- Push & Pop
- Named Routes
- Passing Arguments
- Returning Data
- Route Lifecycle
- Custom Transitions

---

## 🧭 Part 1: Navigator Basics

### Understanding the Navigation Stack

```dart
// Navigation works like a stack (LIFO - Last In First Out)
//
// Screen 3 (top)
// Screen 2
// Screen 1
// Screen 0 (bottom/home)
//
// Push: Add screen to top
// Pop: Remove screen from top
```

### Basic Navigation

```dart
import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Navigation Demo',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Home Screen')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Home Screen',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            
            // Basic Push
            ElevatedButton(
              onPressed: () {
                // Push new screen onto stack
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => SecondScreen(),
                  ),
                );
              },
              child: Text('Go to Second Screen'),
            ),
            
            SizedBox(height: 10),
            
            // Push with data
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => DetailScreen(
                      title: 'Passed Data',
                      description: 'This data was passed from Home Screen',
                    ),
                  ),
                );
              },
              child: Text('Go to Detail Screen'),
            ),
          ],
        ),
      ),
    );
  }
}

class SecondScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Second Screen'),
        // Back button is automatic
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Second Screen',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            
            // Pop with default back button (automatic)
            Text('Use back button or:'),
            SizedBox(height: 10),
            
            // Manual Pop
            ElevatedButton(
              onPressed: () {
                // Remove current screen from stack
                Navigator.pop(context);
              },
              child: Text('Go Back'),
            ),
            
            SizedBox(height: 20),
            
            // Push another screen
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ThirdScreen(),
                  ),
                );
              },
              child: Text('Go to Third Screen'),
            ),
          ],
        ),
      ),
    );
  }
}

class ThirdScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Third Screen')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Third Screen',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            
            // Pop back one screen
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Back to Second Screen'),
            ),
            
            SizedBox(height: 10),
            
            // Pop multiple screens
            ElevatedButton(
              onPressed: () {
                // Pop until we reach home screen
                Navigator.popUntil(context, (route) => route.isFirst);
              },
              child: Text('Back to Home Screen'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 📦 Part 2: Passing Data Between Screens

### Passing Data Forward

```dart
class DetailScreen extends StatelessWidget {
  final String title;
  final String description;
  
  const DetailScreen({
    required this.title,
    required this.description,
  });
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              description,
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}

// Usage
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => DetailScreen(
      title: 'Product Name',
      description: 'Product description goes here',
    ),
  ),
);
```

### Returning Data Back

```dart
class SelectionScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Select an Option')),
      body: ListView(
        children: [
          ListTile(
            title: Text('Option 1'),
            onTap: () {
              // Pop and return data
              Navigator.pop(context, 'Option 1');
            },
          ),
          ListTile(
            title: Text('Option 2'),
            onTap: () {
              Navigator.pop(context, 'Option 2');
            },
          ),
          ListTile(
            title: Text('Option 3'),
            onTap: () {
              Navigator.pop(context, 'Option 3');
            },
          ),
        ],
      ),
    );
  }
}

// Receiving returned data
class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? selectedOption;
  
  void _navigateAndGetResult() async {
    // Wait for result from SelectionScreen
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SelectionScreen(),
      ),
    );
    
    // Update state with returned data
    if (result != null) {
      setState(() {
        selectedOption = result;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Home')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              selectedOption ?? 'No option selected',
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _navigateAndGetResult,
              child: Text('Select Option'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 🏷️ Part 3: Named Routes

### Setting Up Named Routes

```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Named Routes Demo',
      // Define initial route
      initialRoute: '/',
      
      // Define all routes
      routes: {
        '/': (context) => HomeScreen(),
        '/second': (context) => SecondScreen(),
        '/third': (context) => ThirdScreen(),
        '/profile': (context) => ProfileScreen(),
        '/settings': (context) => SettingsScreen(),
      },
      
      // Handle unknown routes
      onUnknownRoute: (settings) {
        return MaterialPageRoute(
          builder: (context) => NotFoundScreen(),
        );
      },
    );
  }
}

// Using named routes
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Home')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                // Navigate using route name
                Navigator.pushNamed(context, '/second');
              },
              child: Text('Go to Second Screen'),
            ),
            
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/profile');
              },
              child: Text('Go to Profile'),
            ),
            
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/settings');
              },
              child: Text('Go to Settings'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Named Routes with Arguments

```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Routes with Arguments',
      initialRoute: '/',
      onGenerateRoute: (settings) {
        // Handle dynamic routing with arguments
        switch (settings.name) {
          case '/':
            return MaterialPageRoute(builder: (_) => HomeScreen());
          
          case '/user':
            // Extract arguments
            final args = settings.arguments as Map<String, dynamic>;
            return MaterialPageRoute(
              builder: (_) => UserScreen(
                userId: args['userId'],
                userName: args['userName'],
              ),
            );
          
          case '/product':
            final ProductArguments args = 
                settings.arguments as ProductArguments;
            return MaterialPageRoute(
              builder: (_) => ProductScreen(
                id: args.id,
                name: args.name,
                price: args.price,
              ),
            );
          
          default:
            return MaterialPageRoute(builder: (_) => NotFoundScreen());
        }
      },
    );
  }
}

// Arguments class
class ProductArguments {
  final String id;
  final String name;
  final double price;
  
  ProductArguments({
    required this.id,
    required this.name,
    required this.price,
  });
}

// Passing arguments
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Home')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                // Pass Map arguments
                Navigator.pushNamed(
                  context,
                  '/user',
                  arguments: {
                    'userId': '123',
                    'userName': 'John Doe',
                  },
                );
              },
              child: Text('Go to User Screen'),
            ),
            
            SizedBox(height: 10),
            
            ElevatedButton(
              onPressed: () {
                // Pass typed arguments
                Navigator.pushNamed(
                  context,
                  '/product',
                  arguments: ProductArguments(
                    id: 'P001',
                    name: 'Flutter Book',
                    price: 29.99,
                  ),
                );
              },
              child: Text('Go to Product Screen'),
            ),
          ],
        ),
      ),
    );
  }
}

// Receiving arguments
class UserScreen extends StatelessWidget {
  final String userId;
  final String userName;
  
  const UserScreen({
    required this.userId,
    required this.userName,
  });
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('User Details')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('User ID: $userId'),
            Text('User Name: $userName'),
          ],
        ),
      ),
    );
  }
}

class ProductScreen extends StatelessWidget {
  final String id;
  final String name;
  final double price;
  
  const ProductScreen({
    required this.id,
    required this.name,
    required this.price,
  });
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(name)),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Product ID: $id'),
            Text('Name: $name'),
            Text('Price: \$${price.toStringAsFixed(2)}'),
          ],
        ),
      ),
    );
  }
}
```

---

## 🔄 Part 4: Advanced Navigation Patterns

### Replace Current Route

```dart
// pushReplacement - Replace current screen
ElevatedButton(
  onPressed: () {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => NewScreen()),
    );
    // Current screen is removed from stack
    // User can't go back to it
  },
  child: Text('Replace Current Screen'),
);

// Use case: After login, replace login screen with home
class LoginScreen extends StatelessWidget {
  void _login(BuildContext context) {
    // Perform login
    // ...
    
    // Replace login screen with home
    Navigator.pushReplacementNamed(context, '/home');
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          onPressed: () => _login(context),
          child: Text('Login'),
        ),
      ),
    );
  }
}
```

### Push and Remove Until

```dart
// pushAndRemoveUntil - Clear navigation stack
ElevatedButton(
  onPressed: () {
    // Go to home and remove all previous screens
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => HomeScreen()),
      (route) => false, // Remove all previous routes
    );
  },
  child: Text('Go to Home (Clear Stack)'),
);

// Use case: After logout
class SettingsScreen extends StatelessWidget {
  void _logout(BuildContext context) {
    // Clear user data
    // ...
    
    // Go to login and clear all screens
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => LoginScreen()),
      (route) => false,
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Settings')),
      body: Center(
        child: ElevatedButton(
          onPressed: () => _logout(context),
          child: Text('Logout'),
        ),
      ),
    );
  }
}
```

### Pop Until

```dart
// Pop until specific route
ElevatedButton(
  onPressed: () {
    // Pop until we reach first route (home)
    Navigator.popUntil(context, (route) => route.isFirst);
  },
  child: Text('Back to Home'),
);

// Pop until named route
ElevatedButton(
  onPressed: () {
    Navigator.popUntil(
      context,
      ModalRoute.withName('/home'),
    );
  },
  child: Text('Back to Home (Named)'),
);
```

---

## 🎨 Part 5: Custom Transitions

### Custom Page Transitions

```dart
class SlideRightRoute extends PageRouteBuilder {
  final Widget page;
  
  SlideRightRoute({required this.page})
      : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            const begin = Offset(-1.0, 0.0);
            const end = Offset.zero;
            const curve = Curves.easeInOut;
            
            var tween = Tween(begin: begin, end: end)
                .chain(CurveTween(curve: curve));
            var offsetAnimation = animation.drive(tween);
            
            return SlideTransition(
              position: offsetAnimation,
              child: child,
            );
          },
        );
}

// Usage
Navigator.push(
  context,
  SlideRightRoute(page: SecondScreen()),
);
```

### Fade Transition

```dart
class FadeRoute extends PageRouteBuilder {
  final Widget page;
  
  FadeRoute({required this.page})
      : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: animation,
              child: child,
            );
          },
        );
}
```

### Scale Transition

```dart
class ScaleRoute extends PageRouteBuilder {
  final Widget page;
  
  ScaleRoute({required this.page})
      : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return ScaleTransition(
              scale: Tween<double>(begin: 0.0, end: 1.0).animate(
                CurvedAnimation(
                  parent: animation,
                  curve: Curves.fastOutSlowIn,
                ),
              ),
              child: child,
            );
          },
        );
}
```

---

## 🎯 Practice Project: Multi-Screen App

```dart
import 'package:flutter/material.dart';

void main() => runApp(MultiScreenApp());

class MultiScreenApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Multi-Screen App',
      theme: ThemeData(primarySwatch: Colors.blue),
      initialRoute: '/',
      routes: {
        '/': (context) => MenuScreen(),
        '/profile': (context) => ProfileScreen(),
        '/products': (context) => ProductsScreen(),
        '/settings': (context) => SettingsScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/product-detail') {
          final product = settings.arguments as Product;
          return MaterialPageRoute(
            builder: (context) => ProductDetailScreen(product: product),
          );
        }
        return null;
      },
    );
  }
}

class MenuScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Main Menu')),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          _buildMenuCard(
            context,
            title: 'Profile',
            icon: Icons.person,
            color: Colors.blue,
            onTap: () => Navigator.pushNamed(context, '/profile'),
          ),
          _buildMenuCard(
            context,
            title: 'Products',
            icon: Icons.shopping_bag,
            color: Colors.green,
            onTap: () => Navigator.pushNamed(context, '/products'),
          ),
          _buildMenuCard(
            context,
            title: 'Settings',
            icon: Icons.settings,
            color: Colors.orange,
            onTap: () => Navigator.pushNamed(context, '/settings'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMenuCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color,
          child: Icon(icon, color: Colors.white),
        ),
        title: Text(
          title,
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        trailing: Icon(Icons.arrow_forward_ios),
        onTap: onTap,
      ),
    );
  }
}

class Product {
  final String id;
  final String name;
  final double price;
  final String description;
  
  Product({
    required this.id,
    required this.name,
    required this.price,
    required this.description,
  });
}

class ProductsScreen extends StatelessWidget {
  final List<Product> products = [
    Product(
      id: '1',
      name: 'Flutter Book',
      price: 29.99,
      description: 'Complete guide to Flutter development',
    ),
    Product(
      id: '2',
      name: 'Dart Course',
      price: 49.99,
      description: 'Master Dart programming language',
    ),
    Product(
      id: '3',
      name: 'UI Kit',
      price: 19.99,
      description: 'Beautiful Flutter UI components',
    ),
  ];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Products')),
      body: ListView.builder(
        padding: EdgeInsets.all(16),
        itemCount: products.length,
        itemBuilder: (context, index) {
          final product = products[index];
          return Card(
            margin: EdgeInsets.only(bottom: 16),
            child: ListTile(
              title: Text(product.name),
              subtitle: Text('\$${product.price.toStringAsFixed(2)}'),
              trailing: Icon(Icons.arrow_forward),
              onTap: () {
                Navigator.pushNamed(
                  context,
                  '/product-detail',
                  arguments: product,
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class ProductDetailScreen extends StatelessWidget {
  final Product product;
  
  const ProductDetailScreen({required this.product});
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(product.name)),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              product.name,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              '\$${product.price.toStringAsFixed(2)}',
              style: TextStyle(fontSize: 20, color: Colors.green),
            ),
            SizedBox(height: 20),
            Text(
              product.description,
              style: TextStyle(fontSize: 16),
            ),
            Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: Text('Add to Cart'),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Profile')),
      body: Center(
        child: Text('Profile Screen'),
      ),
    );
  }
}

class SettingsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Settings')),
      body: Center(
        child: Text('Settings Screen'),
      ),
    );
  }
}
```

---

## 📌 Key Takeaways

1. **Navigator is a stack** - Last In, First Out (LIFO)
2. **Push** adds screen, **Pop** removes current screen
3. **Named routes** make navigation cleaner and maintainable
4. **Pass data forward** via constructor or arguments
5. **Return data back** via Navigator.pop with value
6. **pushReplacement** for login/logout flows
7. **pushAndRemoveUntil** to clear navigation stack
8. **Custom transitions** for better UX

---

## 🔗 Next Steps

Continue to [Week 2 - Intermediate Level](../week-2/README.md)

---

## 📚 Additional Resources

- [Navigation and Routing](https://flutter.dev/docs/development/ui/navigation)
- [Navigator class](https://api.flutter.dev/flutter/widgets/Navigator-class.html)
- [Named Routes](https://flutter.dev/docs/cookbook/navigation/named-routes)
