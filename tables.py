from app import myapp_obj, db
from app.models import User, Event

with myapp_obj.app_context():
    db.drop_all()
    db.create_all()
    # new = User(fname = 'a', lname = 'a', username = 'a', email = 'a', file= 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx8RMuY1dAjfCP6vKGir7SOM0qT8RDFwy8HA&s', data= 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx8RMuY1dAjfCP6vKGir7SOM0qT8RDFwy8HA&s'.read(), picApprove = 1, roleApprove = 1,reg_role = 'admin', act_role = 'admin')
    # new.set_password('a')
    # db.session.add(new)
    # db.session.commit()
    # figure out how to read file data to add users by default when drop data
    