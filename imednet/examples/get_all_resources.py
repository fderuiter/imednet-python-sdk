import os

from imednet.sdk import ImednetSDK as ImednetClient

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    print(f"Studies found: {len(studies)}")
    if not studies:
        print("No studies returned from API.")
    for study in studies[:1]:
        print(f"- Name: {study.study_name}, Key: {study.study_key}")
        study_key = study.study_key

        # Sites
        sites = client.sites.list(study_key=study_key)
        print(f"Sites for study '{study_key}': {len(sites)}")
        for site in sites[:5]:
            print(f"- Site Name: {site.site_name}, ID: {site.site_id}")

        # Subjects
        subjects = client.subjects.list(study_key=study_key)
        print(f"Subjects for study '{study_key}': {len(subjects)}")
        for subject in subjects[:5]:
            print(f"- Subject Key: {subject.subject_key}, Status: {subject.subject_status}")

        # Users
        users = client.users.list(study_key=study_key)
        print(f"Users for study '{study_key}': {len(users)}")
        for user in users[:5]:
            print(f"- User Login: {user.login}, Name: {user.name}")

        # Visits
        visits = client.visits.list(study_key=study_key)
        print(f"Visits for study '{study_key}': {len(visits)}")
        for visit in visits[:5]:
            print(f"- Visit ID: {visit.visit_id}, Subject Key: {visit.subject_key}")

        # Records
        records = client.records.list(study_key=study_key)
        print(f"Records for study '{study_key}': {len(records)}")
        for record in records[:5]:
            print(f"- Record ID: {record.record_id}, Subject Key: {record.subject_key}")

        # Record Revisions
        record_revisions = client.record_revisions.list(study_key=study_key)
        print(f"Record Revisions for study '{study_key}': {len(record_revisions)}")
        for rev in record_revisions[:5]:
            print(f"- Revision ID: {rev.record_revision_id}, Record ID: {rev.record_id}")

        # Codings
        codings = client.codings.list(study_key=study_key)
        print(f"Codings for study '{study_key}': {len(codings)}")
        for coding in codings[:5]:
            print(f"- Coding ID: {coding.coding_id}, Variable: {coding.variable}")

        # Forms
        forms = client.forms.list(study_key=study_key)
        print(f"Forms for study '{study_key}': {len(forms)}")
        for form in forms[:5]:
            print(f"- Form Name: {form.form_name}, ID: {form.form_id}")

        # Intervals
        intervals = client.intervals.list(study_key=study_key)
        print(f"Intervals for study '{study_key}': {len(intervals)}")
        for interval in intervals[:5]:
            print(f"- Interval Name: {interval.interval_name}, ID: {interval.interval_id}")

        # Queries
        queries = client.queries.list(study_key=study_key)
        print(f"Queries for study '{study_key}': {len(queries)}")
        for query in queries[:5]:
            print(f"- Query ID: {query.annotation_id}, Status: {query.status}")

except Exception as e:
    print(f"Error: {e}")
