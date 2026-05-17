from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
PLAN_JSON = ARTIFACTS / "content-plan.json"
OUTPUT = ARTIFACTS / "ssot-registry-content-plan.xlsx"

HEADERS = [
    "page_id",
    "slug",
    "title",
    "section",
    "subject_area",
    "intent",
    "audience",
    "aeo_goal",
    "seo_query_target",
    "aieo_agent_fact",
    "structured_data_types",
    "lander_components",
    "related_packages",
    "related_apis",
    "breadcrumbs",
    "summary",
    "primary_cta",
    "word_target",
]


def load_plan() -> dict:
    if not PLAN_JSON.exists():
        raise SystemExit(f"missing {PLAN_JSON}; run npm run plan:json first")
    return json.loads(PLAN_JSON.read_text(encoding="utf-8"))


def page_row(page: dict) -> list[str | int]:
    return [
        page["pageId"],
        page["slug"],
        page["title"],
        page["section"],
        page["subjectArea"],
        page["intent"],
        page["audience"],
        page["aeoGoal"],
        page["seoQueryTarget"],
        page["aieoAgentFact"],
        ", ".join(page["structuredDataTypes"]),
        ", ".join(page["landerComponents"]),
        ", ".join(page["relatedPackages"]),
        ", ".join(page["relatedApis"]),
        " > ".join(page["breadcrumbs"]),
        page["summary"],
        page["primaryCta"],
        page["wordTarget"],
    ]


def make_workbook(plan: dict) -> dict[str, list[list[str | int]]]:
    pages = plan["pages"]
    sections = [section["id"] for section in plan["sections"]]
    pages_by_section = {
        section: [page for page in pages if page["section"] == section]
        for section in sections
    }

    sheets: dict[str, list[list[str | int]]] = {}
    sheets["Summary"] = [
        ["metric", "value"],
        ["total_planned_pages", plan["totalPlannedPages"]],
        ["minimum_required_pages", plan["minimumRequiredPages"]],
        ["requirement_met", "yes" if plan["totalPlannedPages"] >= plan["minimumRequiredPages"] else "no"],
        ["section_count", len(plan["sections"])],
        ["pages_per_section", len(next(iter(pages_by_section.values())))],
        ["subject_area_count", len(plan["subjectAreas"])],
        ["audience_count", len(plan["audiences"])],
        ["intent_count_per_section", 4],
        ["combinatorial_formula", plan["formula"]],
    ]
    sheets["Legend"] = [
        ["field", "meaning"],
        ["page_id", "Stable planned content page identifier."],
        ["slug", "Canonical planned page route."],
        ["section", "Site section family; every section has one worksheet."],
        ["subject_area", "SSOT Registry domain topic."],
        ["intent", "AEO/SEO/AiEO content intent for the page."],
        ["audience", "Primary reader or agent audience."],
        ["structured_data_types", "Schema-oriented types the page should emit through lander components."],
        ["lander_components", "Structured-data-backed lander component families planned for the page."],
        ["breadcrumbs", "Planned breadcrumb trail."],
    ]
    sheets["Topic Sets"] = [["set", "value"]]
    sheets["Topic Sets"].extend(["subject_area", item] for item in plan["subjectAreas"])
    sheets["Topic Sets"].extend(["audience", item] for item in plan["audiences"])
    sheets["Topic Sets"].extend(["package", item] for item in plan["relatedPackages"])
    sheets["Topic Sets"].extend(["api", item] for item in plan["relatedApis"])
    sheets["Structured Data"] = [["section", "structured_data_types", "lander_components"]]
    for section in plan["sections"]:
      sheets["Structured Data"].append(
          [section["id"], ", ".join(section["structuredDataTypes"]), ", ".join(section["components"])]
      )
    sheets["Proof"] = [["section", "planned_pages", "formula"]]
    for section, section_pages in pages_by_section.items():
        sheets["Proof"].append([section, len(section_pages), "20 subject areas * 4 intents * 4 audiences"])
    sheets["Proof"].append(["TOTAL", plan["totalPlannedPages"], "sum of section worksheets"])

    for section, section_pages in pages_by_section.items():
        sheets[section] = [HEADERS] + [page_row(page) for page in section_pages]

    return sheets


def xml_cell(value: str | int, row: int, col: int) -> str:
    ref = f"{column_name(col)}{row}"
    if isinstance(value, int):
        return f'<c r="{ref}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def worksheet_xml(rows: Iterable[list[str | int]]) -> str:
    xml_rows = []
    for row_index, values in enumerate(rows, start=1):
        cells = "".join(xml_cell(value, row_index, col_index) for col_index, value in enumerate(values, start=1))
        xml_rows.append(f'<row r="{row_index}">{cells}</row>')
    views = '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"{views}<sheetData>{''.join(xml_rows)}</sheetData></worksheet>"
    )


def workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        f'<sheet name="{escape(name)}" sheetId="{index}" r:id="rId{index}"/>'
        for index, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets}</sheets></workbook>"
    )


def workbook_rels_xml(sheet_names: list[str]) -> str:
    rels = "".join(
        '<Relationship '
        f'Id="rId{index}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{index}.xml"/>'
        for index, _ in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{rels}</Relationships>"
    )


def content_types_xml(sheet_count: int) -> str:
    sheet_overrides = "".join(
        '<Override '
        f'PartName="/xl/worksheets/sheet{index}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for index in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        f"{sheet_overrides}</Types>"
    )


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def write_xlsx(sheets: dict[str, list[list[str | int]]]) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    sheet_names = list(sheets)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(len(sheet_names)))
        archive.writestr("_rels/.rels", root_rels_xml())
        archive.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(sheet_names))
        for index, name in enumerate(sheet_names, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", worksheet_xml(sheets[name]))


def main() -> None:
    plan = load_plan()
    write_xlsx(make_workbook(plan))
    print(f"wrote {OUTPUT}")
    print(f"planned_pages={plan['totalPlannedPages']}")


if __name__ == "__main__":
    main()
