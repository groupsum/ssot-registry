# Migration Rules

When a schema change is breaking:

- advance the schema version
- add or update the migration function in `pkgs/ssot-core/src/ssot_registry/api/upgrade.py`
- cover the migration with tests
- update checked-in fixtures or reports that encode the old or new shape

Do not claim conformance if the schema changed but the upgrade path did not.
