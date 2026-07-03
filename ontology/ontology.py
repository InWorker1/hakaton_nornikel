"""Онтология графа знаний R&D — типизированные Python-модели.

Зеркало ``ontology/ontology.md`` и ``ontology/schema.cypher``.
Используется в NLP-пайплайне (п.3 плана), в импортёрах (п.4) и в API (п.5)
для валидации и нормализации данных до записи в Neo4j.

Зависимости: только ``pydantic`` (>= 2.0). Нет I/O, нет внешних
библиотек — модуль должен импортироваться где угодно.

Конвенции:
- Все идентификаторы (``id``, ``slug``) — непустые строки без пробелов.
- ``name_i18n`` — минимум один из ``ru``/``en`` непустой.
- ``confidence`` ∈ [0, 1].
- Если ``numeric_value`` задан, то и ``unit`` тоже.
- Даты — ``datetime.date``, моменты времени — ``datetime.datetime``.

Использование::

    from datetime import date
    from ontology.ontology import Material, UsesMaterial

    m = Material(id="...", slug="cu", name_i18n={"en": "Copper"})
    # Концы связи (from/to) хранятся отдельно — в импортёре, который вызывает
    # MERGE. В самой связи — только метаданные факта.
    rel = UsesMaterial(
        confidence=0.9,
        source_date=date(2024, 1, 1),
        source_ref="doi:10.1234/abc",
        source_excerpt="...медь в качестве анода...",
    )
    assert rel.type.value == "uses_material"
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from enum import Enum

from typing import Any

from uuid import uuid4

from pydantic import (

    BaseModel,

    ConfigDict,

    Field,

    field_validator,

    model_validator,

)

class NodeLabel(str, Enum):

    """Все допустимые лейблы узлов графа."""

    MATERIAL = "Material"

    PROCESS = "Process"

    EQUIPMENT = "Equipment"

    PROPERTY = "Property"

    EXPERIMENT = "Experiment"

    PUBLICATION = "Publication"

    EXPERT = "Expert"

    FACILITY = "Facility"

    CONDITION = "Condition"

class RelationshipType(str, Enum):

    """Все допустимые типы связей графа.

    Двусторонние типы (``contradicts``, ``related_to``) хранятся в одном
    направлении; обратное выражается без ``>`` в Cypher.
    """

    USES_MATERIAL = "uses_material"

    OPERATES_AT_CONDITION = "operates_at_condition"

    PRODUCES_OUTPUT = "produces_output"

    MEASURED_BY = "measured_by"

    CONDUCTED_AT = "conducted_at"

    DESCRIBED_IN = "described_in"

    AUTHORED_BY = "authored_by"

    AFFILIATED_WITH = "affiliated_with"

    VALIDATED_BY = "validated_by"

    CONTRADICTS = "contradicts"

    RELATED_TO = "related_to"

class BaseEntity(BaseModel):

    """Общая часть для КАЖДОГО узла.

    Подклассы добавляют специальные поля. Все подклассы наследуют этот
    набор свойств (см. ``Material``, ``Process`` и т.д.).
    """

    model_config = ConfigDict(

        extra="forbid",

        str_strip_whitespace=True,

        validate_assignment=True,

    )

    id: str = Field(

        default_factory=lambda: str(uuid4()),

        description="Глобальный стабильный идентификатор (UUID).",

    )

    slug: str = Field(

        ...,

        min_length=1,

        max_length=200,

        description="URL-безопасное имя внутри лейбла.",

    )

    name_i18n: dict[str, str] = Field(

        default_factory=dict,

        description="Локализованные имена: {'ru': '...', 'en': '...'}.",

    )

    aliases: list[str] = Field(

        default_factory=list,

        description="Синонимы/аббревиатуры (RU + EN).",

    )

    tags: list[str] = Field(

        default_factory=list,

        description="Теги домена/проекта.",

    )

    created_at: datetime = Field(

        default_factory=lambda: datetime.now(timezone.utc),

        description="Когда узел создан (UTC, timezone-aware).",

    )

    updated_at: datetime = Field(

        default_factory=lambda: datetime.now(timezone.utc),

        description="Когда узел последний раз менялся (UTC, timezone-aware).",

    )

    @field_validator("name_i18n")

    @classmethod

    def _name_i18n_has_at_least_one(cls, v: dict[str, str]) -> dict[str, str]:

        allowed = {"ru", "en"}

        unknown = set(v.keys()) - allowed

        if unknown:

            raise ValueError(

                f"name_i18n: неизвестные ключи {sorted(unknown)}; "

                f"допускаются только {sorted(allowed)}"

            )

        ru = (v.get("ru") or "").strip()

        en = (v.get("en") or "").strip()

        if not (ru or en):

            raise ValueError("name_i18n: нужен хотя бы один непустой 'ru'/'en'.")

        return {k: s for k, s in (("ru", ru), ("en", en)) if s}

    @field_validator("slug")

    @classmethod

    def _slug_safe(cls, v: str) -> str:

        v = v.strip()

        if not v:

            raise ValueError("slug: не может быть пустым.")

        if any(c.isspace() for c in v):

            raise ValueError("slug: не должен содержать пробелов.")

        return v

    @field_validator("aliases", "tags")

    @classmethod

    def _strip_list(cls, v: list[str]) -> list[str]:

        return [s.strip() for s in v if s and s.strip()]

class Material(BaseEntity):

    """Материал / реагент / сырьё / конечный продукт."""

    label: NodeLabel = NodeLabel.MATERIAL

    formula: str | None = Field(default=None, max_length=200)

    cas_number: str | None = Field(default=None, max_length=64)

    family: str | None = Field(default=None, max_length=100)

class Process(BaseEntity):

    """Технологический процесс или операция."""

    label: NodeLabel = NodeLabel.PROCESS

    kind: str | None = Field(

        default=None,

        max_length=64,

        description="Обогащение / пиро / гидро / электро / проч.",

    )

class Equipment(BaseEntity):

    """Конкретный аппарат / установка / модуль."""

    label: NodeLabel = NodeLabel.EQUIPMENT

    model: str | None = Field(default=None, max_length=120)

    vendor: str | None = Field(default=None, max_length=120)

    capacity: str | None = Field(default=None, max_length=120)

class Property(BaseEntity):

    """Измеряемое свойство (физическое/химическое)."""

    label: NodeLabel = NodeLabel.PROPERTY

    kind: str | None = Field(

        default=None,

        max_length=64,

        description="scalar / vector / distribution.",

    )

    unit: str | None = Field(default=None, max_length=32)

class Experiment(BaseEntity):

    """Конкретный эксперимент / опыт / серия испытаний."""

    label: NodeLabel = NodeLabel.EXPERIMENT

    started_at: date | None = None

    ended_at: date | None = None

    batch_id: str | None = Field(default=None, max_length=120)

    sample_count: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")

    def _dates_consistent(self) -> "Experiment":

        if self.started_at and self.ended_at and self.started_at > self.ended_at:

            raise ValueError(

                "Experiment: started_at должен быть <= ended_at."

            )

        return self

class Publication(BaseEntity):

    """Научная статья, отчёт, патент, протокол."""

    label: NodeLabel = NodeLabel.PUBLICATION

    doi: str | None = Field(default=None, max_length=120)

    year: int | None = Field(default=None, ge=1500, le=2100)

    venue: str | None = Field(default=None, max_length=200)

    lang: str | None = Field(default=None, max_length=8)

    url: str | None = Field(default=None, max_length=500)

    @field_validator("doi")

    @classmethod

    def _doi_format(cls, v: str | None) -> str | None:

        if v is None:

            return None

        v = v.strip()

        for prefix in ("https://doi.org/", "http://doi.org/", "doi.org/", "doi:"):

            if v.lower().startswith(prefix):

                v = v[len(prefix):]

                break

        if v and not v.startswith("10."):

            raise ValueError(

                "doi: должен начинаться с '10.' после нормализации "

                "(например, '10.1234/abc')."

            )

        return v or None

class Expert(BaseEntity):

    """Сотрудник / автор / рецензент / внешний эксперт."""

    label: NodeLabel = NodeLabel.EXPERT

    orcid: str | None = Field(default=None, max_length=32)

    email: str | None = Field(default=None, max_length=200)

    position: str | None = Field(default=None, max_length=120)

    current: bool = True

    @field_validator("orcid")

    @classmethod

    def _orcid_format(cls, v: str | None) -> str | None:

        import re as _re

        orcid_re = _re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")

        if v is None:

            return None

        v = v.strip()

        if v and not orcid_re.match(v):

            raise ValueError(

                "orcid: ожидается формат 0000-0000-0000-000X "

                "(19 символов, последний — цифра или X)."

            )

        return v or None

class Facility(BaseEntity):

    """Цех / лаборатория / завод / площадка."""

    label: NodeLabel = NodeLabel.FACILITY

    country: str | None = Field(default=None, max_length=80)

    city: str | None = Field(default=None, max_length=80)

    kind: str | None = Field(default=None, max_length=80)

class Condition(BaseEntity):

    """Условия процесса (T, P, pH, расход и т.п.)."""

    label: NodeLabel = NodeLabel.CONDITION

    value: float | None = None

    unit: str | None = Field(default=None, max_length=32)

    kind: str | None = Field(

        default=None,

        max_length=64,

        description="temperature / pressure / ph / flow / ... .",

    )

    @model_validator(mode="after")

    def _value_unit_consistent(self) -> "Condition":

        if self.value is not None and not (self.unit or "").strip():

            raise ValueError("Condition: если задан value, должен быть задан и unit.")

        if self.value is None and (self.unit or "").strip():

            raise ValueError("Condition: если задан unit, должен быть задан и value.")

        return self

ENTITY_CLASS_BY_LABEL: dict[NodeLabel, type[BaseEntity]] = {

    NodeLabel.MATERIAL: Material,

    NodeLabel.PROCESS: Process,

    NodeLabel.EQUIPMENT: Equipment,

    NodeLabel.PROPERTY: Property,

    NodeLabel.EXPERIMENT: Experiment,

    NodeLabel.PUBLICATION: Publication,

    NodeLabel.EXPERT: Expert,

    NodeLabel.FACILITY: Facility,

    NodeLabel.CONDITION: Condition,

}

class BaseRelationship(BaseModel):

    """Базовый пакет свойств для КАЖДОЙ связи.

    Используется в импортёрах (п.4) — на каждое ребро в Neo4j собираем
    Python-объект, валидируем и только потом пишем в граф.
    """

    model_config = ConfigDict(

        extra="forbid",

        str_strip_whitespace=True,

        validate_assignment=True,

    )

    type: RelationshipType

    confidence: float = Field(..., ge=0.0, le=1.0)

    source_date: date

    source_ref: str = Field(..., min_length=1, max_length=500)

    source_excerpt: str = Field(..., min_length=1, max_length=2000)

    numeric_value: float | None = None

    unit: str | None = Field(default=None, max_length=32)

    valid_from: date | None = None

    valid_to: date | None = None

    note: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")

    def _validate_relationship(self) -> "BaseRelationship":

        if self.numeric_value is not None and not (self.unit or "").strip():

            raise ValueError(

                f"{self.type.value}: если задан numeric_value, должен быть задан и unit."

            )

        if self.numeric_value is None and (self.unit or "").strip():

            raise ValueError(

                f"{self.type.value}: если задан unit, должен быть задан и numeric_value."

            )

        if (

            self.valid_from is not None

            and self.valid_to is not None

            and self.valid_from > self.valid_to

        ):

            raise ValueError(

                f"{self.type.value}: valid_from ({self.valid_from}) "

                f"должен быть <= valid_to ({self.valid_to})."

            )

        return self

class UsesMaterial(BaseRelationship):

    type: RelationshipType = RelationshipType.USES_MATERIAL

class OperatesAtCondition(BaseRelationship):

    type: RelationshipType = RelationshipType.OPERATES_AT_CONDITION

class ProducesOutput(BaseRelationship):

    type: RelationshipType = RelationshipType.PRODUCES_OUTPUT

class MeasuredBy(BaseRelationship):

    type: RelationshipType = RelationshipType.MEASURED_BY

class ConductedAt(BaseRelationship):

    type: RelationshipType = RelationshipType.CONDUCTED_AT

class DescribedIn(BaseRelationship):

    type: RelationshipType = RelationshipType.DESCRIBED_IN

class AuthoredBy(BaseRelationship):

    type: RelationshipType = RelationshipType.AUTHORED_BY

class AffiliatedWith(BaseRelationship):

    type: RelationshipType = RelationshipType.AFFILIATED_WITH

class ValidatedBy(BaseRelationship):

    type: RelationshipType = RelationshipType.VALIDATED_BY

class Contradicts(BaseRelationship):

    type: RelationshipType = RelationshipType.CONTRADICTS

    @model_validator(mode="after")

    def _note_required(self) -> "Contradicts":

        if not (self.note and self.note.strip()):

            raise ValueError(

                "Contradicts: требуется note ('сторона 1 vs сторона 2', причина)."

            )

        return self

class RelatedTo(BaseRelationship):

    type: RelationshipType = RelationshipType.RELATED_TO

RELATIONSHIP_CLASS_BY_TYPE: dict[RelationshipType, type[BaseRelationship]] = {

    RelationshipType.USES_MATERIAL: UsesMaterial,

    RelationshipType.OPERATES_AT_CONDITION: OperatesAtCondition,

    RelationshipType.PRODUCES_OUTPUT: ProducesOutput,

    RelationshipType.MEASURED_BY: MeasuredBy,

    RelationshipType.CONDUCTED_AT: ConductedAt,

    RelationshipType.DESCRIBED_IN: DescribedIn,

    RelationshipType.AUTHORED_BY: AuthoredBy,

    RelationshipType.AFFILIATED_WITH: AffiliatedWith,

    RelationshipType.VALIDATED_BY: ValidatedBy,

    RelationshipType.CONTRADICTS: Contradicts,

    RelationshipType.RELATED_TO: RelatedTo,

}

_OTHER = tuple(

    (lbl, NodeLabel.PUBLICATION)

    for lbl in NodeLabel

    if lbl is not NodeLabel.PUBLICATION

)

_ALL_EXPERIMENT = tuple((lbl, NodeLabel.EXPERIMENT) for lbl in NodeLabel)

_ALL_BIDIR = tuple(

    (a, b)

    for a in NodeLabel

    for b in NodeLabel

    if a is not b

)

ALLOWED_RELATIONSHIPS: dict[

    RelationshipType, tuple[tuple[NodeLabel, NodeLabel], ...]

] = {

    RelationshipType.USES_MATERIAL: (

        (NodeLabel.PROCESS, NodeLabel.MATERIAL),

    ),

    RelationshipType.OPERATES_AT_CONDITION: (

        (NodeLabel.PROCESS, NodeLabel.CONDITION),

        (NodeLabel.EXPERIMENT, NodeLabel.CONDITION),

    ),

    RelationshipType.PRODUCES_OUTPUT: (

        (NodeLabel.PROCESS, NodeLabel.MATERIAL),

        (NodeLabel.PROCESS, NodeLabel.PROPERTY),

    ),

    RelationshipType.MEASURED_BY: (

        (NodeLabel.PROPERTY, NodeLabel.EXPERIMENT),

        (NodeLabel.PROPERTY, NodeLabel.PUBLICATION),

    ),

    RelationshipType.CONDUCTED_AT: (

        (NodeLabel.EXPERIMENT, NodeLabel.FACILITY),

        (NodeLabel.EXPERIMENT, NodeLabel.EQUIPMENT),

    ),

    RelationshipType.DESCRIBED_IN: _OTHER,

    RelationshipType.AUTHORED_BY: (

        (NodeLabel.PUBLICATION, NodeLabel.EXPERT),

    ),

    RelationshipType.AFFILIATED_WITH: (

        (NodeLabel.EXPERT, NodeLabel.FACILITY),

    ),

    RelationshipType.VALIDATED_BY: _ALL_EXPERIMENT,

    RelationshipType.CONTRADICTS: _ALL_BIDIR,

    RelationshipType.RELATED_TO: _ALL_BIDIR,

}

def is_allowed_direction(

    rel_type: RelationshipType,

    src_label: NodeLabel,

    dst_label: NodeLabel,

) -> bool:

    """True, если ``(src_label)-[rel_type]->(dst_label)`` допустимо онтологией."""

    if src_label is dst_label and rel_type not in (

        RelationshipType.CONTRADICTS, RelationshipType.RELATED_TO,

    ):

        return False

    return (src_label, dst_label) in ALLOWED_RELATIONSHIPS.get(rel_type, ())

def make_relationship(rel_type: RelationshipType, **data: Any) -> BaseRelationship:

    """Фабрика: создать объект связи нужного подкласса по ``rel_type``.

    Используется в импортёре, когда тип приходит из БД/JSON.
    ``type`` в ``data`` (если передано) будет проигнорирован.
    """

    cls = RELATIONSHIP_CLASS_BY_TYPE[rel_type]

    data = {k: v for k, v in data.items() if k != "type"}

    return cls(type=rel_type, **data)

def node_to_props_dict(node: BaseEntity) -> dict[str, Any]:

    """Сериализовать узел в dict для MERGE/CREATE в Neo4j.

    Разворачивает ``name_i18n`` в отдельные поля ``name_i18n_ru``/
    ``name_i18n_en`` — под них построены индексы в ``schema.cypher``.
    """

    d = node.model_dump(mode="python")

    name = d.pop("name_i18n", {})

    d["name_i18n_ru"] = name.get("ru")

    d["name_i18n_en"] = name.get("en")

    return d

def rel_to_props_dict(rel: BaseRelationship) -> dict[str, Any]:

    """Сериализовать связь в dict для ``SET r = $props`` в Neo4j."""

    return rel.model_dump(mode="python", exclude={"type"})

__all__ = [

    "NodeLabel",

    "RelationshipType",

    "BaseEntity",

    "Material",

    "Process",

    "Equipment",

    "Property",

    "Experiment",

    "Publication",

    "Expert",

    "Facility",

    "Condition",

    "ENTITY_CLASS_BY_LABEL",

    "BaseRelationship",

    "UsesMaterial",

    "OperatesAtCondition",

    "ProducesOutput",

    "MeasuredBy",

    "ConductedAt",

    "DescribedIn",

    "AuthoredBy",

    "AffiliatedWith",

    "ValidatedBy",

    "Contradicts",

    "RelatedTo",

    "RELATIONSHIP_CLASS_BY_TYPE",

    "ALLOWED_RELATIONSHIPS",

    "make_relationship",

    "is_allowed_direction",

    "node_to_props_dict",

    "rel_to_props_dict",

]

