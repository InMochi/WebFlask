"""Application entry point for local development."""

from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
