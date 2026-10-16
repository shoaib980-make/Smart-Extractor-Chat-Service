
import tiktoken

text = """
I am building a Smart Extractor and Chat Service
using Python, Node.js, and Large Language Models.
"""

# Use a tokenizer encoding commonly associated with GPT models.
encoding = tiktoken.get_encoding("cl100k_base")

tokens = encoding.encode(text)

print("Original text:")
print(text)

print("Token count:", len(tokens))
print("Token IDs:", tokens)
print("Decoded text:", encoding.decode(tokens))
