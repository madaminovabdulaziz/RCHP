from pydantic import BaseModel


class MenuCategories(BaseModel):
    category_name: str
