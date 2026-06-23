"""Pydantic models for iMednet Form Designer layouts."""

from __future__ import annotations

from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class Choice(BaseModel):
    """A choice for radio or dropdown fields."""

    text: str
    choice_id: Union[int, str]
    code: str


class BaseFieldProps(BaseModel):
    """Shared properties for all data capture fields."""

    fld_id: Optional[Union[int, str]] = None
    question_id: Optional[Union[int, str]] = None
    question_name: Optional[str] = None
    label: Optional[str] = None
    sas_label: Optional[str] = None
    sequence: Optional[str] = None
    page_no: Optional[str] = None

    # Validation & Logic
    sdv_req: Optional[Literal["yes", "no"]] = None
    bl_req: Optional[Literal["optional", "hard", "soft", "autoquery", "confirm"]] = None
    bl_req_id: Optional[Union[int, str]] = None

    # Dates & Logic
    bl_future_date: Optional[int] = None
    bl_future_date_id: Optional[Union[int, str]] = None
    bl_inherit_date: Optional[int] = None
    bl_inherit_date_id: Optional[Union[int, str]] = None

    # View Permissions
    bl_related: Optional[Union[str, List[Any]]] = None
    is_blinded: Optional[int] = None
    blinded_roles: Optional[List[str]] = None

    # Internal Flags
    mv: Optional[int] = None
    nodelete: Optional[int] = None
    catalog: Optional[str] = None
    comments: Optional[str] = None

    # New Field ID (often used during creation before DB assignment)
    new_fld_id: Optional[Union[int, str]] = None


class TableProps(BaseModel):
    """Properties for a table layout component."""

    type: Literal["table"]
    columns: int


class LabelProps(BaseModel):
    """Properties for a label component."""

    type: Literal["label"]
    label: str
    label_id: Optional[str] = None
    label_name: Optional[str] = None
    fld_id: Optional[Union[int, str]] = None
    new_fld_id: Optional[Union[int, str]] = None


class SeparatorProps(BaseModel):
    """Properties for a separator/section header component."""

    type: Literal["sep"]
    septype: int
    label: Optional[str] = None


class ExtQuestionProps(BaseModel):
    """Properties for an external question component."""

    type: Literal["ext_question"]
    ext_source: Literal["interval", "form"]
    label: str
    interval_source: Optional[str] = None
    form: Optional[int] = None
    field: Optional[int] = None
    source: Optional[int] = None


class TextFieldProps(BaseFieldProps):
    """Properties for a text input field."""

    type: Literal["text"]
    length: Union[str, int]
    columns: Optional[Union[str, int]] = None


class NumberFieldProps(BaseFieldProps):
    """Properties for a number input field."""

    type: Literal["number"]
    length: Union[str, int]
    columns: Optional[Union[str, int]] = None
    real: Optional[int] = None  # 0=Int, 1=Float
    suffix: Optional[str] = None


class MemoFieldProps(BaseFieldProps):
    """Properties for a memo/multiline text field."""

    type: Literal["memo"]
    length: Union[str, int]
    columns: Union[str, int]
    rows: Union[str, int]


class RadioFieldProps(BaseFieldProps):
    """Properties for a radio button field."""

    type: Literal["radio"]
    choices: List[Choice]
    radio: Optional[int] = None  # Layout: 1=Vertical, 2=Horizontal


class DropdownFieldProps(BaseFieldProps):
    """Properties for a dropdown/select field."""

    type: Literal["dropdown"]
    choices: List[Choice]
    lab_condition: Optional[str] = None
    lab_default_form: Optional[str] = None
    lab_default_form_type: Optional[str] = None
    lab_default_question: Optional[str] = None
    lab_normal: Optional[str] = None


class CheckboxFieldProps(BaseFieldProps):
    """Properties for a checkbox field."""

    type: Literal["checkbox"]
    choices: Optional[List[Choice]] = None


class FileUploadProps(BaseFieldProps):
    """Properties for a file upload field."""

    type: Literal["upload"]
    mfs: int  # Multi-File Support
    max_files: Union[str, int]


class DateTimeFieldProps(BaseFieldProps):
    """Properties for a date/time input field."""

    type: Literal["datetime"]
    time_ctrl: Optional[int] = None  # 1 = Show Time
    date_ctrl: Optional[int] = None  # 1 = Show Date
    use_seconds: Optional[int] = None  # 1 = Show Seconds
    record_comp_date: Optional[int] = None
    record_key_date: Optional[int] = None

    # Legacy support from current builder logic
    allow_no_day: Optional[int] = None
    allow_no_month: Optional[int] = None
    allow_no_year: Optional[int] = None


class PrecisionDateFieldProps(BaseFieldProps):
    """Properties for a precision date input field (supporting partial dates)."""

    type: Literal["precisiondate"]

    # Components Enabled
    precision_secs: Optional[int] = None
    precision_time: Optional[int] = None

    # Partial Date Logic (1=Yes, 0=No)
    allow_no_day: Optional[int] = None
    allow_no_month: Optional[int] = None
    allow_no_year: Optional[int] = None
    allow_no_time: Optional[int] = None

    # Imputation Logic
    impute_time: Optional[str] = None
    impute_day: Optional[str] = None
    impute_month: Optional[int] = None
    impute_year: Optional[int] = None

    # Display Logic
    display_text_time: Optional[str] = None
    display_text_day: Optional[str] = None
    display_text_month: Optional[str] = None
    display_text_year: Optional[str] = None

    # Key Dates
    record_key_date: Optional[int] = None
    record_comp_date: Optional[int] = None


EntityProps = Union[
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
    rows: Optional[List[Row]] = None


class Col(BaseModel):
    """A column in a layout table row."""

    entities: Optional[List[Entity]] = None


class Row(BaseModel):
    """A row in a layout table."""

    cols: List[Col]


class Page(BaseModel):
    """Represents a single page within the electronic Case Report Form (CRF)."""

    entities: List[Entity]


class ProtocolDeviationFormPayload(BaseModel):
    """Root object representing the entire form definition payload."""

    pages: List[Page]


# Alias for compatibility with builder
Layout = ProtocolDeviationFormPayload

# Handle circular references
Entity.model_rebuild()
Col.model_rebuild()
Row.model_rebuild()
Page.model_rebuild()
ProtocolDeviationFormPayload.model_rebuild()
