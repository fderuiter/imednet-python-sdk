import unittest
from unittest.mock import MagicMock

from imednet.api.models.users import Role, User
from imednet.workflows.clinical_guidance import ClinicalGuidanceWorkflow


class TestClinicalGuidanceWorkflow(unittest.TestCase):
    def setUp(self):
        self.sdk = MagicMock()
        self.workflow = ClinicalGuidanceWorkflow(self.sdk)

    def test_get_user_roles_and_responsibilities(self):
        roles = self.workflow.get_user_roles_and_responsibilities()
        self.assertIsInstance(roles, dict)
        self.assertGreater(len(roles), 0)
        self.assertIn("Monitor/CRA", roles)

    def test_get_delegation_of_authority_requirements(self):
        requirements = self.workflow.get_delegation_of_authority_requirements()
        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)
        self.assertTrue(any("Delegation of Authority log" in req for req in requirements))

    def test_get_electronic_source_data_recommendations(self):
        recommendations = self.workflow.get_electronic_source_data_recommendations()
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("audit trail" in rec for rec in recommendations))

    def test_get_users_with_role_info_fuzzy_matching(self):
        mock_users = [
            User(
                user_id="user1",
                login="testuser1",
                roles=[Role(name="CRA"), Role(name="A completely random role")],
            ),
            User(
                user_id="user2",
                login="testuser2",
                roles=[Role(name="Data Manger")],  # Typo
            ),
        ]
        self.sdk.users.list.return_value = mock_users

        users_with_info = self.workflow.get_users_with_role_info("test_study")

        self.sdk.users.list.assert_called_once_with("test_study")
        self.assertEqual(len(users_with_info), 2)

        user1_roles = users_with_info[0]["roles"]
        self.assertEqual(len(user1_roles), 2)
        self.assertIsNotNone(user1_roles[0]["standard_role_match"])
        self.assertEqual(user1_roles[0]["standard_role_match"]["matched_role"], "Monitor/CRA")
        self.assertIsNone(user1_roles[1]["standard_role_match"])

        user2_roles = users_with_info[1]["roles"]
        self.assertEqual(len(user2_roles), 1)
        self.assertIsNotNone(user2_roles[0]["standard_role_match"])
        self.assertEqual(user2_roles[0]["standard_role_match"]["matched_role"], "Data Manager")

    def test_identify_users_needing_delegation_log_fuzzy_matching(self):
        mock_users = [
            User(
                user_id="user1",
                login="testuser1",
                roles=[Role(name="Clinical Research Crdinator")],  # Typo
            ),
            User(
                user_id="user2",
                login="testuser2",
                roles=[Role(name="Software Engineer")],
            ),
            User(
                user_id="user3",
                login="testuser3",
                roles=[Role(name="SubInvestigator"), Role(name="Pharmacist")],  # Close match
            ),
        ]
        self.sdk.users.list.return_value = mock_users

        users_to_log = self.workflow.identify_users_needing_delegation_log("test_study")

        self.sdk.users.list.assert_called_once_with("test_study")
        self.assertEqual(len(users_to_log), 2)

        user_ids_to_log = {user["userId"] for user in users_to_log}
        self.assertIn("user1", user_ids_to_log)
        self.assertIn("user3", user_ids_to_log)
        self.assertNotIn("user2", user_ids_to_log)


if __name__ == "__main__":
    unittest.main()
