from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    result_all = db.Column(JSON)

    def __init__(self, url, result_all):
        self.url = url
        self.result_all = result_all

    def __repr__(self):
        return '<id {}>'.format(self.id)

