"""Espaces de travail : jetons stables d'un texte à l'autre (RAG des LLM cloud)."""

import re

import pytest

TOKEN = re.compile(r"\[[A-Z_]+_\d+_(?:\d{2}_){5}\d{2}\]")


def create(client, name="Dossier test"):
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 201
    return response.get_json()["id"]


def test_create_requires_a_name(client, isolated_store):
    assert client.post("/api/workspaces", json={"name": "  "}).status_code == 400


def test_create_list_and_delete(client, isolated_store):
    workspace_id = create(client, "Lémanis")

    listed = client.get("/api/workspaces").get_json()["workspaces"]
    assert [(w["id"], w["name"], w["count"]) for w in listed] == [(workspace_id, "Lémanis", 0)]

    assert client.delete(f"/api/workspaces/{workspace_id}").status_code == 200
    assert client.get("/api/workspaces").get_json()["workspaces"] == []
    assert client.delete(f"/api/workspaces/{workspace_id}").status_code == 404


def test_workspace_ids_never_collide(client, isolated_store):
    assert len({create(client) for _ in range(3)}) == 3


def test_values_are_encrypted_on_disk(client, isolated_store, models_ready):
    workspace_id = create(client)
    client.post("/api/anonymize", json={"text": "jean@example.com", "workspace_id": workspace_id})

    assert "jean@example.com" not in (isolated_store / "workspaces.json").read_text(encoding="utf-8")


def test_unknown_workspace_returns_404(client, isolated_store):
    response = client.post("/api/anonymize", json={"text": "bonjour", "workspace_id": "00_01_01_00_00_00"})

    assert response.status_code == 404


@pytest.mark.models
class TestStableTokens:
    @pytest.fixture(autouse=True)
    def _need_models(self, models_ready, isolated_store):
        pass

    def anonymize(self, client, text, workspace_id):
        return client.post("/api/anonymize", json={"text": text, "workspace_id": workspace_id}).get_json()

    def test_same_value_gets_same_token_across_texts(self, client):
        workspace_id = create(client)

        first = self.anonymize(client, "Écrire à jean.dupont@exemple.fr", workspace_id)
        second = self.anonymize(client, "Copie : JEAN.DUPONT@exemple.fr et marie@exemple.fr", workspace_id)

        token = TOKEN.search(first["anonymized_text"]).group()
        assert token.endswith(f"_{workspace_id}]")
        assert second["anonymized_text"].startswith(f"Copie : {token} et ")
        assert first["ts"] == second["ts"] == workspace_id

    def test_numbering_continues_after_existing_tokens(self, client):
        workspace_id = create(client)

        self.anonymize(client, "a@exemple.fr", workspace_id)
        second = self.anonymize(client, "b@exemple.fr", workspace_id)

        assert second["anonymized_text"] == f"[EMAIL_2_{workspace_id}]"

    def test_deanonymize_with_workspace_id(self, client):
        workspace_id = create(client)
        self.anonymize(client, "Écrire à jean.dupont@exemple.fr", workspace_id)
        reply = self.anonymize(client, "et à marie@exemple.fr", workspace_id)["anonymized_text"]

        body = client.post(
            "/api/deanonymize",
            json={"ts": workspace_id, "text": f"[EMAIL_1_{workspace_id}] puis {reply}"},
        ).get_json()

        assert body["deanonymized_text"] == "jean.dupont@exemple.fr puis et à marie@exemple.fr"

    def test_without_workspace_tokens_stay_per_session(self, client):
        first = client.post("/api/anonymize", json={"text": "a@exemple.fr"}).get_json()
        second = client.post("/api/anonymize", json={"text": "a@exemple.fr"}).get_json()

        assert first["ts"] != second["ts"]
        assert first["workspace_id"] is None
