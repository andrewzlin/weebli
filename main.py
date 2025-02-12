from website import create_app
from scripts.populate_db import populate_anime_database, populate_manga_database
from scripts.refresh_access_tokens import refresh_access_tokens

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

# remove the populate from auth and instantly direct user to an
# interactive loading screen 