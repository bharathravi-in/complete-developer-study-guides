# Day 8: Prototypes & Inheritance

## 🎯 Learning Objectives
- Understand `__proto__` and prototype
- Master the prototype chain
- Learn constructor functions
- Understand ES6 classes
- Implement inheritance patterns

---

## 📚 Understanding Prototypes

Every JavaScript object has an internal link to another object called its **prototype**. This prototype object has its own prototype, forming a **prototype chain**.

```javascript
// Every object has a prototype
const obj = { name: "John" };
console.log(Object.getPrototypeOf(obj)); // Object.prototype

// Arrays have Array.prototype
const arr = [1, 2, 3];
console.log(Object.getPrototypeOf(arr)); // Array.prototype

// Functions have Function.prototype
function myFunc() {}
console.log(Object.getPrototypeOf(myFunc)); // Function.prototype

/*
═══════════════════════════════════════════════════════════
PROTOTYPE CHAIN VISUALIZATION:
═══════════════════════════════════════════════════════════

      obj                 Object.prototype              null
   ┌───────────┐        ┌─────────────────┐
   │name:"John"│───────▶│  toString()     │───────▶  null
   └───────────┘        │  valueOf()      │
      [[Prototype]]     │  hasOwnProperty │
                        └─────────────────┘
                           [[Prototype]]
*/
```

---

## 🔗 `__proto__` vs prototype

```javascript
// __proto__ (deprecated, use Object.getPrototypeOf)
// Links an INSTANCE to its prototype
const animal = { eats: true };
const rabbit = { jumps: true };

rabbit.__proto__ = animal; // Set prototype (deprecated way)
console.log(rabbit.eats);  // true (inherited)

// Modern way
Object.setPrototypeOf(rabbit, animal);
console.log(Object.getPrototypeOf(rabbit) === animal); // true

// prototype property
// Exists ONLY on functions - used when called with `new`
function Dog(name) {
    this.name = name;
}

// Dog.prototype is shared by all instances
Dog.prototype.bark = function() {
    return `${this.name} says woof!`;
};

const dog1 = new Dog("Buddy");
const dog2 = new Dog("Max");

console.log(dog1.bark()); // "Buddy says woof!"
console.log(dog2.bark()); // "Max says woof!"

// Both instances share the same prototype
console.log(dog1.__proto__ === Dog.prototype); // true
console.log(dog1.__proto__ === dog2.__proto__); // true

/*
═══════════════════════════════════════════════════════════
DISTINCTION:
═══════════════════════════════════════════════════════════

__proto__  (instance property):
- Every object has it
- Points to the object's prototype
- Used for LOOKUP of properties

prototype (function property):
- Only functions have it
- Becomes __proto__ of instances created with new
- Used to DEFINE shared methods

Function:  Dog              ──has──▶  Dog.prototype
                                          │
Instance:  dog1.__proto__  ──points to────┘
Instance:  dog2.__proto__  ──points to────┘
*/
```

---

## ⛓️ Prototype Chain

```javascript
// Property lookup follows the chain
function Animal(name) {
    this.name = name;
}

Animal.prototype.eat = function() {
    console.log(`${this.name} is eating`);
};

function Dog(name, breed) {
    Animal.call(this, name); // Call parent constructor
    this.breed = breed;
}

// Set up prototype chain
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

Dog.prototype.bark = function() {
    console.log(`${this.name} says woof!`);
};

const buddy = new Dog("Buddy", "Golden Retriever");

// Prototype chain:
// buddy → Dog.prototype → Animal.prototype → Object.prototype → null

buddy.bark();  // From Dog.prototype
buddy.eat();   // From Animal.prototype
console.log(buddy.toString()); // From Object.prototype

// Check the chain
console.log(buddy instanceof Dog);    // true
console.log(buddy instanceof Animal); // true
console.log(buddy instanceof Object); // true

// hasOwnProperty vs in
console.log(buddy.hasOwnProperty("name"));  // true (own property)
console.log(buddy.hasOwnProperty("bark"));  // false (on prototype)
console.log("bark" in buddy);               // true (anywhere in chain)

/*
═══════════════════════════════════════════════════════════
PROTOTYPE CHAIN:
═══════════════════════════════════════════════════════════

buddy                    Dog.prototype           Animal.prototype
┌──────────────┐        ┌───────────────┐       ┌───────────────┐
│name: "Buddy" │───────▶│bark: function │──────▶│eat: function  │
│breed: "GR"   │        │constructor:Dog│       │constructor:   │
└──────────────┘        └───────────────┘       │     Animal    │
   [[Prototype]]          [[Prototype]]         └───────────────┘
                                                  [[Prototype]]
                                                       │
                                                       ▼
                                               Object.prototype
                                                       │
                                                       ▼
                                                     null
*/
```

---

## 🏗️ Constructor Functions

```javascript
// Constructor function (convention: PascalCase)
function Person(name, age) {
    // 'this' refers to the new object being created
    this.name = name;
    this.age = age;
    
    // Instance method (NOT recommended - created for each instance)
    this.sayHello = function() {
        console.log(`Hi, I'm ${this.name}`);
    };
}

// Prototype method (recommended - shared across all instances)
Person.prototype.introduce = function() {
    console.log(`I'm ${this.name}, ${this.age} years old`);
};

// Static method (on constructor itself)
Person.isAdult = function(person) {
    return person.age >= 18;
};

const john = new Person("John", 30);
const jane = new Person("Jane", 25);

john.introduce();           // Works (shared method)
console.log(Person.isAdult(john)); // true (static method)

// Constructor property
console.log(john.constructor === Person); // true
console.log(Person.prototype.constructor === Person); // true

// Creating instance from another instance
const johnClone = new john.constructor("John Clone", 30);
```

### What `new` Does Internally

```javascript
function simulateNew(Constructor, ...args) {
    // 1. Create empty object
    const obj = {};
    
    // 2. Link to prototype
    Object.setPrototypeOf(obj, Constructor.prototype);
    // Or: obj.__proto__ = Constructor.prototype;
    
    // 3. Execute constructor with 'this' = obj
    const result = Constructor.apply(obj, args);
    
    // 4. Return obj (unless constructor returns an object)
    return result instanceof Object ? result : obj;
}

// Usage
const person = simulateNew(Person, "Test", 25);
console.log(person.name); // "Test"
person.introduce(); // Works!
```

---

## 🎨 ES6 Classes

ES6 classes are "syntactic sugar" over prototype-based inheritance.

```javascript
// ES6 Class
class Animal {
    // Constructor
    constructor(name) {
        this.name = name;
    }
    
    // Instance method (on prototype)
    speak() {
        console.log(`${this.name} makes a sound`);
    }
    
    // Static method (on class itself)
    static isAnimal(obj) {
        return obj instanceof Animal;
    }
    
    // Getter
    get description() {
        return `Animal named ${this.name}`;
    }
    
    // Setter
    set nickname(value) {
        this._nickname = value;
    }
}

// Inheritance
class Dog extends Animal {
    constructor(name, breed) {
        super(name); // Call parent constructor
        this.breed = breed;
    }
    
    // Override parent method
    speak() {
        console.log(`${this.name} barks`);
    }
    
    // Call parent method
    speakLoud() {
        super.speak(); // Call parent's speak
        console.log("WOOF WOOF!");
    }
}

const dog = new Dog("Rex", "German Shepherd");
dog.speak();         // "Rex barks"
dog.speakLoud();     // "Rex makes a sound" then "WOOF WOOF!"
console.log(Animal.isAnimal(dog)); // true

// Under the hood - same as constructor functions!
console.log(typeof Animal); // "function"
console.log(Dog.prototype.__proto__ === Animal.prototype); // true
```

### Class Features

```javascript
// Private fields (ES2022)
class BankAccount {
    #balance = 0;     // Private field
    #pin;             // Private field
    
    constructor(initialBalance, pin) {
        this.#balance = initialBalance;
        this.#pin = pin;
    }
    
    // Private method
    #validatePin(pin) {
        return pin === this.#pin;
    }
    
    withdraw(amount, pin) {
        if (!this.#validatePin(pin)) {
            throw new Error("Invalid PIN");
        }
        if (amount > this.#balance) {
            throw new Error("Insufficient funds");
        }
        this.#balance -= amount;
        return this.#balance;
    }
    
    getBalance(pin) {
        if (!this.#validatePin(pin)) {
            throw new Error("Invalid PIN");
        }
        return this.#balance;
    }
}

const account = new BankAccount(1000, "1234");
console.log(account.getBalance("1234")); // 1000
// console.log(account.#balance); // SyntaxError: Private field

// Static fields
class MathUtils {
    static PI = 3.14159;
    static #privateStatic = "private";
    
    static circleArea(radius) {
        return MathUtils.PI * radius * radius;
    }
}

console.log(MathUtils.PI);           // 3.14159
console.log(MathUtils.circleArea(5)); // 78.53975
```

---

## 🔄 Inheritance Patterns

### 1. Prototypal Inheritance (Object.create)

```javascript
const personProto = {
    greet() {
        console.log(`Hello, I'm ${this.name}`);
    },
    describe() {
        console.log(`${this.name} is ${this.age} years old`);
    }
};

const john = Object.create(personProto);
john.name = "John";
john.age = 30;
john.greet(); // "Hello, I'm John"

// Factory with Object.create
function createPerson(name, age) {
    const person = Object.create(personProto);
    person.name = name;
    person.age = age;
    return person;
}
```

### 2. Constructor Inheritance (ES5)

```javascript
function Vehicle(type) {
    this.type = type;
}

Vehicle.prototype.describe = function() {
    console.log(`This is a ${this.type}`);
};

function Car(brand) {
    Vehicle.call(this, "car"); // Call parent constructor
    this.brand = brand;
}

// Setup inheritance
Car.prototype = Object.create(Vehicle.prototype);
Car.prototype.constructor = Car;

Car.prototype.honk = function() {
    console.log(`${this.brand} goes beep!`);
};

const toyota = new Car("Toyota");
toyota.describe(); // "This is a car"
toyota.honk();     // "Toyota goes beep!"
```

### 3. Class Inheritance (ES6)

```javascript
class Shape {
    constructor(color) {
        this.color = color;
    }
    
    describe() {
        return `A ${this.color} shape`;
    }
}

class Rectangle extends Shape {
    constructor(color, width, height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    area() {
        return this.width * this.height;
    }
    
    describe() {
        return `${super.describe()} - Rectangle (${this.width}x${this.height})`;
    }
}

class Square extends Rectangle {
    constructor(color, side) {
        super(color, side, side);
    }
    
    describe() {
        return `${super.describe()} (Square)`;
    }
}

const square = new Square("red", 5);
console.log(square.area());     // 25
console.log(square.describe()); // "A red shape - Rectangle (5x5) (Square)"
```

### 4. Composition over Inheritance

```javascript
// Mixins for composition
const canEat = {
    eat() { console.log("Eating..."); }
};

const canWalk = {
    walk() { console.log("Walking..."); }
};

const canSwim = {
    swim() { console.log("Swimming..."); }
};

// Compose behaviors
class Duck {
    constructor(name) {
        this.name = name;
    }
}

Object.assign(Duck.prototype, canEat, canWalk, canSwim);

const duck = new Duck("Donald");
duck.eat();  // "Eating..."
duck.walk(); // "Walking..."
duck.swim(); // "Swimming..."

// Factory function composition
function createRobot(name) {
    return {
        name,
        ...canWalk,
        beep() { console.log("Beep boop!"); }
    };
}
```

---

## ❓ Interview Questions

### Q1: Difference between class & prototype?

```javascript
// Classes ARE prototypes under the hood - just syntactic sugar

// Class way
class Person {
    constructor(name) {
        this.name = name;
    }
    greet() {
        console.log(`Hi, I'm ${this.name}`);
    }
}

// Prototype way (equivalent)
function PersonProto(name) {
    this.name = name;
}
PersonProto.prototype.greet = function() {
    console.log(`Hi, I'm ${this.name}`);
};

// Both work the same
const p1 = new Person("John");
const p2 = new PersonProto("John");

/*
KEY DIFFERENCES:
1. Classes are NOT hoisted (TDZ applies)
2. Class methods are non-enumerable by default
3. Class always runs in strict mode
4. Classes must be called with `new`
5. Classes have cleaner syntax for inheritance
*/

// Class without new throws error
// Person("John"); // TypeError: Class constructor cannot be invoked without 'new'

// Function works (but wrong `this`)
PersonProto("John"); // No error, but probably not what you want
```

### Q2: How does inheritance work internally?

```javascript
// When you access a property:
// 1. Check the object itself
// 2. Check object's [[Prototype]] (i.e., __proto__)
// 3. Check that prototype's [[Prototype]]
// 4. Continue until null is reached

const grandparent = { family: "Smith" };
const parent = Object.create(grandparent);
parent.city = "NYC";
const child = Object.create(parent);
child.name = "John";

console.log(child.name);   // "John" (own property)
console.log(child.city);   // "NYC" (from parent)
console.log(child.family); // "Smith" (from grandparent)

// Setting a property ALWAYS creates it on the object itself
child.city = "LA";        // Creates own property, doesn't modify parent
console.log(parent.city); // "NYC" (unchanged)
console.log(child.city);  // "LA" (own property now)
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: Implement instanceof
function myInstanceOf(obj, Constructor) {
    let proto = Object.getPrototypeOf(obj);
    while (proto !== null) {
        if (proto === Constructor.prototype) {
            return true;
        }
        proto = Object.getPrototypeOf(proto);
    }
    return false;
}

// Problem 2: Create inheritance chain
function Animal(name) {
    this.name = name;
}
Animal.prototype.speak = function() {
    console.log(this.name + " makes a sound");
};

function Dog(name, breed) {
    Animal.call(this, name);
    this.breed = breed;
}
// Setup inheritance HERE
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;
Dog.prototype.speak = function() {
    console.log(this.name + " barks");
};

// Problem 3: What's the output?
function Foo() {}
Foo.prototype.name = "Foo";

const a = new Foo();
const b = new Foo();

a.name = "a";
console.log(a.name); // ?
console.log(b.name); // ?

// Answer: "a", "Foo" (a has own property, b uses prototype)
```

---

## ✅ Day 8 Checklist

- [ ] Understand `__proto__` vs prototype
- [ ] Know the prototype chain lookup mechanism
- [ ] Create constructor functions properly
- [ ] Add methods to prototype
- [ ] Implement prototypal inheritance
- [ ] Use ES6 classes
- [ ] Understand class under the hood
- [ ] Implement class inheritance with extends
- [ ] Know private fields syntax
- [ ] Use composition over inheritance when appropriate
- [ ] Complete practice problems
