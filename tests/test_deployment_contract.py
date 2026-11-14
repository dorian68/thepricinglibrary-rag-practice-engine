from __future__ import annotations

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_deployment_contract.py"
SPEC = importlib.util.spec_from_file_location("check_deployment_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _template_values() -> dict[str, str]:
    values, errors = MODULE.load_environment_file(ROOT / ".env.production.example")
    assert errors == []
    return values


def _production_values() -> dict[str, str]:
    values = _template_values()
    values.update(
        {
            "TPL_IMAGE_REPOSITORY": "registry.company.test/tpl/backend",
            "TPL_IMAGE_DIGEST": "a" * 64,
            "TPL_PUBLIC_ORIGIN": "https://staging.tpl.test",
            "TPL_STARTER_KIT_RELEASE_DIR": "/srv/tpl/releases/starter-kit/1.0.0",
            "TPL_STARTER_KIT_BUNDLE_FILENAME": "starter-kit-v1.0.0.zip",
            "TPL_API_KEY": "m" * 40,
            "TPL_OPERATOR_API_KEY": "o" * 40,
            "TPL_AUTH_ISSUER": "https://project.supabase.co/auth/v1",
            "TPL_AUTH_JWKS_URL": "https://project.supabase.co/auth/v1/.well-known/jwks.json",
            "TPL_CORS_ORIGINS": "https://staging.tpl.test",
            "STRIPE_SECRET_KEY": "sk_test_1234567890",
            "STRIPE_WEBHOOK_SECRET": "whsec_1234567890",
            "STRIPE_PRICE_STARTER": "price_starter1",
            "STRIPE_PRICE_STUDENT": "price_student1",
            "STRIPE_PRICE_PRO": "price_pro12345",
            "STRIPE_PRICE_STARTER_KIT": "price_kit12345",
            "TPL_SOURCE_RIGHTS_CLEARED": "true",
        }
    )
    return values


def test_repository_template_resolves_to_the_hardened_relational_contract() -> None:
    values = _template_values()
    assert MODULE.validate_environment_values(values, allow_placeholders=True) == []
    config, errors = MODULE.resolve_compose(ROOT / ".env.production.example")
    assert errors == [] and config is not None
    assert MODULE.validate_resolved_config(config, values) == []


def test_resolved_contract_rejects_mutable_image_writable_mount_and_public_port() -> None:
    values = _template_values()
    config, errors = MODULE.resolve_compose(ROOT / ".env.production.example")
    assert errors == [] and config is not None
    unsafe = copy.deepcopy(config)
    api = unsafe["services"]["api"]
    api["image"] = "thepricinglibrary-backend:latest"
    api["read_only"] = False
    api["ports"][0]["host_ip"] = "0.0.0.0"
    release_mount = next(item for item in api["volumes"] if item["target"] == "/releases/starter-kit")
    release_mount["read_only"] = False
    errors = MODULE.validate_resolved_config(unsafe, values)
    assert "api image must be digest-pinned and must not contain a production build directive" in errors
    assert "api root filesystem must be read-only" in errors
    assert "api port 8000 must be published once on loopback only" in errors
    assert "Starter Kit release mount must be read-only" in errors


def test_environment_contract_rejects_empty_placeholder_and_traversal_values() -> None:
    empty = {key: "" for key in MODULE.REQUIRED_SERVER_VALUES}
    assert "missing or empty" in MODULE.validate_environment_values(empty, allow_placeholders=False)[0]

    values = _production_values()
    values["TPL_API_KEY"] = "replace-with-a-real-key"
    values["TPL_PUBLIC_ORIGIN"] = "http://localhost:5173"
    values["TPL_STARTER_KIT_RELEASE_DIR"] = "/"
    values["TPL_STARTER_KIT_BUNDLE_FILENAME"] = "../escape.zip"
    errors = MODULE.validate_environment_values(values, allow_placeholders=False)
    assert any("placeholder" in error for error in errors)
    assert any("TPL_PUBLIC_ORIGIN" in error for error in errors)
    assert any("dedicated absolute POSIX directory" in error for error in errors)
    assert any("basename ending in .zip" in error for error in errors)


def test_environment_contract_accepts_well_formed_distinct_production_values() -> None:
    assert MODULE.validate_environment_values(_production_values(), allow_placeholders=False) == []


def test_well_formed_production_values_resolve_to_the_same_contract(tmp_path: Path) -> None:
    values = _production_values()
    env_file = tmp_path / ".env.production"
    env_file.write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )
    config, errors = MODULE.resolve_compose(env_file)
    assert errors == [] and config is not None
    assert MODULE.validate_resolved_config(config, values) == []


def test_comments_cannot_satisfy_a_resolved_compose_control() -> None:
    values = _template_values()
    config, errors = MODULE.resolve_compose(ROOT / ".env.production.example")
    assert errors == [] and config is not None
    unsafe = copy.deepcopy(config)
    api = unsafe["services"]["api"]
    api["security_opt"] = []
    api["x-comment"] = "no-new-privileges:true read_only:true sha256:deadbeef"
    errors = MODULE.validate_resolved_config(unsafe, values)
    assert "api security options must contain only no-new-privileges:true" in errors


def test_resolved_contract_rejects_privilege_compensation_and_secret_override() -> None:
    values = _template_values()
    config, resolution_errors = MODULE.resolve_compose(ROOT / ".env.production.example")
    assert resolution_errors == [] and config is not None
    unsafe = copy.deepcopy(config)
    api = unsafe["services"]["api"]
    api["environment"]["TPL_API_KEY"] = ""
    api["environment"]["STRIPE_SECRET_KEY"] = ""
    api["cap_add"] = ["SYS_ADMIN"]
    api["privileged"] = True
    api["user"] = "root"
    api["network_mode"] = "host"
    api["security_opt"].append("seccomp:unconfined")
    api["volumes"].append(
        {
            "type": "bind",
            "source": "/var/run/docker.sock",
            "target": "/var/run/docker.sock",
        }
    )
    errors = MODULE.validate_resolved_config(unsafe, values)
    assert "api must explicitly run as the non-root tpl user" in errors
    assert "api must drop ALL capabilities and add none" in errors
    assert "api forbidden privileged control: privileged" in errors
    assert "api forbidden privileged control: network_mode" in errors
    assert "api security options must contain only no-new-privileges:true" in errors
    assert "api mounts must be exactly the data volume and read-only Starter Kit release" in errors
    assert any("TPL_API_KEY" in error and "STRIPE_SECRET_KEY" in error for error in errors)


def test_image_metadata_requires_non_root_user_and_ready_healthcheck() -> None:
    valid = {
        "Config": {
            "User": "tpl",
            "WorkingDir": "/app",
            "Cmd": ["uvicorn", "pricinglibrary_rag.api:app", "--host", "0.0.0.0", "--port", "8000"],
            "Entrypoint": None,
            "Healthcheck": {
                "Test": [
                    "CMD-SHELL",
                    "python -c \"import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/ready').status==200 else 1)\" || exit 1",
                ],
                "Interval": 30_000_000_000,
                "Timeout": 5_000_000_000,
                "Retries": 3,
            },
        }
    }
    assert MODULE.validate_image_metadata(valid) == []
    errors = MODULE.validate_image_metadata({"Config": {"User": "root", "Healthcheck": {}}})
    assert "release image must declare the tpl non-root user" in errors
    assert "release image must declare the exact fail-closed HTTP /ready healthcheck" in errors


def test_image_metadata_rejects_a_healthcheck_that_only_echoes_ready() -> None:
    fake = {
        "Config": {
            "User": "tpl",
            "WorkingDir": "/app",
            "Cmd": ["uvicorn", "pricinglibrary_rag.api:app", "--host", "0.0.0.0", "--port", "8000"],
            "Entrypoint": None,
            "Healthcheck": {
                "Test": ["CMD-SHELL", "echo /ready; exit 0"],
                "Interval": 30_000_000_000,
                "Timeout": 5_000_000_000,
                "Retries": 3,
            },
        }
    }
    assert "exact fail-closed HTTP /ready healthcheck" in MODULE.validate_image_metadata(fake)[0]


def test_runtime_probe_payload_requires_security_and_sale_readiness() -> None:
    assert MODULE._runtime_payload_errors(
        {"status": "ready", "security": {"ready": True}},
        {"sale_ready": True, "version": "1.0.0"},
    ) == []
    errors = MODULE._runtime_payload_errors(
        {"status": "ready", "security": {"ready": False}},
        {"sale_ready": False, "version": None},
    )
    assert "ephemeral release image security readiness is false" in errors
    assert "ephemeral release image Starter Kit availability is not sale-ready" in errors
    assert "ephemeral release image Starter Kit version is missing" in errors


def test_resolved_contract_rejects_extra_services_and_external_data_volume() -> None:
    values = _template_values()
    config, resolution_errors = MODULE.resolve_compose(ROOT / ".env.production.example")
    assert resolution_errors == [] and config is not None
    unsafe = copy.deepcopy(config)
    unsafe["services"]["sidecar"] = {"image": "uncontrolled:latest"}
    unsafe["volumes"]["tpl_data"]["external"] = True
    errors = MODULE.validate_resolved_config(unsafe, values)
    assert "resolved Compose services must contain exactly api" in errors
    assert "Compose tpl_data volume must be project-owned and non-external" in errors
