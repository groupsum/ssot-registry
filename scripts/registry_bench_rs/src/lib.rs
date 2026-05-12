use pyo3::exceptions::PyKeyError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pythonize::pythonize;
use serde_json::{json, Map, Value};

fn parse_registry(payload: &[u8]) -> PyResult<Value> {
    serde_json::from_slice(payload).map_err(|err| PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string()))
}

fn dump_registry(py: Python<'_>, registry: &Value) -> PyResult<Py<PyBytes>> {
    let bytes = serde_json::to_vec(registry)
        .map_err(|err| PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string()))?;
    Ok(PyBytes::new_bound(py, &bytes).into())
}

fn section<'a>(registry: &'a Value, name: &str) -> PyResult<&'a Vec<Value>> {
    registry
        .get(name)
        .and_then(Value::as_array)
        .ok_or_else(|| PyErr::new::<PyKeyError, _>(format!("missing section {name}")))
}

fn section_mut<'a>(registry: &'a mut Value, name: &str) -> PyResult<&'a mut Vec<Value>> {
    registry
        .get_mut(name)
        .and_then(Value::as_array_mut)
        .ok_or_else(|| PyErr::new::<PyKeyError, _>(format!("missing section {name}")))
}

fn row_by_id<'a>(rows: &'a [Value], entity_id: &str) -> PyResult<&'a Value> {
    rows.iter()
        .find(|row| row.get("id").and_then(Value::as_str) == Some(entity_id))
        .ok_or_else(|| PyErr::new::<PyKeyError, _>(entity_id.to_owned()))
}

fn row_by_id_mut<'a>(rows: &'a mut [Value], entity_id: &str) -> PyResult<&'a mut Value> {
    rows.iter_mut()
        .find(|row| row.get("id").and_then(Value::as_str) == Some(entity_id))
        .ok_or_else(|| PyErr::new::<PyKeyError, _>(entity_id.to_owned()))
}

fn feature_row(index: usize) -> Value {
    let feature_id = format!("feat:bench.feature-{index:06}");
    let status = if index % 5 == 0 { "implemented" } else { "partial" };
    json!({
        "id": feature_id,
        "title": format!("Benchmark feature {index:06}"),
        "description": "Synthetic benchmark feature row with enough descriptive payload to simulate real registry growth while remaining targetable and independently linked.",
        "implementation_status": status,
        "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": Value::Null},
        "plan": {"horizon": "current", "slot": Value::Null, "target_claim_tier": "T1", "target_lifecycle_stage": "active"},
        "spec_ids": [],
        "claim_ids": [format!("clm:bench.claim-{index:06}")],
        "test_ids": [format!("tst:bench.test-{index:06}")],
        "requires": [],
    })
}

fn lowercase_field(row: &Value, field: &str) -> String {
    row.get(field)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_ascii_lowercase()
}

fn read_index<'a>(registry: &'a Value, section_name: &str) -> PyResult<Map<String, Value>> {
    let mut map = Map::new();
    for row in section(registry, section_name)? {
        if let Some(entity_id) = row.get("id").and_then(Value::as_str) {
            map.insert(entity_id.to_owned(), row.clone());
        }
    }
    Ok(map)
}

#[pyfunction]
fn create_feature(py: Python<'_>, payload: &[u8], index: usize) -> PyResult<Py<PyBytes>> {
    let mut registry = parse_registry(payload)?;
    section_mut(&mut registry, "features")?.push(feature_row(index));
    dump_registry(py, &registry)
}

#[pyfunction]
fn read_feature(py: Python<'_>, payload: &[u8], entity_id: &str) -> PyResult<PyObject> {
    let registry = parse_registry(payload)?;
    let row = row_by_id(section(&registry, "features")?, entity_id)?;
    let obj = pythonize(py, row)
        .map_err(|err| PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string()))?;
    Ok(obj.into())
}

#[pyfunction]
fn update_feature(py: Python<'_>, payload: &[u8], entity_id: &str, suffix: &str) -> PyResult<Py<PyBytes>> {
    let mut registry = parse_registry(payload)?;
    let rows = section_mut(&mut registry, "features")?;
    let row = row_by_id_mut(rows, entity_id)?;
    let current = row
        .get("description")
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned();
    if let Some(object) = row.as_object_mut() {
        object.insert("description".to_owned(), Value::String(format!("{current}{suffix}")));
    }
    dump_registry(py, &registry)
}

#[pyfunction]
fn delete_feature(py: Python<'_>, payload: &[u8], entity_id: &str) -> PyResult<Py<PyBytes>> {
    let mut registry = parse_registry(payload)?;
    let rows = section_mut(&mut registry, "features")?;
    rows.retain(|row| row.get("id").and_then(Value::as_str) != Some(entity_id));
    dump_registry(py, &registry)
}

#[pyfunction]
fn list_features(payload: &[u8]) -> PyResult<Vec<String>> {
    let registry = parse_registry(payload)?;
    let mut values = section(&registry, "features")?
        .iter()
        .filter_map(|row| row.get("id").and_then(Value::as_str).map(str::to_owned))
        .collect::<Vec<_>>();
    values.sort();
    Ok(values)
}

#[pyfunction]
fn traverse_children(py: Python<'_>, payload: &[u8], feature_id: &str) -> PyResult<PyObject> {
    let registry = parse_registry(payload)?;
    let features = read_index(&registry, "features")?;
    let claims = read_index(&registry, "claims")?;
    let tests = read_index(&registry, "tests")?;
    let evidence = read_index(&registry, "evidence")?;
    let feature = features
        .get(feature_id)
        .ok_or_else(|| PyErr::new::<PyKeyError, _>(feature_id.to_owned()))?;
    let mut rows = vec![feature.clone()];
    if let Some(ids) = feature.get("claim_ids").and_then(Value::as_array) {
        for claim_id in ids.iter().filter_map(Value::as_str) {
            if let Some(row) = claims.get(claim_id) {
                rows.push(row.clone());
            }
        }
    }
    if let Some(ids) = feature.get("test_ids").and_then(Value::as_array) {
        for test_id in ids.iter().filter_map(Value::as_str) {
            if let Some(test) = tests.get(test_id) {
                rows.push(test.clone());
                if let Some(evidence_ids) = test.get("evidence_ids").and_then(Value::as_array) {
                    for evidence_id in evidence_ids.iter().filter_map(Value::as_str) {
                        if let Some(row) = evidence.get(evidence_id) {
                            rows.push(row.clone());
                        }
                    }
                }
            }
        }
    }
    let obj = pythonize(py, &rows)
        .map_err(|err| PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string()))?;
    Ok(obj.into())
}

#[pyfunction]
fn traverse_parents(py: Python<'_>, payload: &[u8], test_id: &str) -> PyResult<PyObject> {
    let registry = parse_registry(payload)?;
    let features = read_index(&registry, "features")?;
    let claims = read_index(&registry, "claims")?;
    let tests = read_index(&registry, "tests")?;
    let evidence = read_index(&registry, "evidence")?;
    let test = tests
        .get(test_id)
        .ok_or_else(|| PyErr::new::<PyKeyError, _>(test_id.to_owned()))?;
    let mut rows = vec![test.clone()];
    if let Some(ids) = test.get("feature_ids").and_then(Value::as_array) {
        for feature_id in ids.iter().filter_map(Value::as_str) {
            if let Some(row) = features.get(feature_id) {
                rows.push(row.clone());
            }
        }
    }
    if let Some(ids) = test.get("claim_ids").and_then(Value::as_array) {
        for claim_id in ids.iter().filter_map(Value::as_str) {
            if let Some(row) = claims.get(claim_id) {
                rows.push(row.clone());
            }
        }
    }
    if let Some(ids) = test.get("evidence_ids").and_then(Value::as_array) {
        for evidence_id in ids.iter().filter_map(Value::as_str) {
            if let Some(row) = evidence.get(evidence_id) {
                rows.push(row.clone());
            }
        }
    }
    let obj = pythonize(py, &rows)
        .map_err(|err| PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string()))?;
    Ok(obj.into())
}

#[pyfunction]
fn search_features(payload: &[u8], query: &str) -> PyResult<Vec<String>> {
    let registry = parse_registry(payload)?;
    let query_lower = query.to_ascii_lowercase();
    let mut out = Vec::new();
    for row in section(&registry, "features")? {
        let title = lowercase_field(row, "title");
        let description = lowercase_field(row, "description");
        let status = lowercase_field(row, "implementation_status");
        if (title.contains(&query_lower) || description.contains(&query_lower) || status == query_lower)
            && row.get("id").and_then(Value::as_str).is_some()
        {
            out.push(row.get("id").and_then(Value::as_str).unwrap().to_owned());
        }
    }
    Ok(out)
}

#[pymodule]
fn registry_bench_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(create_feature, m)?)?;
    m.add_function(wrap_pyfunction!(read_feature, m)?)?;
    m.add_function(wrap_pyfunction!(update_feature, m)?)?;
    m.add_function(wrap_pyfunction!(delete_feature, m)?)?;
    m.add_function(wrap_pyfunction!(list_features, m)?)?;
    m.add_function(wrap_pyfunction!(traverse_children, m)?)?;
    m.add_function(wrap_pyfunction!(traverse_parents, m)?)?;
    m.add_function(wrap_pyfunction!(search_features, m)?)?;
    Ok(())
}
