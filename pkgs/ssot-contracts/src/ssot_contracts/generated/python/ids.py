from __future__ import annotations

import re

from ssot_contracts.contract_data import CONTRACT_DATA

ENTITY_PREFIXES = CONTRACT_DATA["entity_prefixes"]
ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*:[a-z0-9][a-z0-9._-]*$")
