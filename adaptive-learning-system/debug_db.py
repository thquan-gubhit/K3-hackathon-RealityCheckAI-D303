from app.database import SessionLocal
from app.repositories.learning_repository import LearningRepository
from app.schemas.learning import LearningSessionCreate
db = SessionLocal()
try:
    from app.models.document import Document
    doc = db.query(Document).first()
    if not doc:
        print("No documents found in DB.")
    else:
        print(f"Using document {doc.id}")
        payload = LearningSessionCreate(user_id="local-user", document_id=str(doc.id))
        repo = LearningRepository(db)
        # Attempt to insert a session
        from app.models.learning_session import LearningSession
        import uuid
        
        db_record = LearningSession(
            id=str(uuid.uuid4()),
            user_id=payload.user_id,
            document_id=payload.document_id,
            status="ACTIVE"
        )
        db.add(db_record)
        db.commit()
        print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
