from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as package_version

from .api import (
    InvalidPackManifestError,
    InvalidPackMetadataError,
    PackContractError,
    PackDocumentEntry,
    PackMetadata,
    UnsupportedDocumentKindError,
    bind_pack_contract,
    list_packaged_document_ids,
    get_packaged_document_entry,
    load_document_manifest,
    load_pack_manifest,
    load_pack_metadata,
    load_pack_schema_version,
    normalize_document_kind,
    read_packaged_document_bytes,
    read_packaged_document_text,
    validate_pack_document_entry,
    validate_pack_metadata,
)

__ssot_package_name__ = "ssot-pack-contracts"

try:
    __version__ = package_version(__ssot_package_name__)
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "__ssot_package_name__",
    "PackMetadata",
    "PackDocumentEntry",
    "PackContractError",
    "UnsupportedDocumentKindError",
    "InvalidPackMetadataError",
    "InvalidPackManifestError",
    "bind_pack_contract",
    "load_pack_metadata",
    "load_pack_schema_version",
    "load_pack_manifest",
    "load_document_manifest",
    "read_packaged_document_bytes",
    "read_packaged_document_text",
    "validate_pack_metadata",
    "validate_pack_document_entry",
    "normalize_document_kind",
    "list_packaged_document_ids",
    "get_packaged_document_entry",
]
