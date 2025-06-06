from pyscrapy import say_hello, say_goodbye
from pyscrapy.ecommerce import formal_hello, formal_goodbye

print(say_hello("Alice"))      # Output: Hello, Alice!
print(say_goodbye("Bob"))      # Output: Goodbye, Bob!
print(formal_hello("Alice"))   # Output: Greetings, Alice. It is a pleasure to meet you.
print(formal_goodbye("Bob"))   # Output: Farewell, Bob. Until we meet again.