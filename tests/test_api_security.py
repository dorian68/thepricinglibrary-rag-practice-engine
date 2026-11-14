from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import time

from fastapi.testclient import TestClient

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.integrations import _default_documents_root
from pricinglibrary_rag.security import (
    ApiSecurity,
    SQLiteRateLimiter,
    mint_session_token,
    verify_session_token,
)


MEMBER_KEY = "member_" + "m" * 40
OPERATOR_KEY = "operator_" + "o" * 40
AUTH_SECRET = "identity_" + "s" * 40


def _settings(tmp_path: Path, **overrides) -> Settings:
    base = Settings(
        data_dir=tmp_path,
        db_path=tmp_path / "security.sqlite3",
        embedding_backend="local-hashing",
        embedding_dim=64,
        sentence_transformer_model=None,
        llm_provider="template",
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        openai_base_url=None,
        openai_timeout_seconds=10,
        openai_max_retries=0,
        ollama_url="http://localhost:11434",
        ollama_model="dummy",
        transformers_model_path=None,
        chunk_target_chars=700,
        chunk_overlap_chars=80,
        max_context_chunks=4,
        environment="production",
        api_key=MEMBER_KEY,
        operator_api_key=OPERATOR_KEY,
        auth_token_secret=AUTH_SECRET,
        rate_limit_per_min=100,
        source_rights_cleared=True,
    )
    return replace(base, **overrides)


def _client(settings: Settings) -> TestClient:
    return TestClient(create_app(build_services(settings)))


def test_production_missing_security_fails_closed_but_public_reads_work(tmp_path: Path) -> None:
    client = _client(
        _settings(
            tmp_path,
            api_key=None,
            operator_api_key=None,
            auth_token_secret=None,
            rate_limit_per_min=0,
        )
    )

    assert client.get("/health").status_code == 200
    assert client.get("/platform/blog").status_code == 200
    assert client.get("/ready").status_code == 503
    assert client.post("/platform/blog", json={"slug": "x", "title": "x"}).status_code == 503
    assert client.post("/billing/checkout", json={"plan": "starter"}).status_code == 503


def test_production_member_and_operator_rbac(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    services = build_services(settings)
    client = TestClient(create_app(services))
    member = {"X-API-Key": MEMBER_KEY}
    operator = {"Authorization": f"Bearer {OPERATOR_KEY}"}

    assert client.get("/ready").status_code == 200
    assert client.post("/rag/search", json={"query": "DV01"}).status_code == 401
    assert client.post("/rag/search", json={"query": "DV01"}, headers=member).status_code == 403

    blog = {"slug": "security-smoke", "title": "Security smoke"}
    assert client.post("/platform/blog", json=blog).status_code == 401
    assert client.post("/platform/blog", json=blog, headers=member).status_code == 403
    assert client.post("/platform/blog", json=blog, headers=operator).status_code == 200

    assert client.post("/billing/checkout", json={"plan": "starter", "email": "spoof@evil.test"}).status_code == 401
    token = mint_session_token(
        AUTH_SECRET,
        user_id="user_security_1",
        email="buyer@desk.test",
        expires_at=int(time.time()) + 300,
    )
    session = {"Authorization": f"Bearer {token}"}
    assert client.post("/rag/search", json={"query": "DV01"}, headers=session).status_code == 403
    services.store.upsert_entitlement(
        "buyer@desk.test", "starter", user_id="user_security_1", status="active", source="test"
    )
    assert client.post("/rag/search", json={"query": "DV01"}, headers=session).status_code == 200
    assert client.post("/billing/checkout", json={"plan": "starter", "email": "spoof@evil.test"}, headers=session).status_code == 200
    entitlement = client.get("/billing/entitlement?email=spoof@evil.test", headers=session)
    assert entitlement.status_code == 200
    assert entitlement.json()["user_id"] == "user_security_1"
    assert entitlement.json()["email"] == "buyer@desk.test"


def test_production_checkout_fails_closed_without_source_rights_clearance(tmp_path: Path) -> None:
    settings = _settings(tmp_path, source_rights_cleared=False)
    client = _client(settings)
    token = mint_session_token(
        AUTH_SECRET,
        user_id="user_rights_gate",
        email="buyer@desk.test",
        expires_at=int(time.time()) + 300,
    )
    response = client.post(
        "/billing/checkout",
        json={"plan": "starter"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "source-rights clearance" in response.json()["detail"]


def test_platform_identity_is_server_owned_and_progress_is_private(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    services = build_services(settings)
    client = TestClient(create_app(services))
    services.store.upsert_entitlement(
        "alice@desk.test", "student", user_id="user-alice", status="active", source="test"
    )
    services.store.upsert_entitlement(
        "bob@desk.test", "student", user_id="user-bob", status="active", source="test"
    )

    def session(user_id: str, email: str) -> dict[str, str]:
        token = mint_session_token(
            AUTH_SECRET,
            user_id=user_id,
            email=email,
            expires_at=int(time.time()) + 300,
        )
        return {"Authorization": f"Bearer {token}"}

    alice = session("user-alice", "alice@desk.test")
    bob = session("user-bob", "bob@desk.test")

    # Client-supplied identity is ignored in favour of the signed identity.
    spoof = client.post(
        "/platform/community/threads",
        headers=alice,
        json={
            "channel": "forum",
            "title": "Signed identity",
            "body": "The API owns the author field.",
            "author": "bob@desk.test",
            "author_id": "user-bob",
        },
    )
    assert spoof.status_code == 200
    thread_data = spoof.json()
    assert "author_id" not in thread_data
    assert thread_data["author"].startswith("member-")

    # Voting is idempotent for one signed account.
    vote_url = f"/platform/community/threads/{thread_data['id']}/vote?delta=500"
    first_vote = client.post(vote_url, headers=alice)
    second_vote = client.post(vote_url, headers=alice)
    assert first_vote.status_code == second_vote.status_code == 200
    assert first_vote.json()["votes"] == second_vote.json()["votes"] == 1

    progress_payload = {
        "kind": "lesson",
        "ref": "black-scholes#L1",
        "score": 999999,
        "meta": {"course": "black-scholes"},
    }
    first_progress = client.post("/platform/progress", headers=alice, json=progress_payload)
    duplicate = client.post("/platform/progress", headers=alice, json=progress_payload)
    assert first_progress.status_code == duplicate.status_code == 200
    assert first_progress.json()["created"] is True
    assert duplicate.json()["created"] is False
    own_progress = client.get("/platform/progress/user-alice", headers=alice)
    assert own_progress.status_code == 200
    assert own_progress.json()["avg_score"] is None
    assert own_progress.json()["events"] == 1
    assert own_progress.json()["completed_lessons"] == [progress_payload["ref"]]
    bob_progress = client.get("/platform/progress/user-bob", headers=bob)
    assert bob_progress.json()["completed_lessons"] == []
    assert client.get("/platform/progress/user-alice", headers=bob).status_code == 403

    # The leaderboard uses fixed server-side weights, never the submitted score.
    with ThreadPoolExecutor(max_workers=16) as pool:
        concurrent = list(pool.map(
            lambda _: client.post(
                "/platform/progress",
                headers=alice,
                json={**progress_payload, "ref": "black-scholes#L2"},
            ).json(),
            range(32),
        ))
    assert sum(item["created"] is True for item in concurrent) == 1

    board = client.get("/platform/leaderboard").json()["leaderboard"]
    assert "user_id" not in board[0]
    assert board[0]["username"].startswith("member-")
    assert board[0]["points"] == 10

    survival = client.post(
        "/platform/survival",
        headers=alice,
        json={"wave": "Master", "score": 7200, "streak": 20},
    )
    assert survival.status_code == 200
    assert survival.json()["ranked"] is False
    assert client.get("/platform/survival/leaderboard", headers=alice).json()["leaderboard"] == []

    # Operational counts are no longer exposed on the public health route.
    assert client.get("/platform/health").json() == {"status": "ok"}
    assert client.get("/platform/admin/counts").status_code == 401
    assert client.get("/platform/admin/counts", headers={"X-API-Key": OPERATOR_KEY}).status_code == 200


def test_course_scripts_are_delivered_by_server_entitlement(tmp_path: Path) -> None:
    scripts = tmp_path / "course-scripts"
    scripts.mkdir()
    (scripts / "vanilla-options-quote.md").write_text("# Free preview", encoding="utf-8")
    (scripts / "yield-curve-bootstrapping.md").write_text(
        "---\nslug: yield-curve-bootstrapping\n---\n\n"
        "# Starter course\n\n"
        "> Legende de provenance du contenu:\n"
        "> - **[extrait]** texte issu des sources.\n\n"
        "## Positionnement bibliotheque\n- Internal SaaS assembly note.\n\n"
        "## Cours redige\nA client lesson _[reformule]_ grounded by [S1]. "
        "Comme le souligne l'extrait [S1], discount factors must reprice the curve instruments. "
        "Activite: comparer les extraits [Sx] et isoler les definitions robustes. "
        "Le role de l'extrait est de documenter la convention. "
        "Les sources ([Sx]) ancrent la lecon.\n\n"
        "## Plan pedagogique adaptatif (base sur les sources)\n1. Internal authoring plan.\n\n"
        "## Trous pedagogiques (signaler, ne pas inventer)\n- Internal gap.\n\n"
        "## Faits et angles extraits de la base\n- Raw extracted angle.\n\n"
        "## Script enseignant\nPrivate teacher production notes.\n\n"
        "## Checkpoint personas exigeants\nPrivate internal reviewer checklist.\n\n"
        "## Sources RAG a citer\n"
        "- *Hull* — « Distinguishing forward curves from discount curves requires repricing the market instruments used in the bootstrap. »\n"
        "- *Noisy bibliography* — « REFERENCES AND BIBLIOGRAPHY Journal of Finance, 59 (3), 1405–1440. »\n\n"
        "## Source Appendix (back-office)\n"
        "- [S1] Internal source (chunk 8, score 0.991): private evidence\n",
        encoding="utf-8",
    )
    (scripts / "implied-volatility-smile.md").write_text("# Student course", encoding="utf-8")
    settings = _settings(tmp_path, course_scripts_dir=scripts)
    services = build_services(settings)
    client = TestClient(create_app(services))
    token = mint_session_token(
        AUTH_SECRET,
        user_id="course-user",
        email="course@desk.test",
        expires_at=int(time.time()) + 300,
    )
    session = {"Authorization": f"Bearer {token}"}

    assert client.get("/courses/black-scholes/script").status_code == 401
    assert client.get("/courses/black-scholes/script", headers=session).status_code == 403
    assert client.get("/courses/yield-curves/script").status_code == 401
    assert client.get("/courses/yield-curves/script", headers=session).status_code == 403
    services.store.upsert_entitlement(
        "course@desk.test", "starter", user_id="course-user", status="active", source="test"
    )
    starter = client.get("/courses/yield-curves/script", headers=session)
    assert starter.status_code == 200
    assert starter.text.startswith("# Starter course")
    assert "## Cours redige\nA client lesson grounded by." in starter.text
    assert "discount factors must reprice the curve instruments" in starter.text
    assert "souligne l'extrait" not in starter.text
    assert "l'source" not in starter.text
    assert "[Sx]" not in starter.text
    assert "comparer les sources et isoler les definitions robustes" in starter.text
    assert "Le role de la source" in starter.text
    assert "Les sources ancrent la lecon" in starter.text
    assert "## References du cours" in starter.text
    assert "Distinguishing forward curves from discount curves" in starter.text
    assert "Noisy bibliography" not in starter.text
    assert "Journal of Finance" not in starter.text
    assert "Source Appendix" not in starter.text
    assert "private evidence" not in starter.text
    assert "score 0.991" not in starter.text
    assert "slug:" not in starter.text
    assert "Legende de provenance" not in starter.text
    assert "Positionnement bibliotheque" not in starter.text
    assert "Plan pedagogique adaptatif" not in starter.text
    assert "Trous pedagogiques" not in starter.text
    assert "Faits et angles" not in starter.text
    assert "Script enseignant" not in starter.text
    assert "Private teacher production notes" not in starter.text
    assert "Checkpoint personas" not in starter.text
    assert "Private internal reviewer checklist" not in starter.text
    assert "[reformule]" not in starter.text
    assert "[S1]" not in starter.text
    assert starter.headers["cache-control"] == "private, no-store"
    assert client.get("/courses/black-scholes/script", headers=session).text == "# Free preview"
    assert client.get("/courses/implied-vol/script", headers=session).status_code == 403
    services.store.upsert_entitlement(
        "course@desk.test", "student", user_id="course-user", status="active", source="test"
    )
    assert client.get("/courses/implied-vol/script", headers=session).text == "# Student course"
    operator = {"X-API-Key": OPERATOR_KEY}
    assert client.get("/courses/vol-products/script", headers=operator).status_code == 404
    assert client.get("/courses/hedging/script", headers=operator).status_code == 404
    assert client.get("/courses/not-a-course/script", headers={"X-API-Key": OPERATOR_KEY}).status_code == 404


def test_unclassified_mutations_are_operator_only() -> None:
    assert ApiSecurity.access_for("POST", "/future/admin/mutation") == "operator"
    assert ApiSecurity.access_for("DELETE", "/future/resource/42") == "operator"
    assert ApiSecurity.access_for("POST", "/billing/checkout") == "identity"
    assert ApiSecurity.access_for("POST", "/agent/exercise") == "member"
    assert ApiSecurity.required_plan_for("POST", "/agent/exercise") == "starter"
    assert ApiSecurity.required_plan_for("POST", "/agent/course") == "student"
    assert ApiSecurity.required_plan_for("POST", "/platform/survival") == "student"
    assert ApiSecurity.required_plan_for("POST", "/agent/ag-ui/run") == "pro"
    assert ApiSecurity.required_plan_for("POST", "/agent/desk/run") == "pro"
    assert ApiSecurity.required_plan_for("GET", "/agent/desk/state") == "pro"
    assert ApiSecurity.required_plan_for("POST", "/generate/future-premium") == "pro"
    assert ApiSecurity.required_plan_for("POST", "/platform/progress") is None


def test_sqlite_rate_limit_is_shared_between_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "limits.sqlite3"
    first = SQLiteRateLimiter(db_path, window_seconds=60)
    second = SQLiteRateLimiter(db_path, window_seconds=60)

    assert first.consume(scope="member", principal="client-a", limit=2, now=120) == 1
    assert second.consume(scope="member", principal="client-a", limit=2, now=120) == 0
    try:
        first.consume(scope="member", principal="client-a", limit=2, now=120)
    except Exception as exc:  # HTTPException without coupling this test to Starlette internals
        assert getattr(exc, "status_code", None) == 429
    else:
        raise AssertionError("third request in the same shared window must be rejected")


def test_optional_integration_path_is_safe_in_shallow_container_layout() -> None:
    root = _default_documents_root(Path("/app/pricinglibrary_rag/integrations.py"))
    assert root == Path(root.anchor)


def test_session_token_signature_expiry_and_identity() -> None:
    token = mint_session_token(
        AUTH_SECRET,
        user_id="user-42",
        email="Buyer@Desk.Test",
        expires_at=200,
    )
    identity = verify_session_token(token, AUTH_SECRET, now=100)
    assert identity.user_id == "user-42"
    assert identity.email == "buyer@desk.test"

    for invalid in (token + "x", mint_session_token(AUTH_SECRET, user_id="user-42", email="buyer@desk.test", expires_at=99)):
        try:
            verify_session_token(invalid, AUTH_SECRET, now=100)
        except Exception as exc:
            assert getattr(exc, "status_code", None) == 401
        else:
            raise AssertionError("tampered or expired token must be rejected")


def test_supabase_compatible_jwks_token_opens_member_and_billing_routes(tmp_path: Path) -> None:
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk.update({"kid": "supabase-test-key", "use": "sig", "alg": "RS256"})
    issuer = "https://project-ref.supabase.co/auth/v1"
    settings = _settings(
        tmp_path,
        auth_token_secret=None,
        auth_issuer=issuer,
        auth_audience="authenticated",
        auth_jwks_json=json.dumps({"keys": [jwk]}),
        auth_algorithms=("RS256",),
    )
    services = build_services(settings)
    client = TestClient(create_app(services))
    claims = {
        "sub": "supabase-user-1",
        "email": "supabase@desk.test",
        "aud": "authenticated",
        "iss": issuer,
        "exp": int(time.time()) + 300,
        "role": "authenticated",
    }
    token = jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": "supabase-test-key"})
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/ready").json()["security"]["identity_mode"] == "oidc_jwks"
    assert client.post("/rag/search", json={"query": "DV01"}, headers=headers).status_code == 403
    services.store.upsert_entitlement(
        "supabase@desk.test",
        "starter",
        user_id="supabase-user-1",
        status="active",
        source="test:supabase",
    )
    assert client.post("/rag/search", json={"query": "DV01"}, headers=headers).status_code == 200
    assert client.post("/billing/checkout", json={"plan": "starter"}, headers=headers).status_code == 200
    assert client.post("/platform/blog", json={"slug": "forbidden", "title": "Forbidden"}, headers=headers).status_code == 403

    admin_claims = {
        **claims,
        "sub": "supabase-admin-1",
        "email": "admin@desk.test",
        "app_metadata": {"role": "admin"},
    }
    admin_token = jwt.encode(admin_claims, private_key, algorithm="RS256", headers={"kid": "supabase-test-key"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    assert client.get("/platform/admin/counts", headers=admin_headers).status_code == 200
    assert client.post(
        "/platform/blog",
        json={"slug": "admin-signed", "title": "Signed admin"},
        headers=admin_headers,
    ).status_code == 200

    wrong_audience = jwt.encode(
        {**claims, "aud": "wrong-audience"},
        private_key,
        algorithm="RS256",
        headers={"kid": "supabase-test-key"},
    )
    assert (
        client.post(
            "/billing/checkout",
            json={"plan": "starter"},
            headers={"Authorization": f"Bearer {wrong_audience}"},
        ).status_code
        == 401
    )
