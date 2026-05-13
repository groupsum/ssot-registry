from __future__ import annotations

import hashlib
import importlib
import json
import re
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as distribution_metadata
from importlib.metadata import packages_distributions
from importlib.metadata import version as distribution_version
from importlib import resources
from types import ModuleType
from typing import Any


METADATA_RESOURCE = "metadata.json"
SUPPORTED_DOCUMENT_KINDS = {"adr": "adr", "adrs": "adr", "spec": "spec", "specs": "spec"}
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
PACK_ID_PATTERN = re.compile(r"^pack:[a-z0-9][a-z0-9._-]*$")


class PackContractError(ValueError):
    """Base exception for governance-pack contract failures."""


class UnsupportedDocumentKindError(PackContractError):
    """Raised when a caller requests a document kind outside the pack contract."""


class InvalidPackMetadataError(PackContractError):
    """Raised when packaged governance-pack metadata is missing or invalid."""


class InvalidPackManifestError(PackContractError):
    """Raised when a packaged document manifest or resource is invalid."""


@dataclass(frozen=True)
class PackMetadata:
    schema_version: str
    ssot_package_name: str
    pypi_package_name: str
    origin: dict[str, Any]
    compatibility: dict[str, Any]
    trust: dict[str, Any]
    documents: dict[str, Any]
    version: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ssot_package_name": self.ssot_package_name,
            "pypi_package_name": self.pypi_package_name,
            "origin": dict(self.origin),
            "compatibility": dict(self.compatibility),
            "trust": dict(self.trust),
            "documents": dict(self.documents),
            "version": self.version,
        }


@dataclass(frozen=True)
class PackDocumentEntry:
    id: str
    number: int
    slug: str
    title: str
    filename: str
    target_path: str
    sha256: str
    origin: str
    reservation_owner: str
    immutable: bool
    minimum_schema_version: str
    introduced_in: str
    status: str
    supersedes: list[str]
    superseded_by: list[str]
    status_notes: list[dict[str, Any]]
    kind: str | None = None
    adr_ids: list[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "number": self.number,
            "slug": self.slug,
            "title": self.title,
            "filename": self.filename,
            "target_path": self.target_path,
            "sha256": self.sha256,
            "origin": self.origin,
            "reservation_owner": self.reservation_owner,
            "immutable": self.immutable,
            "minimum_schema_version": self.minimum_schema_version,
            "introduced_in": self.introduced_in,
            "status": self.status,
            "supersedes": list(self.supersedes),
            "superseded_by": list(self.superseded_by),
            "status_notes": [dict(row) for row in self.status_notes],
        }
        if self.kind is not None:
            payload["kind"] = self.kind
        if self.adr_ids is not None:
            payload["adr_ids"] = list(self.adr_ids)
        return payload


def _module(package: str | ModuleType | None) -> ModuleType:
    if package is None:
        raise InvalidPackMetadataError("A governance pack package name or module is required")
    if isinstance(package, ModuleType):
        return package
    return importlib.import_module(package)


def _resource_text(module: ModuleType, resource_name: str) -> str:
    resource = resources.files(module).joinpath(resource_name)
    if not resource.is_file():
        raise InvalidPackMetadataError(f"Governance pack {module.__name__} is missing packaged {resource_name}")
    return resource.read_text(encoding="utf-8")


def _normalized_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _distribution_identity_for_module(module: ModuleType, *, expected_name: str | None = None) -> tuple[str, str]:
    top_level = module.__name__.split(".", 1)[0]
    dist_names = packages_distributions().get(top_level, [])
    if not dist_names:
        raise InvalidPackMetadataError(f"No installed distribution found for import package {top_level}")

    candidates: list[tuple[str, str]] = []
    for dist_name in dist_names:
        try:
            resolved_name = distribution_metadata(dist_name)["Name"]
            resolved_version = distribution_version(dist_name)
        except (KeyError, PackageNotFoundError) as exc:
            raise InvalidPackMetadataError(f"Distribution metadata for {dist_name} is not readable") from exc
        candidates.append((resolved_name, resolved_version))

    if expected_name is not None:
        normalized_expected = _normalized_distribution_name(expected_name)
        matches = [candidate for candidate in candidates if _normalized_distribution_name(candidate[0]) == normalized_expected]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            unique_matches = sorted(set(matches))
            if len(unique_matches) == 1:
                return unique_matches[0]
            raise InvalidPackMetadataError(f"Multiple installed distributions match expected package name {expected_name}")

    if len(candidates) == 1:
        return candidates[0]
    unique_candidates = sorted(set(candidates))
    if len(unique_candidates) == 1:
        return unique_candidates[0]
    names = ", ".join(name for name, _ in candidates)
    raise InvalidPackMetadataError(f"Import package {top_level} maps to multiple installed distributions: {names}")


def _json_object(text: str, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidPackMetadataError(f"{label} must be valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise InvalidPackMetadataError(f"{label} must decode to a JSON object")
    return payload


def normalize_document_kind(kind: str) -> str:
    try:
        return SUPPORTED_DOCUMENT_KINDS[kind]
    except KeyError as exc:
        raise UnsupportedDocumentKindError(f"Unsupported governance-pack document kind: {kind}") from exc


def validate_pack_metadata(
    metadata: dict[str, Any],
    *,
    import_name: str | None = None,
    pypi_package_name: str | None = None,
    version: str | None = None,
) -> PackMetadata:
    schema_version = metadata.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        raise InvalidPackMetadataError("metadata.schema_version is required")
    ssot_package_name = metadata.get("ssot_package_name")
    if not isinstance(ssot_package_name, str) or not ssot_package_name.strip():
        raise InvalidPackMetadataError("metadata.ssot_package_name is required")
    origin = metadata.get("origin")
    compatibility = metadata.get("compatibility")
    trust = metadata.get("trust")
    documents = metadata.get("documents")
    if not isinstance(origin, dict):
        raise InvalidPackMetadataError("metadata.origin must be an object")
    if not isinstance(compatibility, dict):
        raise InvalidPackMetadataError("metadata.compatibility must be an object")
    if not isinstance(trust, dict):
        raise InvalidPackMetadataError("metadata.trust must be an object")
    if not isinstance(documents, dict):
        raise InvalidPackMetadataError("metadata.documents must be an object")
    origin_id = origin.get("id")
    if not isinstance(origin_id, str) or PACK_ID_PATTERN.match(origin_id) is None:
        raise InvalidPackMetadataError("metadata.origin.id must be a normalized pack:* identifier")
    package_name = origin.get("package_name")
    if not isinstance(package_name, str) or not package_name.strip():
        raise InvalidPackMetadataError("metadata.origin.package_name is required")
    if package_name != ssot_package_name:
        raise InvalidPackMetadataError("metadata.origin.package_name must match metadata.ssot_package_name")
    metadata_import_name = origin.get("import_name")
    if not isinstance(metadata_import_name, str) or not metadata_import_name.strip():
        raise InvalidPackMetadataError("metadata.origin.import_name is required")
    if import_name is not None and metadata_import_name != import_name:
        raise InvalidPackMetadataError(f"metadata.origin.import_name must be {import_name}, got {metadata_import_name}")
    if origin.get("kind") != "governance-pack":
        raise InvalidPackMetadataError("metadata.origin.kind must be governance-pack")
    if trust.get("origin") != "extension-pack":
        raise InvalidPackMetadataError("metadata.trust.origin must be extension-pack")
    if "trusted_by_default" not in trust or not isinstance(trust.get("trusted_by_default"), bool):
        raise InvalidPackMetadataError("metadata.trust.trusted_by_default must be a boolean")
    reservation_owner = trust.get("reservation_owner")
    if not isinstance(reservation_owner, str) or not reservation_owner.startswith("extension-pack:"):
        raise InvalidPackMetadataError("metadata.trust.reservation_owner must start with extension-pack:")
    for key in ("python", "ssot_registry_schema", "ssot_pack_contract"):
        if not isinstance(compatibility.get(key), str) or not compatibility[key].strip():
            raise InvalidPackMetadataError(f"metadata.compatibility.{key} is required")
    for raw_kind, value in documents.items():
        kind = normalize_document_kind(str(raw_kind))
        if kind != raw_kind:
            raise InvalidPackMetadataError(f"metadata.documents must use normalized kind key {kind}, got {raw_kind}")
        if not isinstance(value, dict) or not isinstance(value.get("manifest_path"), str) or not value["manifest_path"].strip():
            raise InvalidPackMetadataError(f"metadata.documents.{kind}.manifest_path is required")
    return PackMetadata(
        schema_version=schema_version,
        ssot_package_name=ssot_package_name,
        pypi_package_name=pypi_package_name or ssot_package_name,
        origin=dict(origin),
        compatibility=dict(compatibility),
        trust=dict(trust),
        documents=dict(documents),
        version=version or "",
    )


def load_pack_metadata(package: str | ModuleType) -> dict[str, Any]:
    module = _module(package)
    metadata = _json_object(_resource_text(module, METADATA_RESOURCE), label=METADATA_RESOURCE)
    ssot_package_name = metadata.get("ssot_package_name")
    pypi_package_name, version = _distribution_identity_for_module(
        module,
        expected_name=ssot_package_name if isinstance(ssot_package_name, str) else None,
    )
    validated = validate_pack_metadata(
        metadata,
        import_name=module.__name__,
        pypi_package_name=pypi_package_name,
        version=version,
    )
    return validated.as_dict()


def load_pack_schema_version(package: str | ModuleType) -> str:
    return load_pack_metadata(package)["schema_version"]


def _manifest_path(metadata: dict[str, Any], kind: str) -> str:
    documents = metadata.get("documents")
    if not isinstance(documents, dict) or kind not in documents:
        raise InvalidPackManifestError(f"Governance pack does not declare a {kind} document manifest")
    declaration = documents[kind]
    if not isinstance(declaration, dict) or not isinstance(declaration.get("manifest_path"), str):
        raise InvalidPackManifestError(f"Governance pack {kind} manifest_path is invalid")
    return declaration["manifest_path"]


def validate_pack_document_entry(entry: dict[str, Any], *, kind: str) -> PackDocumentEntry:
    normalized_kind = normalize_document_kind(kind)
    required = [
        "id",
        "number",
        "slug",
        "title",
        "filename",
        "target_path",
        "sha256",
        "origin",
        "reservation_owner",
        "immutable",
        "minimum_schema_version",
        "introduced_in",
        "status",
        "supersedes",
        "superseded_by",
        "status_notes",
    ]
    missing = [field for field in required if field not in entry]
    if missing:
        raise InvalidPackManifestError(f"{normalized_kind} manifest entry missing required fields: {', '.join(missing)}")
    if normalized_kind == "spec" and "kind" not in entry:
        raise InvalidPackManifestError("spec manifest entry missing required field: kind")
    if not isinstance(entry["id"], str) or not entry["id"].startswith("adr:" if normalized_kind == "adr" else "spc:"):
        raise InvalidPackManifestError(f"{normalized_kind} manifest entry id has the wrong prefix")
    if not isinstance(entry["number"], int):
        raise InvalidPackManifestError(f"{entry.get('id', normalized_kind)} number must be an integer")
    if not isinstance(entry["sha256"], str) or SHA256_PATTERN.match(entry["sha256"]) is None:
        raise InvalidPackManifestError(f"{entry.get('id', normalized_kind)} sha256 must be lowercase hex")
    for field in ("slug", "title", "filename", "target_path", "origin", "reservation_owner", "minimum_schema_version", "introduced_in", "status"):
        if not isinstance(entry[field], str) or not entry[field].strip():
            raise InvalidPackManifestError(f"{entry.get('id', normalized_kind)} {field} must be a non-empty string")
    if not isinstance(entry["immutable"], bool):
        raise InvalidPackManifestError(f"{entry['id']} immutable must be a boolean")
    for field in ("supersedes", "superseded_by", "status_notes"):
        if not isinstance(entry[field], list):
            raise InvalidPackManifestError(f"{entry['id']} {field} must be a list")
    return PackDocumentEntry(
        id=entry["id"],
        number=entry["number"],
        slug=entry["slug"],
        title=entry["title"],
        filename=entry["filename"],
        target_path=entry["target_path"],
        sha256=entry["sha256"],
        origin=entry["origin"],
        reservation_owner=entry["reservation_owner"],
        immutable=entry["immutable"],
        minimum_schema_version=entry["minimum_schema_version"],
        introduced_in=entry["introduced_in"],
        status=entry["status"],
        supersedes=list(entry["supersedes"]),
        superseded_by=list(entry["superseded_by"]),
        status_notes=list(entry["status_notes"]),
        kind=entry.get("kind") if normalized_kind == "spec" else None,
        adr_ids=list(entry.get("adr_ids", [])) if normalized_kind == "spec" else None,
    )


def load_document_manifest(package: str | ModuleType, kind: str) -> list[dict[str, Any]]:
    module = _module(package)
    normalized_kind = normalize_document_kind(kind)
    metadata = load_pack_metadata(module)
    manifest_path = _manifest_path(metadata, normalized_kind)
    resource = resources.files(module).joinpath(manifest_path)
    if not resource.is_file():
        raise InvalidPackManifestError(f"Governance pack {module.__name__} is missing manifest {manifest_path}")
    try:
        manifest = json.loads(resource.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InvalidPackManifestError(f"{manifest_path} must be valid JSON: {exc.msg}") from exc
    if not isinstance(manifest, list):
        raise InvalidPackManifestError(f"{manifest_path} must decode to a JSON array")
    return [validate_pack_document_entry(row, kind=normalized_kind).as_dict() for row in manifest]


def load_pack_manifest(package: str | ModuleType) -> dict[str, Any]:
    module = _module(package)
    metadata = load_pack_metadata(module)
    manifests: dict[str, list[dict[str, Any]]] = {}
    for kind in sorted(metadata["documents"]):
        manifests[kind] = load_document_manifest(module, kind)
    return {"metadata": metadata, "documents": manifests}


def _entry_for_filename(package: str | ModuleType, kind: str, filename: str) -> dict[str, Any]:
    normalized_kind = normalize_document_kind(kind)
    for entry in load_document_manifest(package, normalized_kind):
        if entry["filename"] == filename:
            return entry
    raise InvalidPackManifestError(f"{normalized_kind} manifest does not declare document file {filename}")


def read_packaged_document_bytes(package: str | ModuleType, kind: str, filename: str) -> bytes:
    module = _module(package)
    normalized_kind = normalize_document_kind(kind)
    entry = _entry_for_filename(module, normalized_kind, filename)
    manifest_path = _manifest_path(load_pack_metadata(module), normalized_kind)
    resource = resources.files(module).joinpath(manifest_path).parent.joinpath(filename)
    if not resource.is_file():
        raise InvalidPackManifestError(f"Governance pack {module.__name__} is missing document resource {filename}")
    payload = resource.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != entry["sha256"]:
        raise InvalidPackManifestError(f"{entry['id']} sha256 mismatch: expected {entry['sha256']}, got {actual}")
    return payload


def read_packaged_document_text(package: str | ModuleType, kind: str, filename: str) -> str:
    return read_packaged_document_bytes(package, kind, filename).decode("utf-8-sig")


def list_packaged_document_ids(package: str | ModuleType, kind: str | None = None) -> list[str]:
    if kind is not None:
        return [entry["id"] for entry in load_document_manifest(package, kind)]
    manifest = load_pack_manifest(package)
    ids: list[str] = []
    for entries in manifest["documents"].values():
        ids.extend(entry["id"] for entry in entries)
    return sorted(ids)


def get_packaged_document_entry(package: str | ModuleType, document_id: str) -> dict[str, Any]:
    for kind in ("adr", "spec"):
        for entry in load_document_manifest(package, kind):
            if entry["id"] == document_id:
                return entry
    raise InvalidPackManifestError(f"Unknown packaged document id: {document_id}")


def bind_pack_contract(package: str | ModuleType) -> dict[str, Any]:
    module = _module(package)
    metadata = load_pack_metadata(module)

    def bound_load_pack_metadata() -> dict[str, Any]:
        return load_pack_metadata(module)

    def bound_load_pack_schema_version() -> str:
        return load_pack_schema_version(module)

    def bound_load_pack_manifest() -> dict[str, Any]:
        return load_pack_manifest(module)

    def bound_load_document_manifest(kind: str) -> list[dict[str, Any]]:
        return load_document_manifest(module, kind)

    def bound_read_packaged_document_bytes(kind: str, filename: str) -> bytes:
        return read_packaged_document_bytes(module, kind, filename)

    def bound_read_packaged_document_text(kind: str, filename: str) -> str:
        return read_packaged_document_text(module, kind, filename)

    def bound_list_packaged_document_ids(kind: str | None = None) -> list[str]:
        return list_packaged_document_ids(module, kind)

    def bound_get_packaged_document_entry(document_id: str) -> dict[str, Any]:
        return get_packaged_document_entry(module, document_id)

    exported = {
        "__version__": metadata["version"],
        "__ssot_package_name__": metadata["ssot_package_name"],
        "__pypi_package_name__": metadata["pypi_package_name"],
        "load_pack_metadata": bound_load_pack_metadata,
        "load_pack_schema_version": bound_load_pack_schema_version,
        "load_pack_manifest": bound_load_pack_manifest,
        "load_document_manifest": bound_load_document_manifest,
        "read_packaged_document_bytes": bound_read_packaged_document_bytes,
        "read_packaged_document_text": bound_read_packaged_document_text,
        "list_packaged_document_ids": bound_list_packaged_document_ids,
        "get_packaged_document_entry": bound_get_packaged_document_entry,
    }
    exported["__all__"] = sorted(exported.keys())
    return exported
