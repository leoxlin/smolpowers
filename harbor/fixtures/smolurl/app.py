import secrets

from flask import Flask, abort, request


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(DATABASE=None)
    app.config.update(config or {})
    links: dict[str, str] = {}

    @app.post("/links")
    def create_link():
        body = request.get_json(silent=True) or {}
        if not body.get("url"):
            return {"error": "url is required"}, 400

        code = secrets.token_urlsafe(4)
        links[code] = body["url"]
        return {"code": code, "url": body["url"]}, 201

    @app.get("/links")
    def list_links():
        return [{"code": code, "url": url} for code, url in links.items()]

    @app.get("/<code>")
    def follow_link(code: str):
        if code not in links:
            abort(404)
        return "", 302, {"Location": links[code]}

    @app.delete("/links/<code>")
    def delete_link(code: str):
        if code not in links:
            abort(404)
        del links[code]
        return "", 204

    return app


app = create_app()
