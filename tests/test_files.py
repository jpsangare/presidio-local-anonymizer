"""Anonymisation de fichiers (/api/files/*)."""

import base64

import pytest


def post_file(client, filename, data: bytes, **extra):
    payload = {"filename": filename, "content": base64.b64encode(data).decode(), **extra}
    return client.post("/api/files/anonymize", json=payload)


def test_formats_always_include_text_files(client):
    body = client.get("/api/files/formats").get_json()

    assert {".txt", ".md", ".csv"} <= set(body["extensions"])
    assert isinstance(body["docling"], bool)


def test_unsupported_extension_returns_415(client, models_ready):
    assert post_file(client, "virus.exe", b"MZ").status_code == 415


def test_invalid_base64_returns_400(client, models_ready):
    response = client.post("/api/files/anonymize", json={"filename": "a.txt", "content": "@@@"})

    assert response.status_code == 400


def test_empty_file_returns_400(client, models_ready):
    assert post_file(client, "a.txt", b"").status_code == 400


@pytest.mark.models
class TestTextFiles:
    @pytest.fixture(autouse=True)
    def _need_models(self, models_ready, isolated_store):
        pass

    def test_text_file_is_anonymized_and_renamed(self, client):
        body = post_file(client, "CV_Jean_Dupont.txt", "Contact : jean.dupont@exemple.fr".encode()).get_json()

        assert body["anonymized_text"] == f"Contact : [EMAIL_1_{body['ts']}]"
        # Le nom d'origine, souvent nominatif, n'est pas repris
        assert body["output_filename"] == f"document-{body['ts']}-anonymise.txt"
        assert body["source_format"] == "txt"

    def test_windows_1252_text_is_decoded(self, client):
        body = post_file(client, "note.csv", "nom;mail\nÉlise;elise@exemple.fr".encode("cp1252")).get_json()

        assert body["anonymized_text"].startswith("nom;mail\n")
        assert "�" not in body["anonymized_text"]
        assert "elise@exemple.fr" not in body["anonymized_text"]

    def test_file_shares_tokens_with_its_workspace(self, client):
        workspace_id = client.post("/api/workspaces", json={"name": "Projet"}).get_json()["id"]

        first = post_file(client, "a.md", b"jean@example.com", workspace_id=workspace_id).get_json()
        second = client.post(
            "/api/anonymize", json={"text": "Question sur jean@example.com", "workspace_id": workspace_id}
        ).get_json()

        assert second["anonymized_text"] == f"Question sur {first['anonymized_text']}"

    def test_unknown_workspace_returns_404(self, client):
        response = post_file(client, "a.txt", b"jean@example.com", workspace_id="00_01_01_00_00_00")

        assert response.status_code == 404


@pytest.mark.models
def test_docx_is_converted_to_markdown(client, models_ready, isolated_store):
    docx = pytest.importorskip("docx")
    pytest.importorskip("docling")
    import io

    document = docx.Document()
    document.add_heading("Compte rendu", level=1)
    document.add_paragraph("Contact : jean.dupont@exemple.fr")
    document.add_paragraph("Cabinet De La Tour & Associés, dossier ref_interne")
    buffer = io.BytesIO()
    document.save(buffer)

    body = post_file(client, "rapport.docx", buffer.getvalue()).get_json()

    assert body["output_filename"].endswith(".md")
    assert "# Compte rendu" in body["anonymized_text"]
    assert "jean.dupont@exemple.fr" not in body["anonymized_text"]
    # Ni « &amp; » ni « \_ » : le Markdown n'est pas échappé
    assert "&amp;" not in body["anonymized_text"]
    assert "ref_interne" in body["anonymized_text"]
