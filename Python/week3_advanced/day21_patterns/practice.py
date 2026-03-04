#!/usr/bin/env python3
"""Day 21 - Design Patterns in Python"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from functools import wraps

print("=" * 50)
print("DESIGN PATTERNS")
print("=" * 50)


# ============================================
# 1. SINGLETON
# ============================================
print("\n--- 1. SINGLETON ---")


class SingletonMeta(type):
    """Metaclass for Singleton pattern"""
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    """Database connection singleton"""
    
    def __init__(self):
        print("  Initializing Database connection...")
        self.connection = "Connected"
    
    def query(self, sql: str) -> str:
        return f"Result for: {sql}"


# Test Singleton
db1 = Database()
db2 = Database()
print(f"db1 is db2: {db1 is db2}")


# Alternative: Singleton decorator
def singleton(cls):
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton
class Config:
    def __init__(self):
        self.settings = {}


# ============================================
# 2. FACTORY
# ============================================
print("\n--- 2. FACTORY ---")


class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass
    
    @abstractmethod
    def on_click(self) -> str:
        pass


class WindowsButton(Button):
    def render(self) -> str:
        return "Rendering Windows button"
    
    def on_click(self) -> str:
        return "Windows button clicked"


class MacButton(Button):
    def render(self) -> str:
        return "Rendering Mac button"
    
    def on_click(self) -> str:
        return "Mac button clicked"


class ButtonFactory:
    """Factory for creating buttons"""
    
    @staticmethod
    def create_button(os_type: str) -> Button:
        if os_type == "windows":
            return WindowsButton()
        elif os_type == "mac":
            return MacButton()
        else:
            raise ValueError(f"Unknown OS: {os_type}")


# Test Factory
for os_type in ["windows", "mac"]:
    button = ButtonFactory.create_button(os_type)
    print(f"  {os_type}: {button.render()}")


# ============================================
# 3. ABSTRACT FACTORY
# ============================================
print("\n--- 3. ABSTRACT FACTORY ---")


class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass
    
    @abstractmethod
    def create_checkbox(self) -> 'Checkbox':
        pass


class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class WindowsCheckbox(Checkbox):
    def render(self) -> str:
        return "Windows checkbox"


class MacCheckbox(Checkbox):
    def render(self) -> str:
        return "Mac checkbox"


class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()
    
    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()


class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()
    
    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()


def create_ui(factory: GUIFactory):
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    return button.render(), checkbox.render()


print(f"  Windows UI: {create_ui(WindowsFactory())}")
print(f"  Mac UI: {create_ui(MacFactory())}")


# ============================================
# 4. STRATEGY
# ============================================
print("\n--- 4. STRATEGY ---")


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> str:
        pass


class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str):
        self.card_number = card_number
    
    def pay(self, amount: float) -> str:
        return f"Paid ${amount} with card ending in {self.card_number[-4:]}"


class PayPalPayment(PaymentStrategy):
    def __init__(self, email: str):
        self.email = email
    
    def pay(self, amount: float) -> str:
        return f"Paid ${amount} via PayPal ({self.email})"


class CryptoPayment(PaymentStrategy):
    def __init__(self, wallet: str):
        self.wallet = wallet
    
    def pay(self, amount: float) -> str:
        return f"Paid ${amount} in crypto to {self.wallet[:8]}..."


class ShoppingCart:
    def __init__(self):
        self.items: List[tuple] = []
        self._payment_strategy: Optional[PaymentStrategy] = None
    
    def add_item(self, name: str, price: float):
        self.items.append((name, price))
    
    @property
    def total(self) -> float:
        return sum(price for _, price in self.items)
    
    def set_payment_method(self, strategy: PaymentStrategy):
        self._payment_strategy = strategy
    
    def checkout(self) -> str:
        if not self._payment_strategy:
            raise ValueError("No payment method set")
        return self._payment_strategy.pay(self.total)


# Test Strategy
cart = ShoppingCart()
cart.add_item("Book", 29.99)
cart.add_item("Coffee", 4.99)

cart.set_payment_method(CreditCardPayment("1234567890123456"))
print(f"  {cart.checkout()}")

cart.set_payment_method(PayPalPayment("user@email.com"))
print(f"  {cart.checkout()}")


# ============================================
# 5. OBSERVER
# ============================================
print("\n--- 5. OBSERVER ---")


class Subject(ABC):
    """Observable subject"""
    
    def __init__(self):
        self._observers: List['Observer'] = []
    
    def attach(self, observer: 'Observer'):
        self._observers.append(observer)
    
    def detach(self, observer: 'Observer'):
        self._observers.remove(observer)
    
    def notify(self, event: str):
        for observer in self._observers:
            observer.update(event)


class Observer(ABC):
    @abstractmethod
    def update(self, event: str):
        pass


class NewsAgency(Subject):
    def __init__(self):
        super().__init__()
        self._news: str = ""
    
    def publish_news(self, news: str):
        self._news = news
        self.notify(news)


class EmailSubscriber(Observer):
    def __init__(self, email: str):
        self.email = email
    
    def update(self, event: str):
        print(f"    Email to {self.email}: {event}")


class SMSSubscriber(Observer):
    def __init__(self, phone: str):
        self.phone = phone
    
    def update(self, event: str):
        print(f"    SMS to {self.phone}: {event[:20]}...")


# Test Observer
agency = NewsAgency()
agency.attach(EmailSubscriber("user@email.com"))
agency.attach(SMSSubscriber("+1234567890"))

print("  Publishing news:")
agency.publish_news("Breaking: Python 4.0 Released!")


# ============================================
# 6. DEPENDENCY INJECTION
# ============================================
print("\n--- 6. DEPENDENCY INJECTION ---")


class EmailService(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> bool:
        pass


class SMTPEmailService(EmailService):
    def send(self, to: str, message: str) -> bool:
        print(f"    Sending via SMTP to {to}: {message[:20]}...")
        return True


class MockEmailService(EmailService):
    def __init__(self):
        self.sent: List[tuple] = []
    
    def send(self, to: str, message: str) -> bool:
        self.sent.append((to, message))
        print(f"    Mock send to {to}")
        return True


class UserService:
    """Service with injected dependencies"""
    
    def __init__(self, email_service: EmailService):
        self._email_service = email_service
    
    def register_user(self, email: str, name: str) -> bool:
        # Registration logic...
        self._email_service.send(email, f"Welcome, {name}!")
        return True


# Production
print("  Production:")
user_service = UserService(SMTPEmailService())
user_service.register_user("user@test.com", "Alice")

# Testing
print("  Testing:")
mock_email = MockEmailService()
user_service = UserService(mock_email)
user_service.register_user("test@test.com", "Test")
print(f"    Emails sent: {len(mock_email.sent)}")


# ============================================
# 7. DECORATOR PATTERN
# ============================================
print("\n--- 7. DECORATOR PATTERN ---")


class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass


class SimpleCoffee(Coffee):
    def cost(self) -> float:
        return 2.0
    
    def description(self) -> str:
        return "Coffee"


class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee
    
    def cost(self) -> float:
        return self._coffee.cost()
    
    def description(self) -> str:
        return self._coffee.description()


class MilkDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return super().cost() + 0.5
    
    def description(self) -> str:
        return super().description() + " + Milk"


class SugarDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return super().cost() + 0.25
    
    def description(self) -> str:
        return super().description() + " + Sugar"


# Test Decorator
coffee = SimpleCoffee()
print(f"  {coffee.description()}: ${coffee.cost()}")

coffee_with_milk = MilkDecorator(coffee)
print(f"  {coffee_with_milk.description()}: ${coffee_with_milk.cost()}")

fancy_coffee = SugarDecorator(MilkDecorator(MilkDecorator(coffee)))
print(f"  {fancy_coffee.description()}: ${fancy_coffee.cost()}")


# ============================================
# 8. BUILDER
# ============================================
print("\n--- 8. BUILDER ---")


@dataclass
class Computer:
    cpu: str = ""
    ram: int = 0
    storage: int = 0
    gpu: str = ""
    
    def __str__(self):
        return f"Computer(CPU={self.cpu}, RAM={self.ram}GB, Storage={self.storage}GB, GPU={self.gpu})"


class ComputerBuilder:
    def __init__(self):
        self._computer = Computer()
    
    def set_cpu(self, cpu: str) -> 'ComputerBuilder':
        self._computer.cpu = cpu
        return self
    
    def set_ram(self, ram: int) -> 'ComputerBuilder':
        self._computer.ram = ram
        return self
    
    def set_storage(self, storage: int) -> 'ComputerBuilder':
        self._computer.storage = storage
        return self
    
    def set_gpu(self, gpu: str) -> 'ComputerBuilder':
        self._computer.gpu = gpu
        return self
    
    def build(self) -> Computer:
        return self._computer


# Test Builder
gaming_pc = (ComputerBuilder()
    .set_cpu("Intel i9")
    .set_ram(32)
    .set_storage(2000)
    .set_gpu("RTX 4090")
    .build())

print(f"  Built: {gaming_pc}")


print("\n✅ Day 21 completed!")
