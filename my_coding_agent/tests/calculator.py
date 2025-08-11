# Simple calculator
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

if __name__ == "__main__":
    print("Simple Calculator")
    a = float(input("Enter first number: "))
    op = input("Enter operation (+, -, *, /): ")
    b = float(input("Enter second number: "))

    if op == "+":
        print(f"Result: {add(a, b)}")
    elif op == "-":
        print(f"Result: {subtract(a, b)}")
    elif op == "*":
        print(f"Result: {multiply(a, b)}")
    elif op == "/":
        print(f"Result: {divide(a, b)}")
    else:
        print("Invalid operation")