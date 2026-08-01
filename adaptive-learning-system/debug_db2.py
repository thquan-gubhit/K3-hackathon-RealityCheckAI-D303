from app.main import app  # This applies the monkey patch
from app.database import SessionLocal
from app.workflows.adaptive_learning import AdaptiveLearningWorkflow
from app.config import get_settings
from app.schemas.learning import LearningSessionCreate

db = SessionLocal()
settings = get_settings()
# Pass a dummy llm_client
class DummyLLM:
    def generate(self, *args, **kwargs):
        pass
    def generate_structured(self, *args, **kwargs):
        pass

wf = AdaptiveLearningWorkflow(settings=settings, llm_client=DummyLLM())
try:
    from app.models.document import Document
    doc = db.query(Document).filter(Document.status == "ready").first()
    if not doc:
        print("No documents found in DB.")
    else:
        print(f"Using document {doc.id}")
        payload = LearningSessionCreate(user_id="local-user", document_id=str(doc.id))
        session = wf.create_session(db, payload)
        db.commit()
        print("Success! Session ID:", session.id)
except Exception as e:
    import traceback
    traceback.print_exc()
