from app import myapp_obj, db
with myapp_obj.app_context():
    db.drop_all()
    db.create_all()