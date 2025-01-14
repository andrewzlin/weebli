from website import create_app
from scripts.populate_db import populate_anime_database, populate_manga_database

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)