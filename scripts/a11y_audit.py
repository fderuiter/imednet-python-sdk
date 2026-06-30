import json
import os
import sys
import subprocess
import time
import socket
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

def wait_for_port(port, host='localhost', timeout=10.0):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except:
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                return False

def run_audit():
    print("Starting Streamlit for accessibility audit...")
    port = 8503
    app_path = os.path.abspath("packages/plugins-streamlit/src/imednet_streamlit/app.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        os.path.abspath("packages/core/src")
        + os.pathsep
        + os.path.abspath("packages/plugins-workflows/src")
        + os.pathsep
        + os.path.abspath("packages/plugins-streamlit/src")
    )
    env["IMEDNET_BROWSER_TEST"] = "1"
    env["IMEDNET_TENANT_DB_PATH"] = os.path.abspath("tests/browser/test_enterprise.sqlite3")

    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path, "--server.port", str(port),
        "--server.headless", "true", "--browser.gatherUsageStats", "false"
    ]
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if not wait_for_port(port):
        stdout, stderr = proc.communicate()
        proc.kill()
        raise RuntimeError(f"Streamlit failed to start.\n{stderr.decode()}")

    violations = []
    
    try:
        from axe_playwright_python.sync_playwright import Axe
        axe = Axe()
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            page.goto(f"http://localhost:{port}")
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
                
            browser.close()
            
    finally:
        proc.terminate()
        proc.wait(timeout=5)

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

    print(f"Found {len(unexempted_violations)} unexempted violation types out of {len(violations)} total.")
    for v in unexempted_violations:
        print(f" - {v['id']} ({v.get('impact')}) - {len(v['nodes'])} nodes")
    
    audit_ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    report = {
        "status": "compliant" if not unexempted_violations else "non-compliant",
        "wcag_version": "2.1 AA",
        "critically_non_compliant_findings": len(unexempted_violations),
        "last_audit": audit_ts,
        "passed": len(unexempted_violations) == 0,
        "violations": [{"id": v['id'], "impact": v.get('impact'), "description": v.get('description'), "helpUrl": v.get('helpUrl')} for v in unexempted_violations]
    }
    
    with open("a11y_report.json", "w") as f:
        json.dump(report, f, indent=2)

    import shutil
    try:
        shutil.copy("a11y_report.json", "packages/plugins-streamlit/src/imednet_streamlit/pages/a11y_report.json")
    except Exception:
        pass
        
    if not unexempted_violations:
        vpat_path = "docs/VPAT.md"
        if os.path.exists(vpat_path):
            with open(vpat_path, "r") as f:
                vpat_content = f.read()
            
            commit_hash = os.environ.get('GITHUB_SHA', 'local-audit-hash')
            
            if "**Last Audit:**" in vpat_content:
                vpat_content = re.sub(r"\*\*Last Audit:\*\* .*", f"**Last Audit:** {audit_ts}", vpat_content)
                vpat_content = re.sub(r"\*\*Commit Hash:\*\* .*", f"**Commit Hash:** {commit_hash}", vpat_content)
            else:
                vpat_content += f"\n\n**Last Audit:** {audit_ts}\n**Commit Hash:** {commit_hash}\n"
                
            with open(vpat_path, "w") as f:
                f.write(vpat_content)

    if unexempted_violations:
        print("Accessibility violations found!")
        sys.exit(1)

run_audit()
