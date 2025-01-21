from typing import Annotated, Callable, Tuple
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlmodel import Field, SQLModel
from fastapi_demo.database import SessionDep
from fastapi_demo.auth import auth, optional_auth
from fastapi_demo.database import SessionDep
import logging

#Use standard python logging 
LOG = logging.getLogger(__name__)

router = APIRouter()

#https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
#Reduce duplication by defining request/reponse models in terms of database models.

#SQLModel models
class UserBase(SQLModel):
    username:str
    pass

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    auth0_sub:str

#Request/Response Models
class UserPublic(UserBase):
    id: int
    pass

class UserCreate(UserBase):
    auth0_sub:str
    pass

class UserPrivate(User):
    pass


def _get_user(id:int, session:SessionDep)->User:
    user = session.get(User, id);
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

# Replace this with whatever authorization scheme you prefer
# Currently verifies the bearer token is the same user as the
# user row being accessed.
class AuthUser:
    '''
    Authenticate the currently logged in user's bearer token against
    the user row being accessed to determine if the bearer owns the row
    or not
    '''
    def __init__(self, auto_error=True):
        self.auto_error = auto_error

    def _check(self, user:User, token:dict[str,str] | None):
        if token is None:
            LOG.info("No auth token provided")
            return False
        sub = token["sub"]
        if user.auth0_sub != sub:
            LOG.info(f"auth sub {sub} cannot access user {user.id}, {user.auth0_sub}")
            return False
        return True
    
    async def __call__(self, id:int, session:SessionDep, token=Security(optional_auth))->Tuple[User, bool]:  
        user = _get_user(id, session)
        authorized = self._check(user, token)
        if not(authorized) and self.auto_error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return user, authorized


AuthUserDep = Annotated[Tuple[User, bool], Depends(AuthUser(auto_error=True))]
AuthUserOptionalDep = Annotated[Tuple[User, bool], Depends(AuthUser(auto_error=False))]


@router.post("/user")
def create_user(session:SessionDep, user_create:UserCreate, token=Security(auth))->UserPrivate:
    if user_create.auth0_sub != token["sub"]:
        LOG.info(f"User {token['sub']} attempted to create a record for {user_create.auth0_sub}. Rejecting.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    user = User.model_validate(user_create)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserPrivate.model_validate(user)


@router.get("/user/{id}")
def get_user(authUser:AuthUserOptionalDep)->UserPublic | UserPrivate:
    [user, authorized] = authUser
    # model_validate will automatically convert the data in the 
    # database model for a full row into just the fields defined in the
    # target model.
    if authorized:
        return UserPrivate.model_validate(user)
    return UserPublic.model_validate(user)

@router.delete("/user/{id}")
def delete_user(session:SessionDep, authUser:AuthUserDep)->None:
    [user,_] = authUser
    session.delete(user)
    session.commit()
