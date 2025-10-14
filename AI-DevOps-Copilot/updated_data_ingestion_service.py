from utils.jira_connection import get_jira_client
from utils.db_connection import get_db_connection
from core.embeddings import embedder
from config import qdrant, ensure_collection, BOOKSTACK_COLLECTION, JIRA_COLLECTION
from qdrant_client.http import models


# -------------------------------
# 📘 Ingest Bookstack Data (MySQL)
# -------------------------------
def ingest_sql_data(book_ids=None):
    """Fetch Bookstack data from MySQL and insert into Qdrant."""
    ensure_collection(BOOKSTACK_COLLECTION)

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # ✅ Dynamic query with placeholders
    if book_ids:
        placeholders = ', '.join(['%s'] * len(book_ids))
        query = f"SELECT id, text FROM pages WHERE book_id IN ({placeholders})"
        cursor.execute(query, tuple(book_ids))
    else:
        cursor.execute("SELECT id, text FROM pages")

    rows = cursor.fetchall()

    if not rows:
        print("⚠️ No Bookstack data found.")
        cursor.close()
        db.close()
        return {"status": "no_data"}

    print(f"📄 Found {len(rows)} Bookstack records. Ingesting into Qdrant...")

    points = []
    for row in rows:
        text = row.get("text", "")
        if not text:
            continue

        try:
            vector = embedder.encode(text).tolist()
        except Exception as e:
            print(f"⚠️ Skipping ID {row['id']} (embedding failed): {e}")
            continue

        points.append(
            models.PointStruct(
                id=row["id"],
                vector=vector,
                payload={
                    "id": row["id"],
                    "text": text
                },
            )
        )

    try:
        qdrant.upsert(collection_name=BOOKSTACK_COLLECTION, points=points)
        print(f"✅ Ingested {len(points)} Bookstack pages into Qdrant.")
        status = {"status": "success", "count": len(points)}
    except Exception as e:
        print(f"❌ Qdrant upsert failed: {e}")
        status = {"status": "error", "details": str(e)}

    cursor.close()
    db.close()
    return status


# -------------------------------
# 🧩 Ingest Jira Data (API)
# -------------------------------
def ingest_jira_data():
    """Fetch Jira issues and insert into Qdrant."""
    ensure_collection(JIRA_COLLECTION)

    jira = get_jira_client()
    if not jira:
        print("⚠️ Jira connection failed.")
        return {"status": "jira_connection_failed"}

    jql_query = 'key = "DEVSUP-9375"'
    try:
        issues = jira.search_issues(jql_query, maxResults=1)
    except Exception as e:
        print(f"❌ Jira search failed: {e}")
        return {"status": "error", "details": str(e)}

    if not issues:
        print("⚠️ No Jira issues found.")
        return {"status": "no_data"}

    print(f"📄 Found {len(issues)} Jira issues. Ingesting into Qdrant...")

    points = []
    for issue in issues:
        issue_key = issue.key
        summary = getattr(issue.fields, "summary", "") or ""
        description = getattr(issue.fields, "description", "") or ""
        project_key = getattr(issue.fields.project, "key", "Unknown")

        # ---- Comments ----
        try:
            comments = jira.comments(issue)
            comments_text = "\n\n".join(
                [f"{c.author.displayName}: {c.body}" for c in comments]
            ) if comments else ""
        except Exception as e:
            print(f"⚠️ Failed to fetch comments for {issue_key}: {e}")
            comments_text = ""

        # ---- Full text ----
        full_text = (
            f"Issue Key: {issue_key}\n"
            f"Project: {project_key}\n"
            f"Summary: {summary}\n\n"
            f"Description:\n{description}\n\n"
            f"Comments:\n{comments_text}"
        )

        try:
            vector = embedder.encode(full_text).tolist()
        except Exception as e:
            print(f"⚠️ Skipping {issue_key} (embedding failed): {e}")
            continue

        points.append(
            models.PointStruct(
                id=abs(hash(issue_key)),
                vector=vector,
                payload={
                    "key": issue_key,
                    "summary": summary,
                    "description": description,
                    "project": project_key,
                    "comments": comments_text,
                },
            )
        )

    try:
        qdrant.upsert(collection_name=JIRA_COLLECTION, points=points)
        print(f"✅ Ingested {len(points)} Jira issues into Qdrant.")
        return {"status": "success", "count": len(points)}
    except Exception as e:
        print(f"❌ Qdrant upsert failed: {e}")
        return {"status": "error", "details": str(e)}
