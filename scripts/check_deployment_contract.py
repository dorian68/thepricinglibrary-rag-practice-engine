"""Fail-closed gate for the resolved production Docker Compose topology."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path, PurePosixPath
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker-compose.yml"
PRODUCTION_ENV_EXAMPLE = ROOT / ".env.production.example"

REQUIRED_CONTAINER_ENVIRONMENT = {
    "TPL_ENVIRONMENT", "TPL_API_KEY", "TPL_OPERATOR_API_KEY", "TPL_AUTH_ISSUER",
    "TPL_AUTH_AUDIENCE", "TPL_AUTH_JWKS_URL", "TPL_AUTH_ALGORITHMS",
    "TPL_RATE_LIMIT_PER_MIN", "TPL_CORS_ORIGINS", "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET", "STRIPE_PRICE_STARTER", "STRIPE_PRICE_STUDENT",
    "STRIPE_PRICE_PRO", "STRIPE_PRICE_STARTER_KIT", "TPL_BILLING_SUCCESS_URL",
    "TPL_BILLING_CANCEL_URL", "TPL_STARTER_KIT_BUNDLE_PATH",
    "TPL_STARTER_KIT_MANIFEST_PATH", "TPL_STARTER_KIT_SUCCESS_URL",
    "TPL_STARTER_KIT_CANCEL_URL", "TPL_SOURCE_RIGHTS_CLEARED",
}

ALLOWED_CONTAINER_ENVIRONMENT = REQUIRED_CONTAINER_ENVIRONMENT | {
    "TPL_AUTH_TOKEN_SECRET", "TPL_RATE_LIMIT_WINDOW_SECONDS", "TPL_TRUST_PROXY_HEADERS",
    "TPL_LLM_PROVIDER", "TPL_OPENAI_API_KEY", "GENERATION_MODE", "RETRIEVAL_MODE",
    "EMBEDDING_PROVIDER", "LLM_PROVIDER", "GENERATION_STRICT_VALIDATION",
    "TPL_BILLING_CHECKOUT_MODE",
}

REQUIRED_SERVER_VALUES = {
    "TPL_IMAGE_REPOSITORY", "TPL_IMAGE_DIGEST", "TPL_PUBLIC_ORIGIN",
    "TPL_STARTER_KIT_RELEASE_DIR", "TPL_STARTER_KIT_BUNDLE_FILENAME",
    "TPL_API_KEY", "TPL_OPERATOR_API_KEY", "TPL_AUTH_ISSUER", "TPL_AUTH_AUDIENCE",
    "TPL_AUTH_JWKS_URL", "TPL_AUTH_ALGORITHMS", "TPL_RATE_LIMIT_PER_MIN",
    "TPL_RATE_LIMIT_WINDOW_SECONDS", "TPL_TRUST_PROXY_HEADERS", "TPL_CORS_ORIGINS",
    "GENERATION_STRICT_VALIDATION", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PRICE_STARTER", "STRIPE_PRICE_STUDENT", "STRIPE_PRICE_PRO",
    "STRIPE_PRICE_STARTER_KIT", "TPL_SOURCE_RIGHTS_CLEARED",
}

PLACEHOLDER_TERMS = ("replace-with", "changeme", "placeholder", "<", ">")


def load_environment_file(path: Path) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    errors: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            errors.append(f"invalid environment entry at line {line_number}")
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'\"', "'"}:
            value = value[1:-1]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            errors.append(f"invalid environment key at line {line_number}")
        elif key in values:
            errors.append(f"duplicate environment key: {key}")
        else:
            values[key] = value
    return values, errors


def _valid_https_origin(value: str) -> bool:
    parsed = urlsplit(value)
    return (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
        and not parsed.username
        and not parsed.password
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
    )


def _valid_https_url(value: str) -> bool:
    parsed = urlsplit(value)
    return (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
    )


def validate_environment_values(values: dict[str, str], *, allow_placeholders: bool) -> list[str]:
    errors: list[str] = []
    missing = sorted(key for key in REQUIRED_SERVER_VALUES if not values.get(key, "").strip())
    if missing:
        errors.append(f"required production values missing or empty: {', '.join(missing)}")
        return errors

    if not allow_placeholders:
        placeholders = sorted(
            key for key in REQUIRED_SERVER_VALUES
            if any(term in values[key].casefold() for term in PLACEHOLDER_TERMS)
        )
        if placeholders:
            errors.append(f"placeholder production values forbidden: {', '.join(placeholders)}")

    origin = values["TPL_PUBLIC_ORIGIN"].rstrip("/")
    if not _valid_https_origin(origin):
        errors.append("TPL_PUBLIC_ORIGIN must be an HTTPS origin without localhost, credentials, path or query")
    for key in ("TPL_AUTH_ISSUER", "TPL_AUTH_JWKS_URL"):
        if not _valid_https_url(values[key]):
            errors.append(f"{key} must be an HTTPS URL without localhost")
    issuer = urlsplit(values["TPL_AUTH_ISSUER"])
    jwks = urlsplit(values["TPL_AUTH_JWKS_URL"])
    expected_jwks_path = f"{issuer.path.rstrip('/')}/.well-known/jwks.json"
    if issuer.hostname != jwks.hostname or jwks.path != expected_jwks_path:
        errors.append("TPL_AUTH_JWKS_URL must share the issuer host and use its /.well-known/jwks.json path")

    member_key = values["TPL_API_KEY"]
    operator_key = values["TPL_OPERATOR_API_KEY"]
    if len(member_key) < 32 or len(operator_key) < 32:
        errors.append("member and operator API keys must each contain at least 32 characters")
    if member_key == operator_key:
        errors.append("member and operator API keys must be different")
    try:
        if int(values["TPL_RATE_LIMIT_PER_MIN"]) <= 0:
            raise ValueError
    except ValueError:
        errors.append("TPL_RATE_LIMIT_PER_MIN must be a positive integer")
    try:
        rate_window = int(values["TPL_RATE_LIMIT_WINDOW_SECONDS"])
        if not 1 <= rate_window <= 3600:
            raise ValueError
    except ValueError:
        errors.append("TPL_RATE_LIMIT_WINDOW_SECONDS must be an integer between 1 and 3600")
    if values["TPL_TRUST_PROXY_HEADERS"].casefold() not in {"true", "false"}:
        errors.append("TPL_TRUST_PROXY_HEADERS must be explicitly true or false")
    if values["GENERATION_STRICT_VALIDATION"].casefold() != "true":
        errors.append("GENERATION_STRICT_VALIDATION must remain true in production")
    if not allow_placeholders and values["TPL_SOURCE_RIGHTS_CLEARED"].casefold() != "true":
        errors.append("TPL_SOURCE_RIGHTS_CLEARED must be true only after rights-clearance evidence is approved")

    algorithms = {item.strip() for item in values["TPL_AUTH_ALGORITHMS"].split(",") if item.strip()}
    if not algorithms or not algorithms <= {"ES256", "RS256"}:
        errors.append("TPL_AUTH_ALGORITHMS must contain only ES256 and/or RS256")
    if origin not in {item.strip().rstrip("/") for item in values["TPL_CORS_ORIGINS"].split(",")}:
        errors.append("TPL_CORS_ORIGINS must include TPL_PUBLIC_ORIGIN exactly")

    if not allow_placeholders:
        format_checks = {
            "TPL_IMAGE_REPOSITORY": r"[a-zA-Z0-9.-]+(?::[0-9]+)?/[a-zA-Z0-9._/-]+",
            "TPL_IMAGE_DIGEST": r"[0-9a-fA-F]{64}",
            "STRIPE_SECRET_KEY": r"sk_(?:test|live)_[A-Za-z0-9]{8,}",
            "STRIPE_WEBHOOK_SECRET": r"whsec_[A-Za-z0-9]{8,}",
            "STRIPE_PRICE_STARTER": r"price_[A-Za-z0-9]{6,}",
            "STRIPE_PRICE_STUDENT": r"price_[A-Za-z0-9]{6,}",
            "STRIPE_PRICE_PRO": r"price_[A-Za-z0-9]{6,}",
            "STRIPE_PRICE_STARTER_KIT": r"price_[A-Za-z0-9]{6,}",
        }
        invalid = sorted(
            key for key, pattern in format_checks.items()
            if re.fullmatch(pattern, values[key]) is None
        )
        if invalid:
            errors.append(f"invalid production value format: {', '.join(invalid)}")
        if values["TPL_IMAGE_DIGEST"] == "0" * 64:
            errors.append("TPL_IMAGE_DIGEST cannot be the all-zero sentinel")

    release_dir = values["TPL_STARTER_KIT_RELEASE_DIR"]
    pure_release = PurePosixPath(release_dir)
    if (
        not pure_release.is_absolute()
        or pure_release == PurePosixPath("/")
        or ".." in pure_release.parts
        or "\\" in release_dir
        or len(pure_release.parts) < 4
        or "," in release_dir
    ):
        errors.append("TPL_STARTER_KIT_RELEASE_DIR must be a dedicated absolute POSIX directory")
    filename = values["TPL_STARTER_KIT_BUNDLE_FILENAME"]
    if (
        PurePosixPath(filename).name != filename
        or "\\" in filename
        or not filename.lower().endswith(".zip")
        or filename in {"", ".", ".."}
    ):
        errors.append("TPL_STARTER_KIT_BUNDLE_FILENAME must be a basename ending in .zip")
    return errors


def resolve_compose(env_file: Path) -> tuple[dict[str, object] | None, list[str]]:
    command = [
        "docker", "compose", "--file", str(COMPOSE), "--env-file", str(env_file),
        "config", "--format", "json",
    ]
    clean_environment = os.environ.copy()
    controlled_prefixes = ("TPL_", "STRIPE_", "GENERATION_", "RETRIEVAL_", "EMBEDDING_", "LLM_")
    for key in list(clean_environment):
        if key.startswith(controlled_prefixes):
            clean_environment.pop(key, None)
    try:
        completed = subprocess.run(
            command, cwd=ROOT, env=clean_environment, check=False, capture_output=True, text=True,
        )
    except FileNotFoundError:
        return None, ["Docker Compose is required to resolve the production topology"]
    if completed.returncode != 0:
        return None, ["Docker Compose could not resolve the production topology"]
    try:
        return json.loads(completed.stdout), []
    except json.JSONDecodeError:
        return None, ["Docker Compose returned invalid JSON"]


def validate_resolved_config(config: dict[str, object], values: dict[str, str]) -> list[str]:
    errors: list[str] = []
    services = config.get("services")
    if not isinstance(services, dict) or set(services) != {"api"}:
        errors.append("resolved Compose services must contain exactly api")
    api = services.get("api") if isinstance(services, dict) else None
    if not isinstance(api, dict):
        errors.append("resolved Compose service api is missing")
        return errors
    top_level_volumes = config.get("volumes")
    if not isinstance(top_level_volumes, dict) or set(top_level_volumes) != {"tpl_data"}:
        errors.append("Compose must define exactly the tpl_data volume")
    else:
        tpl_data = top_level_volumes["tpl_data"]
        if not isinstance(tpl_data, dict) or tpl_data.get("external") is True:
            errors.append("Compose tpl_data volume must be project-owned and non-external")

    expected_image = f"{values['TPL_IMAGE_REPOSITORY']}@sha256:{values['TPL_IMAGE_DIGEST']}"
    if api.get("image") != expected_image or api.get("build"):
        errors.append("api image must be digest-pinned and must not contain a production build directive")
    if api.get("command") is not None or api.get("entrypoint") is not None:
        errors.append("api command and entrypoint overrides are forbidden")
    if str(api.get("user", "")).casefold() != "tpl":
        errors.append("api must explicitly run as the non-root tpl user")
    if api.get("read_only") is not True:
        errors.append("api root filesystem must be read-only")
    if api.get("cap_drop") != ["ALL"] or api.get("cap_add"):
        errors.append("api must drop ALL capabilities and add none")
    if api.get("security_opt") != ["no-new-privileges:true"]:
        errors.append("api security options must contain only no-new-privileges:true")
    if api.get("tmpfs") != ["/tmp:rw,noexec,nosuid,size=64m"]:
        errors.append("api must use the exact bounded hardened /tmp tmpfs")
    if api.get("privileged") is True:
        errors.append("api forbidden privileged control: privileged")
    for key in ("network_mode", "pid", "ipc", "uts", "userns_mode"):
        if api.get(key) not in (None, ""):
            errors.append(f"api forbidden privileged control: {key}")
    for key in (
        "devices", "device_cgroup_rules", "volumes_from", "group_add", "sysctls",
        "runtime", "cgroup", "cgroup_parent", "post_start", "pre_stop", "extra_hosts",
        "dns", "dns_search", "links",
    ):
        if api.get(key):
            errors.append(f"api forbidden device or inherited mount control: {key}")
    if api.get("healthcheck") is not None:
        errors.append("api Compose healthcheck override is forbidden; use the inspected image healthcheck")
    if api.get("networks") != {"default": None}:
        errors.append("api must use only the isolated project default network")
    top_level_networks = config.get("networks")
    if not isinstance(top_level_networks, dict) or set(top_level_networks) != {"default"}:
        errors.append("Compose must define exactly one project default network")
    else:
        default_network = top_level_networks["default"]
        if not isinstance(default_network, dict) or default_network.get("external") is True:
            errors.append("Compose default network must not be external")
    for key in ("secrets", "configs"):
        if api.get(key):
            errors.append(f"api unexpected mounted configuration control: {key}")

    ports = api.get("ports") or []
    safe_port = any(
        isinstance(port, dict)
        and port.get("host_ip") == "127.0.0.1"
        and int(port.get("target", 0)) == 8000
        and str(port.get("published", "")) == "8000"
        for port in ports
    )
    if len(ports) != 1 or not safe_port:
        errors.append("api port 8000 must be published once on loopback only")

    volumes = api.get("volumes") or []
    if len(volumes) != 2 or {item.get("target") for item in volumes if isinstance(item, dict)} != {
        "/data", "/releases/starter-kit"
    }:
        errors.append("api mounts must be exactly the data volume and read-only Starter Kit release")
    data_mounts = [item for item in volumes if isinstance(item, dict) and item.get("target") == "/data"]
    if (
        len(data_mounts) != 1
        or data_mounts[0].get("type") != "volume"
        or data_mounts[0].get("source") != "tpl_data"
        or data_mounts[0].get("read_only") is True
    ):
        errors.append("api data mount must be one writable named volume")
    release_mounts = [item for item in volumes if isinstance(item, dict) and item.get("target") == "/releases/starter-kit"]
    if len(release_mounts) != 1:
        errors.append("exactly one Starter Kit release mount is required")
    else:
        mount = release_mounts[0]
        if mount.get("type") != "bind" or mount.get("source") != values["TPL_STARTER_KIT_RELEASE_DIR"]:
            errors.append("Starter Kit release mount must bind the declared dedicated host directory")
        if mount.get("read_only") is not True:
            errors.append("Starter Kit release mount must be read-only")

    environment = api.get("environment")
    if not isinstance(environment, dict):
        errors.append("api environment mapping is missing")
        environment = {}
    missing_environment = sorted(REQUIRED_CONTAINER_ENVIRONMENT - set(environment))
    if missing_environment:
        errors.append(f"resolved api environment mapping missing: {', '.join(missing_environment)}")
    unexpected_environment = sorted(set(environment) - ALLOWED_CONTAINER_ENVIRONMENT)
    if unexpected_environment:
        errors.append(f"resolved api environment contains unexpected keys: {', '.join(unexpected_environment)}")
    origin = values["TPL_PUBLIC_ORIGIN"].rstrip("/")
    expected_environment = {
        "TPL_ENVIRONMENT": "production",
        "TPL_BILLING_CHECKOUT_MODE": "subscription",
        "TPL_BILLING_SUCCESS_URL": f"{origin}/#/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        "TPL_BILLING_CANCEL_URL": f"{origin}/#/billing/cancel",
        "TPL_STARTER_KIT_BUNDLE_PATH": f"/releases/starter-kit/{values['TPL_STARTER_KIT_BUNDLE_FILENAME']}",
        "TPL_STARTER_KIT_MANIFEST_PATH": "/releases/starter-kit/manifest.json",
        "TPL_STARTER_KIT_SUCCESS_URL": f"{origin}/#/starter-kit/success",
        "TPL_STARTER_KIT_CANCEL_URL": f"{origin}/#/starter-kit/cancel",
    }
    invalid_mapping = sorted(
        key for key, expected in expected_environment.items() if environment.get(key) != expected
    )
    if invalid_mapping:
        errors.append(f"resolved commercial environment mapping invalid: {', '.join(invalid_mapping)}")
    source_mappings = {
        "TPL_API_KEY": "TPL_API_KEY",
        "TPL_OPERATOR_API_KEY": "TPL_OPERATOR_API_KEY",
        "TPL_AUTH_ISSUER": "TPL_AUTH_ISSUER",
        "TPL_AUTH_AUDIENCE": "TPL_AUTH_AUDIENCE",
        "TPL_AUTH_JWKS_URL": "TPL_AUTH_JWKS_URL",
        "TPL_AUTH_ALGORITHMS": "TPL_AUTH_ALGORITHMS",
        "TPL_RATE_LIMIT_PER_MIN": "TPL_RATE_LIMIT_PER_MIN",
        "TPL_RATE_LIMIT_WINDOW_SECONDS": "TPL_RATE_LIMIT_WINDOW_SECONDS",
        "TPL_TRUST_PROXY_HEADERS": "TPL_TRUST_PROXY_HEADERS",
        "TPL_CORS_ORIGINS": "TPL_CORS_ORIGINS",
        "GENERATION_STRICT_VALIDATION": "GENERATION_STRICT_VALIDATION",
        "TPL_SOURCE_RIGHTS_CLEARED": "TPL_SOURCE_RIGHTS_CLEARED",
        "STRIPE_SECRET_KEY": "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET": "STRIPE_WEBHOOK_SECRET",
        "STRIPE_PRICE_STARTER": "STRIPE_PRICE_STARTER",
        "STRIPE_PRICE_STUDENT": "STRIPE_PRICE_STUDENT",
        "STRIPE_PRICE_PRO": "STRIPE_PRICE_PRO",
        "STRIPE_PRICE_STARTER_KIT": "STRIPE_PRICE_STARTER_KIT",
    }
    mismatched_secrets = sorted(
        container_key for container_key, source_key in source_mappings.items()
        if environment.get(container_key) != values.get(source_key)
    )
    if mismatched_secrets:
        errors.append(f"resolved environment differs from the validated env-file: {', '.join(mismatched_secrets)}")
    return errors


def inspect_release_image(image: str) -> tuple[dict[str, object] | None, list[str]]:
    try:
        completed = subprocess.run(
            ["docker", "image", "inspect", image], cwd=ROOT, check=False,
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        return None, ["Docker is required to inspect the digest-pinned release image"]
    if completed.returncode != 0:
        return None, ["digest-pinned release image is not locally available for inspection"]
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None, ["Docker image inspect returned invalid JSON"]
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        return None, ["Docker image inspect returned an unexpected payload"]
    return payload[0], []


def validate_image_metadata(metadata: dict[str, object]) -> list[str]:
    config = metadata.get("Config")
    if not isinstance(config, dict):
        return ["release image Config metadata is missing"]
    user = str(config.get("User", "")).strip().casefold()
    errors: list[str] = []
    if user != "tpl":
        errors.append("release image must declare the tpl non-root user")
    if config.get("WorkingDir") != "/app":
        errors.append("release image working directory must be /app")
    expected_command = [
        "uvicorn", "pricinglibrary_rag.api:app", "--host", "0.0.0.0", "--port", "8000"
    ]
    if config.get("Cmd") != expected_command or config.get("Entrypoint") not in (None, []):
        errors.append("release image command must be the audited uvicorn API command")
    healthcheck = config.get("Healthcheck")
    expected_healthcheck = {
        "Test": [
            "CMD-SHELL",
            "python -c \"import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/ready').status==200 else 1)\" || exit 1",
        ],
        "Interval": 30_000_000_000,
        "Timeout": 5_000_000_000,
        "Retries": 3,
    }
    if not isinstance(healthcheck, dict) or any(
        healthcheck.get(key) != expected for key, expected in expected_healthcheck.items()
    ):
        errors.append("release image must declare the exact fail-closed HTTP /ready healthcheck")
    return errors


def _runtime_payload_errors(ready: object, availability: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(ready, dict) or ready.get("status") != "ready":
        errors.append("ephemeral release image /ready response is not ready")
    security = ready.get("security") if isinstance(ready, dict) else None
    if not isinstance(security, dict) or security.get("ready") is not True:
        errors.append("ephemeral release image security readiness is false")
    if not isinstance(availability, dict) or availability.get("sale_ready") is not True:
        errors.append("ephemeral release image Starter Kit availability is not sale-ready")
    version = availability.get("version") if isinstance(availability, dict) else None
    if not isinstance(version, str) or not version.strip():
        errors.append("ephemeral release image Starter Kit version is missing")
    return errors


def probe_release_image(image: str, env_file: Path, values: dict[str, str]) -> list[str]:
    release_dir = Path(values["TPL_STARTER_KIT_RELEASE_DIR"])
    bundle = release_dir / values["TPL_STARTER_KIT_BUNDLE_FILENAME"]
    manifest = release_dir / "manifest.json"
    if not release_dir.is_dir() or not bundle.is_file() or not manifest.is_file():
        return ["verified Starter Kit release directory, bundle or manifest is missing on this host"]

    container_name = f"tpl-deployment-probe-{uuid.uuid4().hex[:12]}"
    origin = values["TPL_PUBLIC_ORIGIN"].rstrip("/")
    run_command = [
        "docker", "run", "--detach", "--rm", "--name", container_name,
        "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges:true", "--user", "tpl",
        "--publish", "127.0.0.1::8000", "--env-file", str(env_file),
        "--env", "TPL_ENVIRONMENT=production",
        "--env", "TPL_BILLING_CHECKOUT_MODE=subscription",
        "--env", f"TPL_BILLING_SUCCESS_URL={origin}/#/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        "--env", f"TPL_BILLING_CANCEL_URL={origin}/#/billing/cancel",
        "--env", f"TPL_STARTER_KIT_BUNDLE_PATH=/releases/starter-kit/{bundle.name}",
        "--env", "TPL_STARTER_KIT_MANIFEST_PATH=/releases/starter-kit/manifest.json",
        "--env", f"TPL_STARTER_KIT_SUCCESS_URL={origin}/#/starter-kit/success",
        "--env", f"TPL_STARTER_KIT_CANCEL_URL={origin}/#/starter-kit/cancel",
        "--mount", "type=volume,target=/data",
        "--mount", f"type=bind,source={release_dir},target=/releases/starter-kit,readonly",
        image,
    ]
    started = False
    try:
        completed = subprocess.run(
            run_command, cwd=ROOT, check=False, capture_output=True, text=True,
        )
        if completed.returncode != 0:
            return ["digest-pinned release image failed to start under hardened controls"]
        started = True
        port_result = subprocess.run(
            ["docker", "port", container_name, "8000/tcp"], cwd=ROOT,
            check=False, capture_output=True, text=True,
        )
        if port_result.returncode != 0:
            return ["ephemeral release image port could not be resolved"]
        match = re.search(r"127\.0\.0\.1:(\d+)", port_result.stdout)
        if match is None:
            return ["ephemeral release image was not published on loopback"]
        base_url = f"http://127.0.0.1:{match.group(1)}"
        deadline = time.monotonic() + 45
        ready_payload: object = None
        while time.monotonic() < deadline:
            try:
                with urlopen(f"{base_url}/ready", timeout=2) as response:
                    if response.status == 200:
                        ready_payload = json.loads(response.read(1_000_000))
                        break
            except (OSError, URLError, json.JSONDecodeError):
                time.sleep(1)
        if ready_payload is None:
            return ["ephemeral release image did not reach /ready within 45 seconds"]
        try:
            with urlopen(
                f"{base_url}/products/market-finance-starter-kit/availability", timeout=5
            ) as response:
                availability_payload = json.loads(response.read(1_000_000))
        except (OSError, URLError, json.JSONDecodeError):
            return ["ephemeral release image availability endpoint failed"]
        return _runtime_payload_errors(ready_payload, availability_payload)
    finally:
        if started:
            subprocess.run(
                ["docker", "rm", "--force", "--volumes", container_name], cwd=ROOT,
                check=False, capture_output=True, text=True,
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file", type=Path, default=ROOT / ".env.production",
        help="server environment file to resolve; defaults to .env.production",
    )
    parser.add_argument(
        "--allow-placeholders", action="store_true",
        help="validate the committed template topology without claiming live readiness",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_file = args.env_file if args.env_file.is_absolute() else (ROOT / args.env_file)
    print(f"[STEP 1] production environment contract · [INPUT] {env_file.name}; values redacted")
    if not env_file.is_file():
        print("[STATUS] fail · [ERROR] production environment file is missing")
        print("[VERDICT] FAIL")
        return 1
    if args.allow_placeholders and env_file.resolve() != PRODUCTION_ENV_EXAMPLE.resolve():
        print("[STATUS] fail · [ERROR] placeholder mode is restricted to .env.production.example")
        print("[VERDICT] FAIL")
        return 1
    values, errors = load_environment_file(env_file)
    errors.extend(validate_environment_values(values, allow_placeholders=args.allow_placeholders))
    if not COMPOSE.is_file():
        errors.append("docker-compose.yml is missing")
    config = None
    if not errors:
        print("[STEP 2] resolved Docker Compose topology · [INPUT] secrets redacted")
        config, resolution_errors = resolve_compose(env_file)
        errors.extend(resolution_errors)
    if config is not None:
        errors.extend(validate_resolved_config(config, values))
    if config is not None and not args.allow_placeholders and not errors:
        image = str(config["services"]["api"]["image"])
        print("[STEP 3] digest-pinned release image metadata · [INPUT] image digest only")
        metadata, inspection_errors = inspect_release_image(image)
        errors.extend(inspection_errors)
        if metadata is not None:
            errors.extend(validate_image_metadata(metadata))
    if config is not None and not args.allow_placeholders and not errors:
        print("[STEP 4] hardened ephemeral runtime probe · [INPUT] secrets redacted")
        errors.extend(probe_release_image(str(config["services"]["api"]["image"]), env_file, values))
    if errors:
        for error in errors:
            print(f"[STATUS] fail · [ERROR] {error}")
        print("[VERDICT] FAIL")
        return 1
    if args.allow_placeholders:
        print("[STATUS] ok · [OUTPUT] committed template topology is hardened and relationally valid")
        print("[VERDICT] PASS-CLOSED · template only; real production values not validated")
    else:
        print("[STATUS] ok · [OUTPUT] resolved production topology and redacted values validated")
        print("[VERDICT] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
