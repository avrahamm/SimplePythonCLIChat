# Implement the Python code using the `openai` library to create the assistant.
# Start with a system prompt for the chat completion API.
# Send a static message and receive a response from the API.
# Show the chat completion message.

import os
from dotenv import load_dotenv

load_dotenv()

api_key=os.environ.get("OPENAI_API_KEY", None)
print(api_key) # will print 'openai_token'
