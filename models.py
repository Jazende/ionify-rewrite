from gino import Gino

db = Gino()

class Song(db.model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    
