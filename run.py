# Local application imports
from app import create_app

if __name__ == "__main__":
    app = create_app()

    host = app.config.get("HOST")
    port = app.config.get("PORT")

    app.run(host=host, port=port)
