"""
Code Snippets and Quick Generation Tools for CodeBuddy
"""
from typing import Dict, List, Optional, Any


class CodeSnippetTool:
    """Generate common code snippets and patterns"""
    
    def execute(self, snippet_type: str, **kwargs) -> str:
        """Generate a code snippet"""
        try:
            snippets = {
                # Python patterns
                'singleton': self._singleton_pattern,
                'factory': self._factory_pattern,
                'decorator': self._decorator_pattern,
                'context_manager': self._context_manager_pattern,
                'property': self._property_pattern,
                'dataclass': self._dataclass_pattern,
                'enum': self._enum_pattern,
                
                # Common functions
                'file_reader': self._file_reader_snippet,
                'json_handler': self._json_handler_snippet,
                'error_handler': self._error_handler_snippet,
                'logger': self._logger_snippet,
                'config_loader': self._config_loader_snippet,
                'retry_decorator': self._retry_decorator_snippet,
                'timer_decorator': self._timer_decorator_snippet,
                
                # Data structures
                'linked_list': self._linked_list_snippet,
                'binary_tree': self._binary_tree_snippet,
                'queue': self._queue_snippet,
                'stack': self._stack_snippet,
                
                # Algorithms
                'binary_search': self._binary_search_snippet,
                'quicksort': self._quicksort_snippet,
                'fibonacci': self._fibonacci_snippet,
                
                # Web/API
                'flask_route': self._flask_route_snippet,
                'fastapi_route': self._fastapi_route_snippet,
                'requests_wrapper': self._requests_wrapper_snippet,
            }
            
            if snippet_type not in snippets:
                available = ', '.join(sorted(snippets.keys()))
                return f"❌ Snippet '{snippet_type}' not found. Available: {available}"
            
            snippet_func = snippets[snippet_type]
            code = snippet_func(**kwargs)
            
            return f"✅ Generated {snippet_type} snippet:\n\n```python\n{code}\n```"
            
        except Exception as e:
            return f"❌ Snippet generation failed: {e}"
    
    def _singleton_pattern(self, class_name: str = "Singleton", **kwargs) -> str:
        """Singleton design pattern"""
        return f'''class {class_name}:
    """Singleton pattern implementation"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # Initialize only once
            self._initialized = True
            # Add initialization code here
    
    def reset(self):
        """Reset singleton instance (useful for testing)"""
        self.__class__._instance = None
        self.__class__._initialized = False


# Usage
instance1 = {class_name}()
instance2 = {class_name}()
print(instance1 is instance2)  # True
'''
    
    def _factory_pattern(self, **kwargs) -> str:
        """Factory design pattern"""
        return '''from abc import ABC, abstractmethod
from typing import Dict, Type


class Product(ABC):
    """Abstract product interface"""
    
    @abstractmethod
    def operation(self) -> str:
        pass


class ConcreteProductA(Product):
    """Concrete product A"""
    
    def operation(self) -> str:
        return "Result from Product A"


class ConcreteProductB(Product):
    """Concrete product B"""
    
    def operation(self) -> str:
        return "Result from Product B"


class ProductFactory:
    """Factory for creating products"""
    
    _products: Dict[str, Type[Product]] = {
        'A': ConcreteProductA,
        'B': ConcreteProductB,
    }
    
    @classmethod
    def create_product(cls, product_type: str) -> Product:
        """Create product by type"""
        if product_type not in cls._products:
            raise ValueError(f"Unknown product type: {product_type}")
        
        product_class = cls._products[product_type]
        return product_class()
    
    @classmethod
    def register_product(cls, product_type: str, product_class: Type[Product]):
        """Register new product type"""
        cls._products[product_type] = product_class


# Usage
factory = ProductFactory()
product_a = factory.create_product('A')
product_b = factory.create_product('B')

print(product_a.operation())  # Result from Product A
print(product_b.operation())  # Result from Product B
'''
    
    def _decorator_pattern(self, decorator_name: str = "my_decorator", **kwargs) -> str:
        """Decorator pattern"""
        return f'''import functools
from typing import Callable, Any


def {decorator_name}(func: Callable = None, *, arg1: str = "default"):
    """
    A flexible decorator that can be used with or without arguments
    
    Usage:
        @{decorator_name}
        def my_func(): pass
        
        @{decorator_name}(arg1="custom")
        def my_func(): pass
    """
    def decorator_wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Pre-execution logic
            print(f"Before calling {{func.__name__}} with arg1={{arg1}}")
            
            try:
                # Call original function
                result = func(*args, **kwargs)
                
                # Post-execution logic
                print(f"After calling {{func.__name__}}")
                return result
                
            except Exception as e:
                # Error handling
                print(f"Error in {{func.__name__}}: {{e}}")
                raise
        
        return wrapper
    
    if func is None:
        # Decorator called with arguments: @{decorator_name}(arg1="value")
        return decorator_wrapper
    else:
        # Decorator called without arguments: @{decorator_name}
        return decorator_wrapper(func)


# Usage examples
@{decorator_name}
def simple_function():
    return "Hello, World!"

@{decorator_name}(arg1="custom_value")
def parameterized_function(x: int) -> int:
    return x * 2

# Test the decorated functions
result1 = simple_function()
result2 = parameterized_function(5)
'''
    
    def _context_manager_pattern(self, class_name: str = "MyContextManager", **kwargs) -> str:
        """Context manager pattern"""
        return f'''from typing import Optional, Any


class {class_name}:
    """Context manager implementation"""
    
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.resource: Optional[Any] = None
    
    def __enter__(self):
        """Enter the context - acquire resource"""
        print(f"Acquiring resource: {{self.resource_name}}")
        # Simulate resource acquisition
        self.resource = f"Resource({{self.resource_name}})"
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context - release resource"""
        print(f"Releasing resource: {{self.resource_name}}")
        
        if exc_type is not None:
            print(f"Exception occurred: {{exc_type.__name__}}: {{exc_val}}")
            # Return False to propagate exception
            return False
        
        # Cleanup
        self.resource = None
        return True


# Function-based context manager using contextlib
from contextlib import contextmanager

@contextmanager
def managed_resource(resource_name: str):
    """Function-based context manager"""
    print(f"Setting up {{resource_name}}")
    resource = f"Resource({{resource_name}})"
    
    try:
        yield resource
    finally:
        print(f"Cleaning up {{resource_name}}")


# Usage examples
with {class_name}("database_connection") as db:
    print(f"Using resource: {{db}}")

with managed_resource("file_handle") as file:
    print(f"Using resource: {{file}}")
'''
    
    def _property_pattern(self, **kwargs) -> str:
        """Property pattern with getter, setter, deleter"""
        return '''class PropertyExample:
    """Example class demonstrating property usage"""
    
    def __init__(self):
        self._value = None
        self._computed_cache = None
    
    @property
    def value(self):
        """Getter for value property"""
        return self._value
    
    @value.setter
    def value(self, new_value):
        """Setter for value property with validation"""
        if new_value is not None and new_value < 0:
            raise ValueError("Value must be non-negative")
        
        self._value = new_value
        # Clear cache when value changes
        self._computed_cache = None
    
    @value.deleter
    def value(self):
        """Deleter for value property"""
        self._value = None
        self._computed_cache = None
    
    @property
    def computed_value(self):
        """Read-only computed property with caching"""
        if self._computed_cache is None:
            if self._value is not None:
                self._computed_cache = self._value ** 2
            else:
                self._computed_cache = 0
        return self._computed_cache
    
    @property
    def is_positive(self) -> bool:
        """Boolean property"""
        return self._value is not None and self._value > 0


# Usage
obj = PropertyExample()
obj.value = 5
print(obj.value)           # 5
print(obj.computed_value)  # 25
print(obj.is_positive)     # True

del obj.value
print(obj.value)           # None
print(obj.computed_value)  # 0
'''
    
    def _dataclass_pattern(self, class_name: str = "DataExample", **kwargs) -> str:
        """Dataclass pattern"""
        return f'''from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class {class_name}:
    """Example dataclass with various field types"""
    
    # Required fields
    name: str
    age: int
    
    # Optional fields with defaults
    email: Optional[str] = None
    active: bool = True
    
    # Field with factory default (for mutable defaults)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Field with custom initialization
    created_at: datetime = field(default_factory=datetime.now)
    
    # Field excluded from repr
    internal_id: str = field(default="", repr=False)
    
    # Field excluded from comparison
    last_accessed: Optional[datetime] = field(default=None, compare=False)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Validate data
        if self.age < 0:
            raise ValueError("Age cannot be negative")
        
        # Set computed fields
        if not self.internal_id:
            self.internal_id = f"{{self.name.lower().replace(' ', '_')}}_{{self.age}}"
    
    def add_tag(self, tag: str):
        """Add a tag to the tags list"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def update_metadata(self, key: str, value: Any):
        """Update metadata"""
        self.metadata[key] = value
        self.last_accessed = datetime.now()


# Usage
person = {class_name}(
    name="John Doe",
    age=30,
    email="john@example.com"
)

person.add_tag("developer")
person.update_metadata("department", "engineering")

print(person)
print(f"Internal ID: {{person.internal_id}}")
'''
    
    def _file_reader_snippet(self, **kwargs) -> str:
        """File reading utility"""
        return '''import os
from typing import List, Optional, Generator
from pathlib import Path


class FileReader:
    """Utility class for reading files safely"""
    
    @staticmethod
    def read_text(filepath: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read entire text file"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None
        except UnicodeDecodeError:
            print(f"Encoding error reading {filepath}")
            return None
    
    @staticmethod
    def read_lines(filepath: str, encoding: str = 'utf-8') -> List[str]:
        """Read file lines into list"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return [line.rstrip('\\n\\r') for line in f]
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return []
    
    @staticmethod
    def read_lines_generator(filepath: str, encoding: str = 'utf-8') -> Generator[str, None, None]:
        """Read file lines as generator (memory efficient)"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                for line in f:
                    yield line.rstrip('\\n\\r')
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Check if file exists"""
        return Path(filepath).is_file()
    
    @staticmethod
    def get_file_size(filepath: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return None


# Usage examples
reader = FileReader()

# Read entire file
content = reader.read_text("example.txt")
if content:
    print(f"File content: {content[:100]}...")

# Read lines
lines = reader.read_lines("example.txt")
print(f"Number of lines: {len(lines)}")

# Memory-efficient reading for large files
for line_num, line in enumerate(reader.read_lines_generator("large_file.txt"), 1):
    if line_num > 10:  # Process only first 10 lines
        break
    print(f"Line {line_num}: {line}")
'''
