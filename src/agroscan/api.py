from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .classifier import AgroScanClassifier


DEFAULT_BASE_CSV = Path("AgroScan_API") / "Base.csv"
DEFAULT_CULTURAS_CSV = Path("AgroScan_API") / "Culturas_e_pragas.csv"


def create_app(
    classifier: AgroScanClassifier | None = None,
    base_csv_path: str | Path = DEFAULT_BASE_CSV,
    culturas_csv_path: str | Path = DEFAULT_CULTURAS_CSV,
) -> Flask:
    app = Flask(__name__)
    clf = classifier or AgroScanClassifier.from_csv(base_csv_path, culturas_csv_path)

    if hasattr(clf, "data") and hasattr(clf.data, "df_base") and hasattr(clf.data, "diag_base_col"):
        perguntas = [
            col for col in clf.data.df_base.columns if col != clf.data.diag_base_col
        ]
    else:
        perguntas = [
            "Qual cultura esta sendo atacada?",
            "Quais sintomas voce esta observando?",
            "Houve mudancas recentes no solo ou clima?",
        ]

    @app.get("/")
    def index():
        return render_template("index.html", perguntas=perguntas)

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok", "service": "AgroScan API"}, 200

    @app.post("/diagnostico")
    def diagnostico():
        body = request.get_json(silent=True) or {}
        respostas = body.get("respostas")

        if not isinstance(respostas, list) or not respostas:
            return jsonify({"error": "Respostas não fornecidas"}), 400

        resultado = clf.diagnostico_e_tratamento(respostas)
        status = 400 if "error" in resultado else 200
        return jsonify(resultado), status

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
