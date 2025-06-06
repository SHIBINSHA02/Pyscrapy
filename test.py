from pyscrapy import get_gemini_key_value
from pyscrapy.commerce import formal_hello, formal_goodbye

print(get_gemini_key_value())    # chicking fiole path linking
print(formal_hello("Alice"))   # Output: Greetings, Alice. It is a pleasure to meet you.
print(formal_goodbye("Bob"))   # Output: Farewell, Bob. Until we meet again.