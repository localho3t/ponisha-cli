import os
import signal
import threading
from flask import Flask, jsonify , render_template
from Apps.WebApp.config import Config
from Apps.WebApp.models import db, Project
from Apps.WebApp.worker_ponisha import ponisha_loop


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

def flask_app(profile_clean,me_clean):
    app = create_app()
    cfg = app.config
    stop_event = threading.Event()

    # Worker Thread
    worker = threading.Thread(
        target=ponisha_loop,
        args=(app, cfg, stop_event),
        daemon=True,
    )
    worker.start()

    # graceful shutdown
    def handle_sig(*_):
        print("Shutting down gracefully...")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    # Routes
    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/projects")
    def list_projects():
        q = Project.query.order_by(Project.inserted_at.desc()).limit(20).all()
        return jsonify([p.to_dict() for p in q])

    @app.get("/projects/<external_id>")
    def get_project(external_id: str):
        p = Project.query.filter_by(external_id=str(external_id)).first_or_404()
        return jsonify(p.to_dict())

    @app.get("/")
    def profile_page():

        return render_template("profile.html",
                               profile_clean=profile_clean,
                               me_clean=me_clean)

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = bool(int(os.getenv("DEBUG", "0")))

    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    finally:
        stop_event.set()
        worker.join(timeout=5)