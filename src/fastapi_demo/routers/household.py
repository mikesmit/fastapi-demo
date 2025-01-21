from fastapi import APIRouter, HTTPException
from sqlmodel import Session, SQLModel, Field
from fastapi_demo.database import SessionDep

router = APIRouter()

class HouseholdBase(SQLModel):
    pass

class Household(HouseholdBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class HouseholdCreate(HouseholdBase):
    pass

@router.post("/household")
async def create_houshold(item:HouseholdCreate, session:SessionDep)->Household:
    model = Household.model_validate(item)
    session.add(model)
    session.commit()
    session.refresh(model)
    
    return model

def _get_household(id:int, session:Session)->Household:
    model = session.get(Household, id)
    if not model:
        raise HTTPException(status_code=404, detail="Household not found")
    return model

@router.get("/household/{id}")
async def get_household(id:int,
                        session:SessionDep)->Household:
    return _get_household(id, session)
    

@router.delete("/household/{id}")
async def delete_household(id:int, session:SessionDep)->None:
    model = _get_household(id, session)
    session.delete(model)
    session.commit()
