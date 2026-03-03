## Summary
- [ ] What changed
- [ ] Why it changed

## Business Impact
- [ ] Expected impact on insights or decision quality
- [ ] Risks and mitigations

## Data Governance
- [ ] Kaggle provenance updated (if dataset changed)
- [ ] No raw sensitive data committed

## Quality Gates
- [ ] `python -m ruff check src config scripts dashboard tests`
- [ ] `python -m pytest`
- [ ] `python scripts/check_encoding.py`
- [ ] `python scripts/streamlit_cloud_preflight.py`
- [ ] `python scripts/validate_data_provenance.py`

## Deployment Notes
- [ ] Streamlit Cloud impact assessed
- [ ] Secrets/config changes documented
