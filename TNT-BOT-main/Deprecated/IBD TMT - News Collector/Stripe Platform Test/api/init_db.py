from index import app, db

with app.app_context():
    db.create_all()
    print("数据库已创建")