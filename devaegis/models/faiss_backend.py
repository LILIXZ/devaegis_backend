import uuid

from sqlalchemy.dialects.postgresql import UUID

from devaegis.extensions import db


class FaissIndex(db.Model):
    __tablename__ = "faiss_index"
    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    index_data = db.Column(db.LargeBinary)

    def __repr__(self):
        return f"{self.id}"
