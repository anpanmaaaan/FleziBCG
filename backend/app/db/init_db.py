from app.db.base import Base
from app.db.session import engine

# ✅ Import ALL models here
from app.models.master import ProductionOrder, WorkOrder, Operation
from app.models.execution import ExecutionEvent

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()