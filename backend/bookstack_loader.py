import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
import pinecone


load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))


headers = {"Authorization": f"Token {os.getenv('BOOKSTACK_TOKEN')}", "Content-Type": "application/json"}
url = f"{os.getenv('BOOKSTACK_URL')}/api/pages"
response = requests.get(url, headers=headers)
pages = response.json()['data']


def embed_bookstack():
for page in pages:
title = page['name']
id_ = page['id']
url = page['url']
content = page['html'] # or fetch full HTML/content


embedding = client.embeddings.create(
input=content,
model="text-embedding-3-small"
).data[0].embedding


index.upsert([(str(id_), embedding, {"title": title, "url": url})])


if __name__ == '__main__':
embed_bookstack()
