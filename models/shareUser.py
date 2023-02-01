from config import db


class ShareUser(db.Model):
    __tablename__ = 'shareUser'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"))
