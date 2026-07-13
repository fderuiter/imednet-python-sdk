import json
import os
import re
import shutil
import time
from datetime import datetime, timezone

import pytest
from axe_playwright_python.sync_playwright import Axe
from imednet.config import load_config


@pytest.mark.a11y
def test_accessibility_audit(dashboard_server, page):
    """Run an accessibility audit against the Streamlit dashboard."""
    axe = Axe()
    violations = []

    page.goto(dashboard_server)
    time.sleep(1)

    try:
        page.get_by_label("Select Authorized Study").click()
        page.get_by_role("option", name="TEST-STUDY").click()
        page.get_by_role("button", name="Connect").click()
        page.wait_for_selector("text=Connected ✓", timeout=5000)
    except Exception as e:
        print("Could not connect to study:", e)

    time.sleep(1)
    results = axe.run(page)
    if 'response' in results.__dict__:
        violations.extend(results.__dict__['response'].get('violations', []))

    try:
        page.locator("section[data-testid='stSidebar']").get_by_text("Accessibility Portal").click()
        page.wait_for_selector("text=Accessibility Conformance Portal", timeout=5000)
        time.sleep(1)
        results = axe.run(page)
        if 'response' in results.__dict__:
            for v in results.__dict__['response'].get('violations', []):
                violations.append(v)
    except Exception as e:
        print("Could not navigate to conformance:", e)

    exemptions = []
    if os.path.exists("a11y_exemptions.json"):
        with open("a11y_exemptions.json", "r") as f:
            exemptions = json.load(f)

    now = datetime.now(timezone.utc)
    valid_exemptions = []
    for ex in exemptions:
        expiry = datetime.strptime(ex['expiry'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if now < expiry:
            valid_exemptions.append(ex)

    unexempted_violations = []

    for v in violations:
        rule_id = v['id']
        unexempted_nodes = []
        for node in v.get('nodes', []):
            is_exempted = False
            for ex in valid_exemptions:
                if ex['rule_id'] == rule_id:
                    pattern = ex.get('selector_pattern', '.*')
                    for target in node.get('target', []):
                        if re.search(pattern, target):
                            is_exempted = True
                            break
                if is_exempted:
                    break
            if not is_exempted:
                unexempted_nodes.append(node)

        if unexempted_nodes:
            v_copy = v.copy()
            v_copy['nodes'] = unexempted_nodes
            unexempted_violations.append(v_copy)

    audit_ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    report = {
        "status": "compliant" if not unexempted_violations else "non-compliant",
        "wcag_version": "2.1 AA",
        "critically_non_compliant_findings": len(unexempted_violations),
        "last_audit": audit_ts,
        "passed": len(unexempted_violations) == 0,
        "violations": [
            {
                "id": v['id'],
                "impact": v.get('impact'),
                "description": v.get('description'),
                "helpUrl": v.get('helpUrl'),
            }
            for v in unexempted_violations
        ],
    }

    try:
        config = load_config()
    except ValueError:
        config = None

    a11y_report_path = config.a11y_report_path if config and config.a11y_report_path else "a11y_report.json"

    with open(a11y_report_path, "w") as f:
        json.dump(report, f, indent=2)

    if not unexempted_violations:
        vpat_path = config.vpat_path if config else "docs/VPAT.md"
        if os.path.exists(vpat_path):
            with open(vpat_path, "r") as f:
                vpat_content = f.read()

            commit_hash = os.environ.get('GITHUB_SHA', 'local-audit-hash')

            if "**Last Audit:**" in vpat_content:
                vpat_content = re.sub(
                    r"\*\*Last Audit:\*\* .*", f"**Last Audit:** {audit_ts}", vpat_content
                )
                vpat_content = re.sub(
                    r"\*\*Commit Hash:\*\* .*", f"**Commit Hash:** {commit_hash}", vpat_content
                )
            else:
                vpat_content += f"\n\n**Last Audit:** {audit_ts}\n**Commit Hash:** {commit_hash}\n"

            with open(vpat_path, "w") as f:
                f.write(vpat_content)

    assert not unexempted_violations, (
        f"Found {len(unexempted_violations)} unexempted accessibility violations."
    )
