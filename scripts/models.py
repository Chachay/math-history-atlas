from typing import Literal
from pydantic import BaseModel, Field, model_validator

EntityType = Literal['Person','Concept','Result','Work','Event','Problem']
Perspective = Literal['historical','later_interpretation','modern_abstraction']
Status = Literal['candidate','source_checked','historically_reviewed','accepted','published']
Certainty = Literal['high','medium','low']

class Period(BaseModel):
    from_: int | None = Field(None, alias='from')
    to: int | None = None
    model_config = {'populate_by_name': True}
    @model_validator(mode='after')
    def valid(self):
        if self.from_ is not None and self.to is not None and self.from_ > self.to:
            raise ValueError('period.from must be <= period.to')
        return self

class Entity(BaseModel):
    id: str; type: EntityType; name: str
    start_year: int | None = None; end_year: int | None = None
    fields: list[str] = []

class Question(BaseModel):
    id: str; question: str; period: Period; fields: list[str] = []

class Assertion(BaseModel):
    id: str; subject: str; predicate: str; object: str; period: Period
    perspective: Perspective; certainty: Certainty; sources: list[str]; status: Status

class FieldModel(BaseModel):
    id: str; name: str; parents: list[str] = []

class ConceptState(BaseModel):
    id: str; concept_id: str; period: Period; label: str

class StoryStep(BaseModel):
    id: str; ref: str; role: str
    narrative: str | None = None
    assertion_refs: list[str] = []
    perspective: Perspective | None = None

class StoryLink(BaseModel):
    from_: str = Field(alias='from'); to: str
    type: Literal['continues','branches','converges','alternative']
    model_config = {'populate_by_name': True}

class Story(BaseModel):
    id: str; title: str; description: str
    question_phases: list[str] = []; steps: list[StoryStep]; links: list[StoryLink]; fields: list[str] = []
