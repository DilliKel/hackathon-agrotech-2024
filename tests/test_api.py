from agroscan.api import create_app


class StubClassifier:
    def diagnostico_e_tratamento(self, respostas):
        if not respostas:
            return {"error": "Respostas vazias ou inválidas"}
        return {
            "diagnostico": "Pragas do Solo",
            "tratamento_nivel_1": "Org",
            "tratamento_nivel_2": "Gen",
            "tratamento_nivel_3": "Agr",
        }


def test_health_endpoint():
    app = create_app(classifier=StubClassifier())
    client = app.test_client()

    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_index_page():
    app = create_app(classifier=StubClassifier())
    client = app.test_client()

    resp = client.get("/")
    assert resp.status_code == 200
    assert b"AgroScan" in resp.data


def test_diagnostico_endpoint():
    app = create_app(classifier=StubClassifier())
    client = app.test_client()

    resp = client.post("/diagnostico", json={"respostas": ["texto"]})
    assert resp.status_code == 200
    assert resp.get_json()["diagnostico"] == "Pragas do Solo"


def test_perguntas_endpoint():
    app = create_app(classifier=StubClassifier())
    client = app.test_client()

    resp = client.get("/perguntas")
    data = resp.get_json()

    assert resp.status_code == 200
    assert isinstance(data.get("perguntas"), list)
    assert len(data["perguntas"]) >= 1


def test_diagnostico_invalido():
    app = create_app(classifier=StubClassifier())
    client = app.test_client()

    resp = client.post("/diagnostico", json={"respostas": []})
    assert resp.status_code == 400
