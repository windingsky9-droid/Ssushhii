from flask import Flask, jsonify, request

from src.pricing import public_pricing
from src.research import get_research_provider, normalize_ticker


def create_app(provider=None) -> Flask:
    app = Flask(__name__)
    research_provider = provider or get_research_provider()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/config")
    def config():
        return jsonify(public_pricing())

    @app.get("/api/research")
    def research():
        try:
            ticker = normalize_ticker(request.args.get("ticker", ""))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        try:
            payload = research_provider.research(ticker)
        except Exception:
            app.logger.exception("Research provider request failed")
            return jsonify({"error": "Research is temporarily unavailable."}), 503
        return jsonify(payload)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
