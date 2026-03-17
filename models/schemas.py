from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str


class StandardResponse(BaseModel):
    status: Literal["success", "error"]
    data: Optional[Any] = None
    message: Optional[str] = None


class DrugProduct(BaseModel):
    product_ndc: str = Field(
        ...,
        description=(
            "The labeler manufacturer code and product code segments of the NDC "
            "number, separated by a hyphen."
        ),
    )
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    brand_name_base: Optional[str] = None
    labeler_name: Optional[str] = None
    product_type: Optional[str] = None
    marketing_category: Optional[str] = None
    dosage_form: Optional[str] = None
    route: Optional[str] = None
    finished: Optional[bool] = None
    application_number: Optional[str] = None
    marketing_start_date: Optional[str] = None
    listing_expiration_date: Optional[str] = None


class DrugPackage(BaseModel):
    package_ndc: str = Field(
        ...,
        description=(
            "NDC that identifies the labeler, product, and trade package size."
        ),
    )
    description: Optional[str] = None
    marketing_start_date: Optional[str] = None
    sample: Optional[bool] = None


class Substance(BaseModel):
    unii: str = Field(
        ...,
        description=(
            "Unique Ingredient Identifier (UNII), a unique alphanumeric "
            "identifier for a substance."
        ),
    )
    name: str
    strength: Optional[str] = None


class IngredientText(BaseModel):
    text: str
    type: Literal["inactive"] = "inactive"


class DrugLabel(BaseModel):
    set_id: str
    spl_id: str = Field(
        ...,
        pattern=(
            r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-"
            r"[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
        ),
    )
    effective_time: Optional[str] = None
    version: Optional[int] = None
    purpose: Optional[str] = None
    warnings: Optional[str] = None
    when_using: Optional[str] = None
    stop_use: Optional[str] = None
    pregnancy_or_breast_feeding: Optional[str] = None
    keep_out_of_reach_of_children: Optional[str] = None
    boxed_warning: Optional[str] = None
    description: Optional[str] = None
    clinical_pharmacology: Optional[str] = None
    indications_and_usage: Optional[str] = None
    contraindications: Optional[str] = None
    precautions: Optional[str] = None
    information_for_patients: Optional[str] = None
    drug_interactions: Optional[str] = None
    drug_and_or_laboratory_test_interactions: Optional[str] = None
    carcinogenesis_and_mutagenesis_and_impairment_of_fertility: Optional[str] = None
    pregnancy: Optional[str] = None
    nursing_mothers: Optional[str] = None
    pediatric_use: Optional[str] = None
    geriatric_use: Optional[str] = None
    adverse_reactions: Optional[str] = None
    drug_abuse_and_dependence: Optional[str] = None
    overdosage: Optional[str] = None
    other_safety_information: Optional[str] = None
    dosage_and_administration: Optional[str] = None
    how_supplied: Optional[str] = None
    spl_medguide: Optional[str] = None
    package_label_principal_display_panel: Optional[str] = None


class RxNormConcept(BaseModel):
    rxcui: str = Field(..., pattern=r"^[0-9]{6}$")


class PharmClass(BaseModel):
    name: str
    type: Literal["MoA", "EPC", "OTHER"]


class MedicinePlus(BaseModel):
    name: str = Field(..., description="Name of the medical condition or disease.")
    definition: Optional[str] = Field(
        None, description="Short definition or summary of the condition."
    )
    url: Optional[str] = Field(None, description="Source URL (e.g. MedlinePlus page).")


class DrugProductRelations(BaseModel):
    has_package: List[DrugPackage] = Field(default_factory=list)
    has_active_ingredient: List[Substance] = Field(default_factory=list)
    has_inactive_ingredient_text: List[IngredientText] = Field(default_factory=list)
    has_rxnorm: List[RxNormConcept] = Field(default_factory=list)
    has_pharm_class: List[PharmClass] = Field(default_factory=list)
    has_label: List[DrugLabel] = Field(default_factory=list)
