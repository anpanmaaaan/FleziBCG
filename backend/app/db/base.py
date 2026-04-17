from sqlalchemy.orm import DeclarativeBase


# INTENT: Single shared DeclarativeBase for all models. Every ORM model
# inherits from this class so that Base.metadata.create_all() discovers
# all tables in one call.
class Base(DeclarativeBase):
    pass
