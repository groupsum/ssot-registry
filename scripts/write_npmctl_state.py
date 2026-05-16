#!/usr/bin/env python3
from pathlib import Path
import os
import sys


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


domain = env("DOMAIN_NAME")
server_ip = env("SERVER_IP")
forward_port = env("FORWARD_PORT")
letsencrypt_email = env("LETSENCRYPT_EMAIL")
namecheap_username = env("NAMECHEAP_USERNAME")
namecheap_api_user = env("NAMECHEAP_API_USER")
namecheap_api_key = env("NAMECHEAP_API_KEY")
namecheap_client_ip = env("NAMECHEAP_CLIENT_IP")

state = f"""apiVersion: npmctl.com/v1
schemaVersion: 2
certificates:
  - name: ssot-registry-com
    domain_names:
      - {domain}
      - www.{domain}
    certificate_type: letsencrypt
    api_payload:
      provider: letsencrypt
      nice_name: ssot-registry.com
      domain_names:
        - {domain}
        - www.{domain}
      meta:
        letsencrypt_email: {letsencrypt_email}
        letsencrypt_agree: true
        dns_challenge: true
        dns_provider: namecheap
        dns_provider_credentials: |
          dns_namecheap_username = {namecheap_username}
          dns_namecheap_api_user = {namecheap_api_user}
          dns_namecheap_api_key = {namecheap_api_key}
          dns_namecheap_client_ip = {namecheap_client_ip}
    meta:
      managed_by: npmctl
      owner: ssot-registry
      resource_id: cert.ssot-registry
proxy_hosts:
  - domain_names:
      - {domain}
      - www.{domain}
    forward_scheme: http
    forward_host: {server_ip}
    forward_port: {forward_port}
    certificate_ref: cert.ssot-registry
    ssl_forced: 1
    http2_support: 1
    hsts_enabled: 1
    hsts_subdomains: 0
    block_exploits: 1
    caching_enabled: 0
    allow_websocket_upgrade: 1
    meta:
      managed_by: npmctl
      owner: ssot-registry
      resource_id: proxy.ssot-registry
"""

out_dir = Path("desired-state")
out_dir.mkdir(exist_ok=True)
(out_dir / "ssot-registry.yml").write_text(state, encoding="utf-8")
print("Wrote desired-state/ssot-registry.yml")
