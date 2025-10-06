from utils.db_connection import get_db_connection
from core.embeddings import embedder
from config import qdrant, COLLECTION_NAME,ensure_collection
from qdrant_client.http import models

def ingest_sql_data():
    """Fetch data from SQL and insert into Qdrant."""
    # db = get_db_connection()
    # cursor = db.cursor(dictionary=True)

    # # Fetch your desired data
    # cursor.execute("SELECT id, title, content FROM documents")
    # rows = cursor.fetchall()

    # if not rows:
    #     print("⚠️ No data found in SQL table.")
    #     return

    # print(f"📄 Found {len(rows)} records. Starting ingestion...")

    # points = []
    # for row in rows:
    #     text = f"{row['title']} {row['content']}"
    #     vector = embedder.encode(text).tolist()
    #     points.append(
    #         models.PointStruct(
    #             id=row["id"],
    #             vector=vector,
    #             payload={
    #                 "id": row["id"],
    #                 "title": row["title"],
    #                 "content": row["content"],
    #                 "text": text
    #             }
    #         )
    #     )

    # # Insert in bulk for efficiency
    # qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    # print(f"✅ Successfully ingested {len(rows)} documents into Qdrant.")
    ensure_collection()
    demo_documents = [
        {
            "id": 1,
            "title": "Docker Basics",
            "content": "Docker is a containerization platform that packages applications with their dependencies. Use docker build to create images and docker run to start containers."
        },
        {
            "id": 2,
            "title": "Kubernetes Deployment",
            "content": "Kubernetes orchestrates containers across multiple hosts. Use kubectl apply to deploy resources. Pods are the smallest deployable units containing one or more containers."
        },
        {
            "id": 3,
            "title": "CI/CD with Jenkins",
            "content": "Jenkins automates build, test, and deployment pipelines. Create a Jenkinsfile to define pipeline stages. Use webhooks to trigger builds on code commits."
        },
        {
            "id": 4,
            "title": "Terraform Infrastructure",
            "content": "Terraform manages infrastructure as code. Define resources in .tf files. Run terraform plan to preview changes and terraform apply to create resources."
        },
        {
            "id": 5,
            "title": "Monitoring with Prometheus",
            "content": "Prometheus collects and stores metrics as time series data. Configure scrape targets in prometheus.yml. Use PromQL to query metrics and Grafana for visualization."
        }
    ]
    
    print(f"📄 Ingesting {len(demo_documents)} demo documents...")
    
    points = []
    for doc in demo_documents:
        text = f"{doc['title']} {doc['content']}"
        vector = embedder.encode(text).tolist()
        points.append(
            models.PointStruct(
                id=doc["id"],
                vector=vector,
                payload={
                    "id": doc["id"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "text": text
                }
            )
        )
    
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Successfully ingested {len(demo_documents)} documents into Qdrant.")
