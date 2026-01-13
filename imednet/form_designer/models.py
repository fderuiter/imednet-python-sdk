from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel


class Choice(BaseModel):
    """A choice for radio or dropdown fields."""

    text: str
    code: str
    new_choice_id: int


class FieldProps(BaseModel):
    """Properties for a field or entity."""

    # Common
    type: Literal[
        "sep",
        "table",
        "label",
        "text",
        "memo",
        "number",
        "radio",
        "dropdown",
        "checkbox",
        "datetime",
        "precisiondate",
        "upload",
        "ext_question",
    ]
    label: Optional[str] = None

    # IDs
    new_fld_id: Optional[int] = None
    fld_id: Optional[int] = None

    # Logic / Requirements
    question_name: Optional[str] = None
    bl_req: Optional[Literal["optional", "hard", "autoquery"]] = "optional"
    sdv_req: Optional[Literal["yes", "no"]] = "no"
    is_blinded: Optional[int] = 0
    mv: Optional[int] = 0
    nodelete: Optional[int] = 0
    bl_related: Optional[str] = "View"

    # Text / Memo
    columns: Optional[int] = None
    rows: Optional[int] = None
    length: Optional[int] = None

    # Number
    real: Optional[Literal[0, 1]] = None  # 0=Int, 1=Float
    suffix: Optional[str] = None

    # Radio / Dropdown
    radio: Optional[Literal[1, 2]] = None  # 1=Horiz, 2=Vert
    choices: Optional[List[Choice]] = None

    # Date
    date_ctrl: Optional[Literal[0, 1]] = None
    time_ctrl: Optional[Literal[0, 1]] = None
    bl_future_date: Optional[Literal[0, 1]] = None
    allow_no_day: Optional[Literal[0, 1]] = None
    allow_no_month: Optional[Literal[0, 1]] = None
    allow_no_year: Optional[Literal[0, 1]] = None

    # Precision Date
    precision_time: Optional[Literal[0, 1]] = None
    precision_secs: Optional[Literal[0, 1]] = None

    # Upload
    mfs: Optional[Literal[0, 1]] = None  # Multi-file select

    # External
    ext_source: Optional[str] = None
    interval_source: Optional[str] = None

    # Separator
    septype: Optional[int] = None


class Entity(BaseModel):
    """A generic entity in the form (Separator, Table, Label, Control)."""

    props: FieldProps
    id: str  # DOM ID (e.g., lfdiv_...)
    rows: Optional[List[Row]] = None  # Only for type='table'


class Col(BaseModel):
    """A column in a table row."""

    entities: List[Entity]


class Row(BaseModel):
    """A row in a table."""

    cols: List[Col]


class Page(BaseModel):
    """A page in the form definition."""

    entities: List[Entity]


class Layout(BaseModel):
    """The root layout object."""

    pages: List[Page]


# Handle circular references
Entity.model_rebuild()
Col.model_rebuild()
Row.model_rebuild()
Page.model_rebuild()
Layout.model_rebuild()
