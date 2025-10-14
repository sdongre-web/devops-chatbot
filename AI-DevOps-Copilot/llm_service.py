import re
import google.generativeai as genai
from config import GEMINI_API_KEY
from services.qdrant_service import query_documents

# =======================================
# Initialize Gemini
# =======================================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel("gemini-2.0-flash")
else:
    llm_model = None
    print("⚠️ GEMINI_API_KEY not found!")


# =======================================
# Prompt Template Builder
# =======================================
def get_prompt_template(collection: str, question: str, context: str, mode: str):
    """Return an appropriate Gemini prompt template."""

    base_formatting = """
IMPORTANT FORMATTING RULES:
- Use markdown for structure.
- Keep responses concise and readable.
- Highlight key actions or steps with numbers/bullets.
"""

    # --- JIRA mode (summarization) ---
    if collection == "jira" and mode == "contextual":
        return f"""
You are an **AI DevOps Assistant** analyzing Jira ticket data.

You are provided with one or more Jira ticket descriptions and comments.

Your task:
1. Explain briefly (1–2 lines) what the ticket is about — start with: “This Jira ticket was raised to …”.
2. Summarize what actions, steps, or resolutions happened in the comments.
3. If steps exist, include them as short numbered items.
4. Do NOT include entire raw text, HTML, or ADF formatting.
5. End with **one clean list** of related Jira tickets.

Format example:

**🗂️ Jira Ticket:** <ticket key>  
**📝 Summary:**  
This Jira ticket was raised to address XYZ.  

**Key updates or actions:**  
1. Step one  
2. Step two  

---

Context:
{context}

User Question: {question}

{base_formatting}

Answer:
"""

    # --- BOOKSTACK mode ---
    if collection == "bookstack" and mode == "contextual":
        return f"""
You are a **technical documentation assistant** using Bookstack documentation.

Answer the user's question based on the given content.
If related Jira tickets are mentioned, list only their IDs at the end (do not show full ticket data).

Context:
{context}

Question: {question}

{base_formatting}

Answer:
"""

    # --- GENERAL fallback ---
    return f"""
You are a helpful DevOps assistant.

Question: {question}

{base_formatting}

Answer:
"""


# =======================================
# Intent Detection (optional fallback)
# =======================================
def detect_intent(question: str) -> str:
    q = question.lower()
    if re.search(r"(devsup|jira|ticket|issue|bug|story|incident|summary|comments)", q):
        return "jira"
    elif re.search(r"(how to|steps|create|configure|setup|deploy|release|git|terraform|ansible|kubernetes|aws|bookstack)", q):
        return "bookstack"
    else:
        return "general"


# =======================================
# Main LLM Function
# =======================================
def ask_llm(question: str, collection: str = None, top_k: int = 5):
    """
    Generate a Gemini response with smart handling for Jira, Bookstack, and general queries.
    """

    if not collection:
        collection = detect_intent(question)

    docs_with_scores = query_documents(question, collection, top_k)
    print(f"🔍 Collection: {collection} | Query: {question}")

    if not llm_model:
        return {"answer": "⚠️ Gemini API not configured.", "source": "error"}

    if not isinstance(docs_with_scores, list):
        docs_with_scores = list(docs_with_scores)

    # Build context
    context_blocks = []
    related_keys = set()

    for doc in docs_with_scores:
        if isinstance(doc, dict) and doc.get("score", 0) > 0.35:
            key = doc.get("key", "")
            if key:
                related_keys.add(key)
            if collection == "jira":
                text_data = "\n".join([
                    f"Key: {doc.get('key', '')}",
                    f"Summary: {doc.get('summary', '')}",
                    f"Description: {doc.get('description', '')}",
                    f"Comments: {doc.get('comments', '')}",
                ])
            else:
                # For Bookstack/general
                text_data = doc.get("text", "")
            context_blocks.append(text_data)

    try:
        # === Context found ===
        if context_blocks:
            context = "\n\n".join(context_blocks)
            prompt = get_prompt_template(collection, question, context, "contextual")
            response = llm_model.generate_content(prompt)
            answer_text = response.text.strip()

            # Append related Jira tickets ONCE
            if collection == "jira" and related_keys:
                answer_text += "\n\n**📎 Related Jira Tickets:**\n" + "\n".join(
                    [f"- {k}" for k in sorted(related_keys)]
                )

            return {"answer": answer_text, "source": "database"}

        # === No relevant data found ===
        else:
            prompt = get_prompt_template(collection, question, "", "general")
            response = llm_model.generate_content(prompt)
            return {"answer": response.text, "source": "llm_knowledge"}

    except Exception as e:
        return {"answer": f"❌ Error generating response: {e}", "source": "error"}

