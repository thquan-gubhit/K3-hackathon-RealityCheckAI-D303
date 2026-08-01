from app.database import SessionLocal
from app.repositories.learning_repository import LearningRepository
from app.models.learning_session import LearningSession
from app.schemas.learning import SessionStatus
import uuid
import datetime

# The original create_session from the compiled .pyc is bugged. It misses knowledge_unit_id!
_original_create_session = LearningRepository.create_session

def patched_create_session(self, *, user_id: str, document_id: str, knowledge_unit_id: str) -> LearningSession:
    # We will just write the correct implementation here.
    # It probably looks like this:
    record = LearningSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        document_id=document_id,
        knowledge_unit_id=knowledge_unit_id,
        status=SessionStatus.ACTIVE,
        started_at=datetime.datetime.now(datetime.timezone.utc),
        main_question_count=0,
        remediation_question_count=0,
    )
    self.session.add(record)
    self.session.flush()
    return record

LearningRepository.create_session = patched_create_session

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
