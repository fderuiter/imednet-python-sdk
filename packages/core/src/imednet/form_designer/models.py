"""Pydantic models for iMednet Form Designer layouts."""

from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel, Field


class Choice(BaseModel):
    """A choice for radio or dropdown fields."""

    text: str
    choice_id: int | str
    code: str


class BaseFieldProps(BaseModel):
    """Shared properties for all data capture fields."""

    fld_id: int | str | None = None
    question_id: int | str | None = None
    question_name: str | None = None
    label: str | None = None
    sas_label: str | None = None
    sequence: str | None = None
    page_no: str | None = None

    # Validation & Logic
    sdv_req: Literal["yes", "no"] | None = None
    bl_req: Literal["optional", "hard", "soft", "autoquery", "confirm"] | None = None
    bl_req_id: int | str | None = None

    # Dates & Logic
    bl_future_date: int | None = None
    bl_future_date_id: int | str | None = None
    bl_inherit_date: int | None = None
    bl_inherit_date_id: int | str | None = None

    # View Permissions
    bl_related: str | list[Any] | None = None
    is_blinded: int | None = None
    blinded_roles: list[str] | None = None

    # Internal Flags
    mv: int | None = None
    nodelete: int | None = None
    catalog: str | None = None
    comments: str | None = None

    # New Field ID (often used during creation before DB assignment)
    new_fld_id: int | str | None = None


class TableProps(BaseModel):
    """Properties for a table layout component."""

    type: Literal["table"]
    columns: int


class LabelProps(BaseModel):
    """Properties for a label component."""

    type: Literal["label"]
    label: str
    label_id: str | None = None
    label_name: str | None = None
    fld_id: int | str | None = None
    new_fld_id: int | str | None = None


class SeparatorProps(BaseModel):
    """Properties for a separator/section header component."""

    type: Literal["sep"]
    septype: int
    label: str | None = None


class ExtQuestionProps(BaseModel):
    """Properties for an external question component."""

    type: Literal["ext_question"]
    ext_source: Literal["interval", "form"]
    label: str
    interval_source: str | None = None
    form: int | None = None
    field: int | None = None
    source: int | None = None


class TextFieldProps(BaseFieldProps):
    """Properties for a text input field."""

    type: Literal["text"]
    length: str | int
    columns: str | int | None = None


class NumberFieldProps(BaseFieldProps):
    """Properties for a number input field."""

    type: Literal["number"]
    length: str | int
    columns: str | int | None = None
    real: int | None = None  # 0=Int, 1=Float
    suffix: str | None = None


class MemoFieldProps(BaseFieldProps):
    """Properties for a memo/multiline text field."""

    type: Literal["memo"]
    length: str | int
    columns: str | int
    rows: str | int


class RadioFieldProps(BaseFieldProps):
    """Properties for a radio button field."""

    type: Literal["radio"]
    choices: list[Choice]
    radio: int | None = None  # Layout: 1=Vertical, 2=Horizontal


class DropdownFieldProps(BaseFieldProps):
    """Properties for a dropdown/select field."""

    type: Literal["dropdown"]
    choices: list[Choice]
    lab_condition: str | None = None
    lab_default_form: str | None = None
    lab_default_form_type: str | None = None
    lab_default_question: str | None = None
    lab_normal: str | None = None


class CheckboxFieldProps(BaseFieldProps):
    """Properties for a checkbox field."""

    type: Literal["checkbox"]
    choices: list[Choice] | None = None


class FileUploadProps(BaseFieldProps):
    """Properties for a file upload field."""

    type: Literal["upload"]
    mfs: int  # Multi-File Support
    max_files: str | int


class DateTimeFieldProps(BaseFieldProps):
    """Properties for a date/time input field."""

    type: Literal["datetime"]
    time_ctrl: int | None = None  # 1 = Show Time
    date_ctrl: int | None = None  # 1 = Show Date
    use_seconds: int | None = None  # 1 = Show Seconds
    record_comp_date: int | None = None
    record_key_date: int | None = None

    # Legacy support from current builder logic
    allow_no_day: int | None = None
    allow_no_month: int | None = None
    allow_no_year: int | None = None


class PrecisionDateFieldProps(BaseFieldProps):
    """Properties for a precision date input field (supporting partial dates)."""

    type: Literal["precisiondate"]

    # Components Enabled
    precision_secs: int | None = None
    precision_time: int | None = None

    # Partial Date Logic (1=Yes, 0=No)
    allow_no_day: int | None = None
    allow_no_month: int | None = None
    allow_no_year: int | None = None
    allow_no_time: int | None = None

    # Imputation Logic
    impute_time: str | None = None
    impute_day: str | None = None
    impute_month: int | None = None
    impute_year: int | None = None

    # Display Logic
    display_text_time: str | None = None
    display_text_day: str | None = None
    display_text_month: str | None = None
    display_text_year: str | None = None

    # Key Dates
    record_key_date: int | None = None
    record_comp_date: int | None = None


EntityProps = Union[  # noqa: UP007
    TableProps,
    LabelProps,
    SeparatorProps,
    ExtQuestionProps,
    TextFieldProps,
    NumberFieldProps,
    RadioFieldProps,
    DropdownFieldProps,
    CheckboxFieldProps,
    DateTimeFieldProps,
    PrecisionDateFieldProps,
    MemoFieldProps,
    FileUploadProps,
]


class Entity(BaseModel):
    """The 'Component' in the Composite Pattern."""

    id: str
    props: EntityProps = Field(discriminator="type")
    rows: list[Row] | None = None


class Col(BaseModel):
    """A column in a layout table row."""

    entities: list[Entity] | None = None


class Row(BaseModel):
    """A row in a layout table."""

    cols: list[Col]


class Page(BaseModel):
    """Represents a single page within the electronic Case Report Form (CRF)."""

    entities: list[Entity]


class ProtocolDeviationFormPayload(BaseModel):
    """Root object representing the entire form definition payload."""

    pages: list[Page]


# Alias for compatibility with builder
Layout = ProtocolDeviationFormPayload

# Handle circular references
Entity.model_rebuild()
Col.model_rebuild()
Row.model_rebuild()
Page.model_rebuild()
ProtocolDeviationFormPayload.model_rebuild()
