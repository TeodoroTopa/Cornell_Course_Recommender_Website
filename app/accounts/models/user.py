from . import *

class User(db.Model):
  __tablename__ = 'users'

  email           = db.Column(db.String(128), nullable =False, unique =True, primary_key =True)
  fname           = db.Column(db.String(128), nullable =False)
  lname           = db.Column(db.String(128), nullable =False)

  def __init__(self, **kwargs):
    self.email           = kwargs.get('email', None)
    self.fname           = kwargs.get('fname', None)
    self.lname           = kwargs.get('lname', None)

  def __repr__(self):
    return str(self.__dict__)


class UserSchema(ModelSchema):
  class Meta:
    model = User
