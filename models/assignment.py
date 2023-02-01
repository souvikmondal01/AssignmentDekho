from config import db


class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    filelink = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.String(200), nullable=False)
    upload_time = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    shareUser = db.relationship('ShareUser', backref='assignment')
