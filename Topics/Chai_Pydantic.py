from pydantic import BaseModel , Field,field_validator,model_validator,computed_field , ConfigDict
from fastapi import FastAPI
from datetime import date ,datetime 
from typing import Optional ,List # Dict

app = FastAPI()

class Address(BaseModel):
    street:str
    @field_validator("street")
    def minlength_of_street(cls,value):

        if len(value) < 3:
            raise ValueError(
                "Street Length must be greater then 3 !!!"
            )

    city:str
    @field_validator("city")
    def minlength_of_street(cls,value):

        if len(value) < 3:
            raise ValueError(
                "Street Length must be greater then 3 !!!"
            )

    postal_code:str
    @field_validator("postal_code")
    def minlength_of_street(cls,value):

        if len(value) < 3:
            raise ValueError(
                "Street Length must be greater then 3 !!!"
            )

class User(BaseModel):
    user_id:int

    name:str = Field(
            ...,
            min_length=3,
            max_length=30,
            description="Name contains atleast 3 char and atmost 30 char"
        )

    age:Optional[int]=20

    password:str

    @field_validator('password')
    def password_length(cls,value):
        if len(value)<4 :
            raise ValueError(
                "Password length must be atleast 4 characters"
            )
        return value

    start_date :date
    end_date: date
    
    @model_validator(mode="after")
    def validate_dates(self):
        if(self.start_date > self.end_date):
            raise ValueError(
                "Start date cannot be greater than end Date"
            )
        return self

    budget_amount:float
    spent_amount:float

    @field_validator('spent_amount')
    @classmethod
    def min_spent_amount(cls,value):
        if value < 100 :
            raise ValueError(
                "Minimun Spent should be Greater than 100 !!!"
            )
        return value

    @computed_field
    @property
    def remaining_amount(self) -> float:

        return (
            self.budget_amount-self.spent_amount
        )

    address :Address # nested _model

    curr_datetime :datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d   %H:%M:%S")
        },
        validate_assignment=True, # validate at the time of updation 
        extra='forbid',  # means no other attributes allowed
    )
    

# forward references

class comment(BaseModel):

    id:int
    content:str
    replies:Optional[list['comment']]=None

comment.model_rebuild()    # to activale the forword refernecing(model calling itself)

    # ------------------------------------------------------------


    
@app.post("/")
def function(user:User):
    return f"Remaining_Amount : {user.remaining_amount}"



@app.post("/get")
def function(user: User):
    return user