from extensions import ma
from models.faiss_backend import FaissIndex


class FaissIndexSchema(ma.SQLAlchemySchema):
    class Meta:
        model = FaissIndex

    id = ma.auto_field()
    index_data = ma.auto_field()
