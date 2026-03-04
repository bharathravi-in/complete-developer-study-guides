# Day 8-9: State Management Basics

## 📋 Topics Covered
- setState Fundamentals
- Lifting State Up
- InheritedWidget
- Provider Package
- Consumer & Selector
- Cart Application

---

## 🎯 Part 1: Understanding State

### What is State?

State is any data that can change over time in your app:
- User input
- API responses
- UI state (loading, error, success)
- Shopping cart items
- User preferences

### Types of State

```dart
// 1. LOCAL STATE (Widget-specific)
class CounterWidget extends StatefulWidget {
  @override
  _CounterWidgetState createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _counter = 0; // Local state - only this widget needs it
  
  @override
  Widget build(BuildContext context) {
    return Text('Counter: $_counter');
  }
}

// 2. APP STATE (Shared across widgets)
// - User authentication status
// - Shopping cart
// - Theme settings
// - User profile
```

---

## 📱 Part 2: setState - The Basics

### Simple Counter with setState

```dart
import 'package:flutter/material.dart';

class CounterApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: CounterScreen(),
    );
  }
}

class CounterScreen extends StatefulWidget {
  @override
  _CounterScreenState createState() => _CounterScreenState();
}

class _CounterScreenState extends State<CounterScreen> {
  int _counter = 0;
  
  void _increment() {
    setState(() {
      // State changes inside setState trigger rebuild
      _counter++;
    });
  }
  
  void _decrement() {
    setState(() {
      _counter--;
    });
  }
  
  void _reset() {
    setState(() {
      _counter = 0;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    print('build() called'); // See how often this runs
    
    return Scaffold(
      appBar: AppBar(title: Text('Counter with setState')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Count:',
              style: TextStyle(fontSize: 20),
            ),
            Text(
              '$_counter',
              style: TextStyle(
                fontSize: 60,
                fontWeight: FontWeight.bold,
                color: _counter < 0 ? Colors.red : Colors.green,
              ),
            ),
            SizedBox(height: 30),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                FloatingActionButton(
                  onPressed: _decrement,
                  child: Icon(Icons.remove),
                  heroTag: 'decrement',
                ),
                SizedBox(width: 20),
                FloatingActionButton(
                  onPressed: _reset,
                  child: Icon(Icons.refresh),
                  heroTag: 'reset',
                ),
                SizedBox(width: 20),
                FloatingActionButton(
                  onPressed: _increment,
                  child: Icon(Icons.add),
                  heroTag: 'increment',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

### Complex State Example - Todo List

```dart
class TodoApp extends StatefulWidget {
  @override
  _TodoAppState createState() => _TodoAppState();
}

class _TodoAppState extends State<TodoApp> {
  List<String> _todos = [];
  final TextEditingController _controller = TextEditingController();
  
  void _addTodo() {
    if (_controller.text.isNotEmpty) {
      setState(() {
        _todos.add(_controller.text);
      });
      _controller.clear();
    }
  }
  
  void _removeTodo(int index) {
    setState(() {
      _todos.removeAt(index);
    });
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Todo List')),
      body: Column(
        children: [
          Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Enter todo',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _addTodo(),
                  ),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _addTodo,
                  child: Text('Add'),
                ),
              ],
            ),
          ),
          Expanded(
            child: _todos.isEmpty
                ? Center(child: Text('No todos yet'))
                : ListView.builder(
                    itemCount: _todos.length,
                    itemBuilder: (context, index) {
                      return ListTile(
                        title: Text(_todos[index]),
                        trailing: IconButton(
                          icon: Icon(Icons.delete, color: Colors.red),
                          onPressed: () => _removeTodo(index),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
```

---

## ⬆️ Part 3: Lifting State Up

### Problem: Sharing State Between Siblings

```dart
// When two widgets need to share state,
// lift the state to their common parent

class ParentWidget extends StatefulWidget {
  @override
  _ParentWidgetState createState() => _ParentWidgetState();
}

class _ParentWidgetState extends State<ParentWidget> {
  int _count = 0; // Lifted state
  
  void _increment() {
    setState(() => _count++);
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Pass state and callbacks to children
        DisplayWidget(count: _count),
        SizedBox(height: 20),
        ButtonWidget(onPressed: _increment),
      ],
    );
  }
}

// Stateless child - receives data
class DisplayWidget extends StatelessWidget {
  final int count;
  
  const DisplayWidget({required this.count});
  
  @override
  Widget build(BuildContext context) {
    return Text(
      'Count: $count',
      style: TextStyle(fontSize: 30),
    );
  }
}

// Stateless child - receives callback
class ButtonWidget extends StatelessWidget {
  final VoidCallback onPressed;
  
  const ButtonWidget({required this.onPressed});
  
  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      child: Text('Increment'),
    );
  }
}
```

---

## 🔗 Part 4: InheritedWidget

### Understanding InheritedWidget

```dart
// InheritedWidget allows data to flow down the widget tree
// without passing it through every level

class CounterData extends InheritedWidget {
  final int counter;
  final Function() increment;
  
  CounterData({
    required this.counter,
    required this.increment,
    required Widget child,
  }) : super(child: child);
  
  // Access this InheritedWidget from any descendant
  static CounterData? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<CounterData>();
  }
  
  // Should widget rebuild when data changes?
  @override
  bool updateShouldNotify(CounterData oldWidget) {
    return oldWidget.counter != counter;
  }
}

// Provider widget
class CounterProvider extends StatefulWidget {
  final Widget child;
  
  const CounterProvider({required this.child});
  
  @override
  _CounterProviderState createState() => _CounterProviderState();
}

class _CounterProviderState extends State<CounterProvider> {
  int _counter = 0;
  
  void _increment() {
    setState(() => _counter++);
  }
  
  @override
  Widget build(BuildContext context) {
    return CounterData(
      counter: _counter,
      increment: _increment,
      child: widget.child,
    );
  }
}

// App structure
class InheritedWidgetDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return CounterProvider(
      child: Scaffold(
        appBar: AppBar(title: Text('InheritedWidget Demo')),
        body: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CounterDisplay(),
            SizedBox(height: 20),
            IncrementButton(),
          ],
        ),
      ),
    );
  }
}

// Consumer widgets
class CounterDisplay extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final counterData = CounterData.of(context);
    
    return Text(
      'Count: ${counterData?.counter ?? 0}',
      style: TextStyle(fontSize: 30),
    );
  }
}

class IncrementButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final counterData = CounterData.of(context);
    
    return ElevatedButton(
      onPressed: counterData?.increment,
      child: Text('Increment'),
    );
  }
}
```

---

## 📦 Part 5: Provider Package

### Setup Provider

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  provider: ^6.0.5
```

### Basic Provider Example

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

// Model class
class Counter with ChangeNotifier {
  int _count = 0;
  
  int get count => _count;
  
  void increment() {
    _count++;
    notifyListeners(); // Notify widgets to rebuild
  }
  
  void decrement() {
    _count--;
    notifyListeners();
  }
  
  void reset() {
    _count = 0;
    notifyListeners();
  }
}

// Main app
void main() {
  runApp(
    // Provide Counter to entire app
    ChangeNotifierProvider(
      create: (context) => Counter(),
      child: MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: CounterScreen(),
    );
  }
}

class CounterScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Provider Example')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('You have pushed the button this many times:'),
            
            // Consumer rebuilds when Counter changes
            Consumer<Counter>(
              builder: (context, counter, child) {
                return Text(
                  '${counter.count}',
                  style: TextStyle(fontSize: 50, fontWeight: FontWeight.bold),
                );
              },
            ),
            
            SizedBox(height: 30),
            
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                FloatingActionButton(
                  onPressed: () {
                    // Access counter and call method
                    context.read<Counter>().decrement();
                  },
                  child: Icon(Icons.remove),
                  heroTag: 'dec',
                ),
                SizedBox(width: 20),
                FloatingActionButton(
                  onPressed: () {
                    context.read<Counter>().reset();
                  },
                  child: Icon(Icons.refresh),
                  heroTag: 'reset',
                ),
                SizedBox(width: 20),
                FloatingActionButton(
                  onPressed: () {
                    context.read<Counter>().increment();
                  },
                  child: Icon(Icons.add),
                  heroTag: 'inc',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

### Consumer vs Selector

```dart
// Consumer - Rebuilds when ANY property changes
Consumer<Counter>(
  builder: (context, counter, child) {
    print('[READ] This rebuilds on every counter change');
    return Text('${counter.count}');
  },
);

// Selector - Rebuilds only when SELECTED property changes (OPTIMIZED)
Selector<Counter, int>(
  selector: (context, counter) => counter.count,
  builder: (context, count, child) {
    print('This only rebuilds when count changes');
    return Text('$count');
  },
);

// Example with complex model
class UserModel with ChangeNotifier {
  String _name = 'John';
  int _age = 25;
  
  String get name => _name;
  int get age => _age;
  
  void updateName(String name) {
    _name = name;
    notifyListeners();
  }
  
  void updateAge(int age) {
    _age = age;
    notifyListeners();
  }
}

// This rebuilds on ANY change (name or age)
Consumer<UserModel>(
  builder: (context, user, child) {
    return Text('${user.name}, ${user.age}');
  },
);

// This only rebuilds when NAME changes
Selector<UserModel, String>(
  selector: (context, user) => user.name,
  builder: (context, name, child) {
    return Text(name);
  },
);
```

---

## 🛒 Part 6: Cart Application with Provider

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

// Product model
class Product {
  final String id;
  final String name;
  final double price;
  
  Product({required this.id, required this.name, required this.price});
}

// Cart item
class CartItem {
  final Product product;
  int quantity;
  
  CartItem({required this.product, this.quantity = 1});
  
  double get totalPrice => product.price * quantity;
}

// Cart model
class Cart with ChangeNotifier {
  final Map<String, CartItem> _items = {};
  
  Map<String, CartItem> get items => {..._items};
  
  int get itemCount {
    return _items.values.fold(0, (sum, item) => sum + item.quantity);
  }
  
  double get totalAmount {
    return _items.values.fold(0.0, (sum, item) => sum + item.totalPrice);
  }
  
  void addItem(Product product) {
    if (_items.containsKey(product.id)) {
      _items[product.id]!.quantity++;
    } else {
      _items[product.id] = CartItem(product: product);
    }
    notifyListeners();
  }
  
  void removeItem(String productId) {
    _items.remove(productId);
    notifyListeners();
  }
  
  void decreaseQuantity(String productId) {
    if (!_items.containsKey(productId)) return;
    
    if (_items[productId]!.quantity > 1) {
      _items[productId]!.quantity--;
    } else {
      _items.remove(productId);
    }
    notifyListeners();
  }
  
  void clear() {
    _items.clear();
    notifyListeners();
  }
}

// Main app
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => Cart(),
      child: CartApp(),
    ),
  );
}

class CartApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Shopping Cart',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: ProductListScreen(),
    );
  }
}

// Product list screen
class ProductListScreen extends StatelessWidget {
  final List<Product> products = [
    Product(id: '1', name: 'Flutter Book', price: 29.99),
    Product(id: '2', name: 'Dart Course', price: 49.99),
    Product(id: '3', name: 'UI Kit', price: 19.99),
    Product(id: '4', name: 'State Management Guide', price: 39.99),
  ];
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Products'),
        actions: [
          IconButton(
            icon: Stack(
              children: [
                Icon(Icons.shopping_cart),
                Consumer<Cart>(
                  builder: (context, cart, child) {
                    if (cart.itemCount == 0) return SizedBox();
                    return Positioned(
                      right: 0,
                      child: Container(
                        padding: EdgeInsets.all(2),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        constraints: BoxConstraints(
                          minWidth: 16,
                          minHeight: 16,
                        ),
                        child: Text(
                          '${cart.itemCount}',
                          style: TextStyle(fontSize: 10),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => CartScreen()),
              );
            },
          ),
        ],
      ),
      body: ListView.builder(
        itemCount: products.length,
        itemBuilder: (context, index) {
          final product = products[index];
          return Card(
            margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ListTile(
              title: Text(product.name),
              subtitle: Text('\$${product.price.toStringAsFixed(2)}'),
              trailing: IconButton(
                icon: Icon(Icons.add_shopping_cart, color: Colors.blue),
                onPressed: () {
                  context.read<Cart>().addItem(product);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Added to cart'),
                      duration: Duration(seconds: 1),
                    ),
                  );
                },
              ),
            ),
          );
        },
      ),
    );
  }
}

// Cart screen
class CartScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Cart'),
        actions: [
          IconButton(
            icon: Icon(Icons.delete_outline),
            onPressed: () {
              context.read<Cart>().clear();
            },
          ),
        ],
      ),
      body: Consumer<Cart>(
        builder: (context, cart, child) {
          if (cart.items.isEmpty) {
            return Center(
              child: Text('Your cart is empty'),
            );
          }
          
          return Column(
            children: [
              Expanded(
                child: ListView.builder(
                  itemCount: cart.items.length,
                  itemBuilder: (context, index) {
                    final item = cart.items.values.toList()[index];
                    return Card(
                      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: Padding(
                        padding: EdgeInsets.all(8),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    item.product.name,
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Text(
                                    '\$${item.product.price.toStringAsFixed(2)} x ${item.quantity}',
                                  ),
                                  Text(
                                    'Total: \$${item.totalPrice.toStringAsFixed(2)}',
                                    style: TextStyle(
                                      color: Colors.green,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              icon: Icon(Icons.remove_circle_outline),
                              onPressed: () {
                                cart.decreaseQuantity(item.product.id);
                              },
                            ),
                            Text('${item.quantity}'),
                            IconButton(
                              icon: Icon(Icons.add_circle_outline),
                              onPressed: () {
                                cart.addItem(item.product);
                              },
                            ),
                            IconButton(
                              icon: Icon(Icons.delete, color: Colors.red),
                              onPressed: () {
                                cart.removeItem(item.product.id);
                              },
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 4,
                      offset: Offset(0, -2),
                    ),
                  ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Total:',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '\$${cart.totalAmount.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: EdgeInsets.all(16),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      // Checkout logic
                      showDialog(
                        context: context,
                        builder: (context) => AlertDialog(
                          title: Text('Order Placed'),
                          content: Text(
                            'Total: \$${cart.totalAmount.toStringAsFixed(2)}',
                          ),
                          actions: [
                            TextButton(
                              onPressed: () {
                                cart.clear();
                                Navigator.pop(context);
                                Navigator.pop(context);
                              },
                              child: Text('OK'),
                            ),
                          ],
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: Text('Checkout'),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
```

---

## 📌 Key Takeaways

1. **setState** is simple but not scalable for large apps
2. **Lift state up** to share between sibling widgets
3. **InheritedWidget** enables data flow down the tree
4. **Provider** simplifies state management significantly
5. **ChangeNotifier** + **notifyListeners()** triggers rebuilds
6. **context.read()** to access without listening
7. **Consumer** for rebuilds, **Selector** for optimization
8. Separate business logic from UI using models

---

## 🔗 Next Steps

Continue to [Day 10-11: Forms & Validation](./day-10-11-forms.md)

---

## 📚 Additional Resources

- [Provider Package](https://pub.dev/packages/provider)
- [State Management Options](https://flutter.dev/docs/development/data-and-backend/state-mgmt/options)
- [InheritedWidget](https://api.flutter.dev/flutter/widgets/InheritedWidget-class.html)
