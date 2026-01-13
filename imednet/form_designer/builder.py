import random
import string
from typing import List, Literal, Optional

from .models import (
    Choice,
    Col,
    Entity,
    FieldProps,
    Layout,
    Page,
    Row,
)


class FormBuilder:
    """
    Builder class to construct iMedNet Form Designer payloads programmatically.

    Manages ID generation and hierarchical structure.
    """

    def __init__(self) -> None:
        self.pages: List[Page] = []
        self._ensure_page()
        # Track generated IDs to avoid collisions (though random large int makes it rare)
        self._generated_ids: set[int] = set()

    def _ensure_page(self) -> None:
        if not self.pages:
            self.pages.append(Page(entities=[]))

    @property
    def current_page(self) -> Page:
        self._ensure_page()
        return self.pages[-1]

    def _generate_new_fld_id(self) -> int:
        """Generate a random unique integer for new fields."""
        while True:
            new_id = random.randint(10000, 99999)
            if new_id not in self._generated_ids:
                self._generated_ids.add(new_id)
                return new_id

    def _generate_dom_id(self) -> str:
        """Generate a random DOM ID (e.g., lfdiv_38492)."""
        suffix = "".join(random.choices(string.digits, k=5))
        return f"lfdiv_{suffix}"

    def _create_entity(self, props: FieldProps, rows: Optional[List[Row]] = None) -> Entity:
        return Entity(props=props, id=self._generate_dom_id(), rows=rows)

    def add_page(self) -> None:
        """Add a new page to the form."""
        self.pages.append(Page(entities=[]))

    def add_section_header(self, label: str) -> None:
        """Add a separator/section header."""
        props = FieldProps(type="sep", label=label, septype=1)
        entity = self._create_entity(props)
        self.current_page.entities.append(entity)
        # After a separator, we typically need a table container for fields
        # But in the schema, tables are siblings of separators.
        # We start a new table automatically when a field is added if one doesn't exist?
        # The schema shows Separators and Tables as siblings in `page.entities`.
        # For simplicity, `add_field` will append to the *last* table if available,
        # or create a new one.

    def _get_or_create_table(self) -> Entity:
        """Get the last entity if it's a table, or create a new one."""
        if self.current_page.entities:
            last = self.current_page.entities[-1]
            if last.props.type == "table":
                return last

        # Create new table
        table_props = FieldProps(type="table", columns=2)  # Standard 2-col
        table = self._create_entity(table_props, rows=[])
        self.current_page.entities.append(table)
        return table

    def add_group_header(self, label: str) -> None:
        """Add a group header (Label-only row)."""
        table = self._get_or_create_table()
        if table.rows is None:
            table.rows = []

        # Group header is Row -> Col 1 (Label) -> Col 2 (Empty)
        # Col 1
        label_props = FieldProps(type="label", label=label)
        # Usually group headers don't have IDs linked to controls
        col1 = Col(entities=[self._create_entity(label_props)])

        # Col 2
        col2 = Col(entities=[])

        row = Row(cols=[col1, col2])
        table.rows.append(row)

    def add_field(
        self,
        type: Literal[
            "text", "number", "radio", "dropdown", "datetime", "upload", "checkbox", "memo"
        ],
        label: str,
        question_name: str,
        required: bool = False,
        # Type specific args
        choices: Optional[List[tuple[str, str]]] = None,  # (text, code)
        max_length: Optional[int] = None,
        is_float: bool = False,
    ) -> None:
        """
        Add a standard field (Label + Control).

        Args:
            type: Field type.
            label: Display label (HTML allowed).
            question_name: Variable OID.
            required: If True, sets bl_req='hard'.
            choices: List of (text, code) for radios/dropdowns.
            max_length: Max chars (text/memo) or digits (number).
            is_float: For numbers, allow decimals.
        """
        table = self._get_or_create_table()
        if table.rows is None:
            table.rows = []

        # Generate shared ID
        shared_id = self._generate_new_fld_id()
        bl_req = "hard" if required else "optional"

        # 1. Label Entity (Col 1)
        label_props = FieldProps(type="label", label=label, new_fld_id=shared_id)
        col1 = Col(entities=[self._create_entity(label_props)])

        # 2. Control Entity (Col 2)
        ctrl_props = FieldProps(
            type=type, question_name=question_name, new_fld_id=shared_id, bl_req=bl_req
        )

        # Apply type-specifics
        if type == "text":
            ctrl_props.columns = 30
            ctrl_props.length = max_length or 100
        elif type == "memo":
            ctrl_props.columns = 40
            ctrl_props.rows = 6
            ctrl_props.length = max_length or 500
        elif type == "number":
            ctrl_props.columns = 10
            ctrl_props.length = max_length or 5
            ctrl_props.real = 1 if is_float else 0
        elif type in ("radio", "dropdown") and choices:
            ctrl_props.choices = [
                Choice(text=t, code=c, new_choice_id=self._generate_new_fld_id())
                for t, c in choices
            ]
            if type == "radio":
                ctrl_props.radio = 1  # Horizontal default
        elif type == "datetime":
            ctrl_props.date_ctrl = 1
            ctrl_props.time_ctrl = 0
            ctrl_props.allow_no_day = 0
            ctrl_props.allow_no_month = 0
            ctrl_props.allow_no_year = 0
        elif type == "upload":
            ctrl_props.mfs = 1

        col2 = Col(entities=[self._create_entity(ctrl_props)])

        row = Row(cols=[col1, col2])
        table.rows.append(row)

    def build(self) -> Layout:
        """Return the final layout."""
        return Layout(pages=self.pages)
