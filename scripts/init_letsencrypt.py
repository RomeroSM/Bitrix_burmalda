#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=PROJECT_DIR, check=check)


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        raise RuntimeError(
            "Нет файла .env. Скопируйте .env.example в .env "
            "и заполните DOMAIN и CERTBOT_EMAIL."
        )
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def main() -> None:
    settings = {**read_env(PROJECT_DIR / ".env"), **os.environ}
    domain = settings.get("DOMAIN", "")
    email = settings.get("CERTBOT_EMAIL", "")

    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", domain):
        raise RuntimeError(f"Некорректный DOMAIN: {domain!r}")
    if domain in {"localhost", "bitrix.example.com"}:
        raise RuntimeError("Укажите реальный публичный домен в .env.")
    if not email:
        raise RuntimeError("В .env не задан CERTBOT_EMAIL.")

    run("docker", "compose", "up", "-d", "--build", "app", "nginx")

    certificate = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
    exists = run(
        "docker",
        "compose",
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "sh",
        "certbot",
        "-c",
        f"test -f '{certificate}'",
        check=False,
    )

    force_renewal = settings.get("CERTBOT_FORCE_RENEWAL", "0") == "1"
    if exists.returncode == 0 and not force_renewal:
        print(f"Сертификат для {domain} уже установлен.")
    else:
        command = [
            "docker",
            "compose",
            "run",
            "--rm",
            "--no-deps",
            "--entrypoint",
            "certbot",
            "certbot",
            "certonly",
            "--webroot",
            "--webroot-path=/var/www/certbot",
            "--email",
            email,
            "--agree-tos",
            "--no-eff-email",
            "--non-interactive",
            "--cert-name",
            domain,
            "-d",
            domain,
        ]
        if settings.get("CERTBOT_STAGING", "0") == "1":
            command.append("--staging")
        if force_renewal:
            command.append("--force-renewal")
        run(*command)

    run("docker", "compose", "restart", "nginx")
    run("docker", "compose", "up", "-d", "certbot")
    print(f"Готово: https://{domain}/health")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
