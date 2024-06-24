# retrieval-api
 Retrieval API that utilizes llama-index 

# Installation
`pip install -r requirements.txt`

# Startup
`uvicorn main:app --reload`

# Access
http://localhost:8000/docs

# Loaders
`PDF` `DOCX` `IPYNB`

# Swagger UI
- Start with load/pdf
- Namespace = name of vector database. Will need later for query
- Upload file

- 2nd Retrival/Query
- Prompt: Update to question to be asked (ie: What is the summary?)
- namespace: name of vector databsae created or to be queryied
- temeprature: leave as is

# TODO
- Add API endpoint for chatting with content (chat history etc.) ref. https://gpt-index.readthedocs.io/en/stable/core_modules/query_modules/chat_engines/usage_pattern.html
- Add more loaders
- Create dynamic loader for files (one endpoint)
