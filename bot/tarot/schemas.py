from pydantic import BaseModel as _BaseModel, ConfigDict, TypeAdapter


class BaseModel(_BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HistorySchema(BaseModel):
    text: str


class CardSchema(BaseModel):
    id: int
    name: str
    description: str
    image: str | None = None


class DailyCardSchema(BaseModel):
    text: str
    card_id: int


Deck = list[CardSchema]
HistoryAdapter = TypeAdapter(HistorySchema | None)
DeckAdapter = TypeAdapter(Deck)
