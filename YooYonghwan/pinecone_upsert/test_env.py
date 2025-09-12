import os
from dotenv import load_dotenv

load_dotenv()

print("Current directory:", os.getcwd())
print("PINECONE_API_KEY:", os.getenv('PINECONE_API_KEY'))
print("OPEN_API_KEY:", os.getenv('OPEN_API_KEY'))

# .env 파일 읽기
try:
    with open('.env', 'r') as f:
        print("\n.env file contents:")
        print(f.read())
except Exception as e:
    print(f"Error reading .env: {e}")