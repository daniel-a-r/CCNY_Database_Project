from flask_app import app, mysql
from flask_app.models import query

if __name__ == '__main__':
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close()
    app.run(debug=True)