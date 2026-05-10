#!/usr/bin/env python3
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


API_URL = "https://api.namecheap.com/xml.response"
NS = {"nc": "http://api.namecheap.com/xml.response"}


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def request(command: str, params: dict[str, str]) -> ET.Element:
    query = {
        "ApiUser": env("NAMECHEAP_API_USER"),
        "ApiKey": env("NAMECHEAP_API_KEY"),
        "UserName": env("NAMECHEAP_USERNAME"),
        "ClientIp": env("NAMECHEAP_CLIENT_IP"),
        "Command": command,
        **params,
    }
    url = f"{API_URL}?{urllib.parse.urlencode(query)}"
    with urllib.request.urlopen(url, timeout=60) as response:
        body = response.read()

    root = ET.fromstring(body)
    if root.attrib.get("Status") != "OK":
        errors = [item.text or "unknown error" for item in root.findall(".//nc:Error", NS)]
        raise SystemExit(f"Namecheap API error: {'; '.join(errors)}")
    return root


def split_domain(domain: str) -> tuple[str, str]:
    parts = domain.split(".", 1)
    if len(parts) != 2:
        raise SystemExit(f"Expected a second-level domain, got: {domain}")
    return parts[0], parts[1]


def existing_hosts(domain: str) -> list[dict[str, str]]:
    sld, tld = split_domain(domain)
    root = request("namecheap.domains.dns.getHosts", {"SLD": sld, "TLD": tld})
    hosts = []
    for host in root.findall(".//nc:host", NS):
        attrs = dict(host.attrib)
        name = attrs.get("Name") or attrs.get("HostName")
        record_type = attrs.get("Type") or attrs.get("RecordType")
        address = attrs.get("Address")
        if name and record_type and address:
            hosts.append(
                {
                    "Name": name,
                    "Type": record_type,
                    "Address": address,
                    "TTL": attrs.get("TTL", "300"),
                    "MXPref": attrs.get("MXPref", ""),
                }
            )
    return hosts


def set_hosts(domain: str, hosts: list[dict[str, str]]) -> None:
    sld, tld = split_domain(domain)
    params: dict[str, str] = {"SLD": sld, "TLD": tld}
    for index, host in enumerate(hosts, start=1):
        params[f"HostName{index}"] = host["Name"]
        params[f"RecordType{index}"] = host["Type"]
        params[f"Address{index}"] = host["Address"]
        params[f"TTL{index}"] = host.get("TTL", "300")
        if host.get("MXPref"):
            params[f"MXPref{index}"] = host["MXPref"]
    request("namecheap.domains.dns.setHosts", params)


def main() -> int:
    domain = env("DOMAIN_NAME")
    server_ip = env("SERVER_IP")
    wanted = {
        "@": {"Name": "@", "Type": "A", "Address": server_ip, "TTL": "300"},
        "www": {"Name": "www", "Type": "A", "Address": server_ip, "TTL": "300"},
    }
    hosts = [host for host in existing_hosts(domain) if host.get("Name") not in wanted]
    hosts.extend(wanted.values())
    set_hosts(domain, hosts)
    print(f"Upserted apex and www A records for {domain}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
