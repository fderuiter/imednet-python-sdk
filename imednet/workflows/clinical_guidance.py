"""Provides workflows for clinical guidance and compliance."""

from typing import TYPE_CHECKING, Any, Dict, List, Set

from thefuzz import process

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class ClinicalGuidanceWorkflow:
    """
    Provides methods for common clinical guidance tasks based on FDA recommendations.

    Args:
        sdk: An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK"):
        self._sdk = sdk

    @staticmethod
    def get_user_roles_and_responsibilities() -> Dict[str, str]:
        """
        Returns a dictionary of standard user roles and their responsibilities.

        Based on: https://oct-clinicaltrials.com/resources/articles/edc-system-user-roles

        Returns:
            A dictionary where keys are role names and values are their descriptions.
        """
        return {
            "Principal Investigator/Investigator": "Data entry and approval from the study site’s side",
            "Data Coordinator/Site Coordinator": "Data entry from the study site’s side",
            "Monitor/CRA": "Data clarification and verification",
            "Project Manager": "Data overview and formation of requests on supplies of IP",
            "Sponsor/Study Coordinator": "Data overview",
            "Data Manager": "Data cleaning",
            "Data Management Assistant": "Data cleaning",
            "Database Administrator": "Administration of project-specific database",
            "Logistician": "Work with supplies of IP on the storage side",
            "Pharmacist": "Receipt of IP supplies from the study site’s side",
        }

    @staticmethod
    def get_delegation_of_authority_requirements() -> List[str]:
        """
        Returns a list of requirements for delegating authority in clinical trials.

        Based on: https://qualitycompliance.research.utah.edu/sop-library/uu-sop-05.php

        Returns:
            A list of strings, each describing a requirement.
        """
        return [
            "The PI is responsible for providing adequate training and supervision to all delegates.",
            "Delegation of study-related tasks must be appropriate to the individual's education, training, and experience.",
            "A list of appropriately qualified persons with delegated trial-related duties must be maintained.",
            "Tasks of a clinical or medical nature must be delegated to staff with appropriate education, experience, and licensing.",
            "The Delegation of Authority log should be completed at study initiation and kept up-to-date.",
            "Corrections to the delegation of authority record must follow 'good clinical practice' procedures.",
            "The delegation of authority record may be maintained electronically in a 21 CFR Part 11 compliant system.",
        ]

    @staticmethod
    def get_electronic_source_data_recommendations() -> List[str]:
        """
        Returns a list of FDA recommendations for electronic source data.

        Based on: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/electronic-source-data-clinical-investigations

        Returns:
            A list of strings, each describing a recommendation.
        """
        return [
            "Identification and specification of authorized source data originators.",
            "Creation of data element identifiers to facilitate examination of the audit trail.",
            "Define methods for capturing source data into the eCRF (manual or electronic).",
            "Clarify clinical investigator responsibilities for reviewing and retaining electronic data.",
            "Ensure proper use and description of computerized systems in clinical investigations.",
        ]

    def get_users_with_role_info(
        self, study_key: str, similarity_threshold: int = 80, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Fetches all users for a study and annotates them with information
        about their roles based on standard guidance, using fuzzy matching.

        Args:
            study_key: The key identifying the study.
            similarity_threshold: The minimum similarity score (0-100) to consider a role a match.
            **kwargs: Additional keyword arguments passed directly to `sdk.users.list`.

        Returns:
            A list of dictionaries, where each dictionary represents a user
            and includes their roles annotated with matching standard role info.
        """
        users = self._sdk.users.list(study_key, **kwargs)
        standard_roles = self.get_user_roles_and_responsibilities()

        user_list = []
        for user in users:
            user_dict = user.model_dump(by_alias=True)
            annotated_roles = []
            for role in user_dict.get("roles", []):
                best_match, score = process.extractOne(role.get("name", ""), standard_roles.keys())

                role["standard_role_match"] = None
                if score >= similarity_threshold:
                    role["standard_role_match"] = {
                        "matched_role": best_match,
                        "similarity_score": score,
                        "description": standard_roles[best_match],
                    }
                annotated_roles.append(role)
            user_dict["roles"] = annotated_roles
            user_list.append(user_dict)

        return user_list

    def identify_users_needing_delegation_log(
        self, study_key: str, similarity_threshold: int = 80, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Fetches all users for a study and identifies those who would likely
        need to be on a Delegation of Authority log based on their roles,
        using fuzzy matching.

        Args:
            study_key: The key identifying the study.
            similarity_threshold: The minimum similarity score (0-100) to consider a role a match.
            **kwargs: Additional keyword arguments passed directly to `sdk.users.list`.

        Returns:
            A list of user dictionaries for users who should be on the log.
        """
        users = self._sdk.users.list(study_key, **kwargs)
        roles_requiring_log: Set[str] = {
            "Principal Investigator/Investigator",
            "Data Coordinator/Site Coordinator",
            "Monitor/CRA",
            "Sub-Investigator",
            "Clinical Research Coordinator",
        }

        users_to_log = []
        for user in users:
            found_match = False
            for role in user.roles:
                best_match, score = process.extractOne(role.name, roles_requiring_log)
                if score >= similarity_threshold:
                    users_to_log.append(user.model_dump(by_alias=True))
                    found_match = True
                    break
            if found_match:
                continue
        return users_to_log
