import re
from config import qdrant
from core.embeddings import embedder

def query_documents(query: str, collection: str, top_k: int = 3):
    """
    Hybrid Qdrant search:
    1. Direct key lookup (e.g., DEVSUP-9443)
    2. Vector similarity
    3. Keyword fallback
    """
    query_vector = embedder.encode(query).tolist()
    query_normalized = query.replace("_", ".").lower().strip()

    # Detect Jira-like key patterns (e.g. DEVSUP-9443)
    jira_key_match = re.findall(r"\b[A-Z]{2,}-\d+\b", query.upper())

    if collection.lower() == "all":
        collections = ["bookstack", "jira"]
    else:
        collections = [collection]

    all_results = []

    for coll in collections:
        # 1️⃣ Direct Jira key lookup
        if jira_key_match and coll == "jira":
            print(f"🔎 Direct key match mode for {jira_key_match}")
            key_to_find = jira_key_match[0].strip().upper()

            points, _ = qdrant.scroll(
                collection_name=coll,
                limit=1000,
                with_payload=True,
            )

            for point in points:
                if str(point.payload.get("key", "")).upper() == key_to_find:
                    print(f"✅ Found Jira issue {key_to_find} in payloads.")
                    all_results.append({
                        "collection": coll,
                        "key": point.payload.get("key", ""),
                        "summary": point.payload.get("summary", ""),
                        "description": point.payload.get("description", ""),
                        "project": point.payload.get("project", ""),
                        "comments": point.payload.get("comments", ""),
                        "text": point.payload.get("text", ""),
                        "score": 1.0
                    })
            if all_results:
                return all_results  # direct return for key match

        # 2️⃣ Semantic (vector) search
        results = qdrant.query_points(
            collection_name=coll,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        # 3️⃣ Fallback keyword search
        if not results.points or len(results.points) == 0:
            print(f"⚠️ No semantic hits in {coll}, using keyword fallback...")
            points, _ = qdrant.scroll(
                collection_name=coll,
                limit=500,
                with_payload=True,
            )

            keyword_hits = []
            for point in points:
                combined_text = (
                    (point.payload.get("summary", "") + " " +
                     point.payload.get("description", "") + " " +
                     point.payload.get("comments", "")).lower()
                )
                if any(word in combined_text for word in query_normalized.split()):
                    keyword_hits.append(point)

            if keyword_hits:
                print(f"✅ Found {len(keyword_hits)} keyword matches in {coll}.")
                results.points = keyword_hits[:top_k]

        # 4️⃣ Normalize results
        for p in results.points:
            all_results.append({
                "collection": coll,
                "key": p.payload.get("key", ""),
                "summary": p.payload.get("summary", ""),
                "description": p.payload.get("description", ""),
                "project": p.payload.get("project", ""),
                "comments": p.payload.get("comments", ""),
                "assignee": p.payload.get("assignee", ""),
                "status": p.payload.get("status", ""),
                "text": p.payload.get("text", ""),
                "score": getattr(p, "score", 1.0),
            })

    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:top_k]


# 🆕 NEW: Direct user/project-based ticket fetch
def get_tickets_by_user_and_project(assignee: str, project: str):
    """
    Fetch Jira tickets directly from Qdrant filtered by assignee and project.
    """
    try:
        print(f"🔎 Fetching tickets for user={assignee}, project={project}")
        scroll = qdrant.scroll(
            collection_name="jira",
            scroll_filter={
                "must": [
                    {"key": "assignee", "match": {"value": assignee}},
                    {"key": "project", "match": {"value": project}},
                ]
            },
            limit=100,
            with_payload=True,
        )

        points = scroll[0]
        tickets = []
        for point in points:
            payload = point.payload
            tickets.append({
                "key": payload.get("key", ""),
                "summary": payload.get("summary", ""),
                "description": payload.get("description", ""),
                "status": payload.get("status", ""),
                "assignee": payload.get("assignee", ""),
                "project": payload.get("project", ""),
            })
        return tickets

    except Exception as e:
        print(f"❌ Error fetching tickets for {assignee}@{project}: {e}")
        return []

