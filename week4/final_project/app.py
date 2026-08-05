"""Flask application for the Satellite Design Assistant."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Callable

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

from ai_api import (
    AIResponseError,
    AIServiceError,
    AIServiceUnavailable,
    analyze_mission,
    validate_ai_design,
)
from db import (
    delete_mission,
    get_knowledge,
    get_mission,
    init_database,
    list_missions,
    save_processed_mission,
)
from reports import generate_report


BASE_DIR = Path(__file__).resolve().parent


def _json_error(message: str, status: int):
    return jsonify({"error": message, "status": status}), status


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Application factory used by both the server and automated tests."""

    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_PATH=Path(os.getenv("DATABASE_PATH", BASE_DIR / "satellite.db")),
        KNOWLEDGE_BASE_PATH=Path(
            os.getenv("KNOWLEDGE_BASE_PATH", BASE_DIR / "knowledge_base.json")
        ),
        ANALYZER=analyze_mission,
        MAX_CONTENT_LENGTH=32 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    app.config["DATABASE_PATH"] = Path(app.config["DATABASE_PATH"])
    app.config["KNOWLEDGE_BASE_PATH"] = Path(app.config["KNOWLEDGE_BASE_PATH"])

    init_database(
        app.config["DATABASE_PATH"],
        app.config["KNOWLEDGE_BASE_PATH"],
    )
    CORS(app)

    def process_mission(description: str) -> dict[str, Any]:
        """Run the AI, knowledge retrieval, and transactional save pipeline."""

        analyzer: Callable[[str], dict[str, Any]] = app.config["ANALYZER"]
        recommendation = validate_ai_design(analyzer(description))
        knowledge = get_knowledge(app.config["DATABASE_PATH"], recommendation["mission_type"])
        if knowledge is None:
            raise LookupError(
                f"No engineering knowledge exists for {recommendation['mission_type']}."
            )

        mission_id = save_processed_mission(
            app.config["DATABASE_PATH"],
            description,
            recommendation,
        )
        saved_mission = get_mission(app.config["DATABASE_PATH"], mission_id)
        if saved_mission is None:
            raise sqlite3.DatabaseError("The saved mission could not be read back.")
        return saved_mission

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "satellite-design-assistant"})

    @app.post("/analyze")
    def analyze_route():
        if not request.is_json:
            return _json_error("Send a JSON body containing a description.", 400)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _json_error("The request body must be a JSON object.", 400)

        description = payload.get("description")
        if not isinstance(description, str):
            return _json_error("Description must be text.", 400)

        description = description.strip()
        if len(description) < 10:
            return _json_error("Describe the mission in at least 10 characters.", 400)
        if len(description) > 2000:
            return _json_error("Description must be 2,000 characters or fewer.", 400)

        try:
            return jsonify(process_mission(description)), 201
        except AIServiceUnavailable as error:
            return _json_error(str(error), 503)
        except (AIServiceError, AIResponseError) as error:
            return _json_error(str(error), 502)
        except LookupError as error:
            return _json_error(str(error), 422)
        except sqlite3.Error:
            app.logger.exception("Database failure while processing mission")
            return _json_error("The mission could not be saved. Try again.", 500)

    @app.get("/missions")
    def missions_route():
        try:
            return jsonify({"missions": list_missions(app.config["DATABASE_PATH"])})
        except sqlite3.Error:
            app.logger.exception("Database failure while listing missions")
            return _json_error("Mission history could not be loaded.", 500)

    @app.get("/mission/<int:mission_id>")
    def mission_route(mission_id: int):
        mission = get_mission(app.config["DATABASE_PATH"], mission_id)
        if mission is None:
            return _json_error("Mission not found.", 404)
        return jsonify(mission)

    @app.delete("/mission/<int:mission_id>")
    def delete_mission_route(mission_id: int):
        try:
            if not delete_mission(app.config["DATABASE_PATH"], mission_id):
                return _json_error("Mission not found.", 404)
            return jsonify({"message": "Mission deleted.", "mission_id": mission_id})
        except sqlite3.Error:
            app.logger.exception("Database failure while deleting mission")
            return _json_error("The mission could not be deleted.", 500)

    @app.get("/download/<int:mission_id>")
    def download_route(mission_id: int):
        mission = get_mission(app.config["DATABASE_PATH"], mission_id)
        if mission is None:
            return _json_error("Mission not found.", 404)

        report = generate_report(mission)
        from io import BytesIO

        return send_file(
            BytesIO(report),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"satellite-design-{mission_id}.pdf",
        )

    @app.errorhandler(404)
    def not_found(_error):
        return _json_error("Route not found.", 404)

    @app.errorhandler(413)
    def request_too_large(_error):
        return _json_error("Request body is too large.", 413)

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").strip().lower() == "true"
    app.run(host="127.0.0.1", port=port, debug=debug)

