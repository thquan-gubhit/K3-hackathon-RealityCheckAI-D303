from app.database import SessionLocal
from app.repositories.learning_repository import LearningRepository
import uuid

db = SessionLocal()
try:
    repo = LearningRepository(db)
    session = repo.create_session(
        user_id="foo",
        document_id=str(uuid.uuid4()),
        knowledge_unit_id=str(uuid.uuid4())
    )
    print("Success: Session created with ID", session.id)
except Exception as e:
    import traceback
    traceback.print_exc()
