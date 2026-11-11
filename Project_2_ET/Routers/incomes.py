from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID, uuid4

from config.db import get_db

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from services import get_current_user
from Models import IncomeModel


income = APIRouter(prefix="/income", tags=["Income Route"])


class Incomes(BaseModel):
    income_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    source: str
    amount: float
    description: str
    income_date: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class Incomes_create(BaseModel):
    source: str
    amount: float
    description: str


class Income_output(BaseModel):
    data: list[Incomes] = Field(default_factory=list)
    msg: str
    error: str = "   ***NO ERROR***   "


# DB: list[Incomes] = []


@income.post("/add", response_model=Income_output)
async def Add_new_Income_Source(
    new_income: Incomes_create,
    request: Request,
    db: AsyncSession = Depends(get_db),
    curr_user=Depends(get_current_user)
):

    # for temp in DB:
    #     if(temp.user_id==new_income.user_id and temp.source==new_income.source and temp.description==new_income.description and temp.amount==new_income.amount):
    #         raise HTTPException(
    #             detail=" This Income is Already Present into the DB",
    #             status_code=409
    #         )
    #
    # Income_data=Incomes(
    #     user_id=new_income.user_id,
    #     source=new_income.source,
    #     amount=new_income.amount,
    #     description=new_income.description
    # )
    #
    # DB.append(Income_data)
    #
    # return Income_output(
    #     data=[Income_data],
    #     msg="New Income Source Added SuccessFully !!! "
    # )

    data_model = IncomeModel(
        user_id=curr_user.user_id,
        source=new_income.source,
        amount=new_income.amount,
        description=new_income.description
    )

    db.add(data_model)

    await db.commit()
    await db.refresh(data_model)

    return Response(
        content=Income_output(
            data=[Incomes.model_validate(data_model)],
            msg="New Income Source Added Successfully !!!"
        ).model_dump_json(),
        status_code=201,
        media_type="application/json"
    )



# class IncomeSourceResponse(BaseModel):
#     user_id: UUID
#     source: str
#     amount: float

#     model_config = ConfigDict(from_attributes=True)


# Source_DB: list[IncomeSourceResponse] = []

# ==================================================================================================   


@income.get("/get/{user_id}", response_model=Income_output)
async def Get_all_the_income_sources_By_user_id(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    curr_user=Depends(get_current_user)
):

    # for temp in DB:
    #     if(temp.user_id==user_id):
    #         Source_DB.append(
    #             IncomeSourceResponse(
    #                 user_id=temp.user_id,
    #                 source=temp.source,
    #                 amount=temp.amount
    #             )
    #         )
    #
    #         return {
    #             "data": Source_DB,
    #             "msg": "Successfully Fetched All the Income Sources !!!"
    #         }
    #
    # raise HTTPException(
    #     detail="User Does Not Have any Income or User Not Found !!!",
    #     status_code=404
    # )

    temp_data = await db.execute(
        select(IncomeModel).where(
            IncomeModel.user_id == user_id
        )
    )

    data_model = temp_data.scalars().all()

    if not data_model:
        return Response(
            content=Income_output(
                data=[],
                msg="ERROR",
                error="User Does Not Have Any Income !!!"
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    return Response(
        content=Income_output(
            data=[
                Incomes.model_validate(temp)
                for temp in data_model
            ],
            msg="Successfully Fetched All the Income Sources !!!"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )


@income.patch("/update/{income_id}", response_model=Income_output)
async def Update_the_perticular_Income_Source_OR_Income_amount(
    income_id: UUID,
    request: Request,
    amount: float = 0.0,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
    curr_user=Depends(get_current_user)
):

    # for temp in DB:
    #     if(temp.user_id==user_id):
    #
    #         if(amount!=0.0 and source!=None):
    #             temp.amount=amount
    #             temp.source=source
    #
    #         elif(amount!=0.0 and source==None):
    #             temp.amount=amount
    #
    #         elif(amount==0.0 and source!=None):
    #             temp.source=source
    #
    #         return Income_output(
    #             data=[temp],
    #             msg="Successfully Updated !!!"
    #         )
    #
    # raise HTTPException(
    #     detail="User Is Not Found !!! ",
    #     status_code = 404
    # )

    temp_data = await db.execute(
        select(IncomeModel).where(
            IncomeModel.income_id == income_id
        )
    )

    data_model = temp_data.scalar_one_or_none()

    if not data_model:
        return Response(
            content=Income_output(
                data=[],
                msg="ERROR",
                error="Income_ID Not Found !!!"
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    if amount != 0.0:
        data_model.amount = amount

    if source is not None:
        data_model.source = source

    await db.commit()
    await db.refresh(data_model)

    return Response(
        content=Income_output(
            data=[Incomes.model_validate(data_model)],
            msg="Successfully Updated !!!"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )

# ====================================================================================================

@income.delete("/delete/{income_id}", response_model=Income_output)
async def Delete_the_Income_By_Income_ID(
    income_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    # for index,temp in enumerate(DB):
    #     if(temp.income_id==income_id):
    #
    #         DB.remove(DB[index])
    #
    #         return Income_output(
    #             data=[temp],
    #             msg="Successfully deleted !!!"
    #         )
    #
    # raise HTTPException(
    #     detail="Income_ID not Found !!!",
    #     status_code=401
    # )

    temp_data = await db.execute(
        delete(IncomeModel)
        .where(
            IncomeModel.income_id == income_id
        )
        .returning(IncomeModel.income_id)
    )

    data_model = temp_data.scalar_one_or_none()

    if not data_model:
        return Response(
            content=Income_output(
                data=[],
                msg="ERROR",
                error="Income_ID Not Found !!!"
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    await db.commit()

    return Response(
        content=Income_output(
            msg=f"Successfully deleted Income_ID : {data_model}"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )