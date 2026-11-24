from pydantic import BaseModel, ConfigDict


class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    order_index: int
    completed: bool = False


class CompleteOut(BaseModel):
    message: str
    completed_lessons: int
    hp: int
    level: int