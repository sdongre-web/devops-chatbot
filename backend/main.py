from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import pinecone, requests, os


load_dotenv()


app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))


class QueryRequest(BaseModel):
query: str


@app.post("/chat")
def chat(req: QueryRequest):
embedding = client.embeddings.create(
input=req.query,
model="text-embedding-3-small"
).data[0].embedding


results = index.query(vector=embedding, top_k=3, include_metadata=True)
if results.matches:
best = results.matches[0].metadata
return {"answer": f"🔎 I found this doc for you: [{best['title']}]({best['url']})"}
else:
return {"answer": "❌ No documentation found. Do you want me to create a Jira ticket?"}


@app.post("/create_ticket")
def create_ticket(req: QueryRequest):
auth = (os.getenv("JIRA_USER"), os.getenv("JIRA_TOKEN"))
headers = {"Content-Type": "application/json"}
payload = {
"fields": {
"project": {"key": os.getenv("JIRA_PROJECT_KEY")},
"summary": req.query,
"description": f"Raised via DevOps Chatbot: {req.query}",
"issuetype": {"name": "Task"}
}
}
res = requests.post(f"{os.getenv('JIRA_URL')}/rest/api/2/issue", auth=auth, headers=headers, json=payload)
return res.json()
