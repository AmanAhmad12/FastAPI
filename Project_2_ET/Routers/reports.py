from fastapi import APIRouter, Response, Request, Depends
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

# =========================
# Database Imports
# =========================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.db import get_db
from services import get_current_user

from Models import (
    IncomeModel,
    ExpenseModel,
    BudgetModel
)

# =========================
# Router
# =========================

report = APIRouter( prefix="/report",tags=["Report Route"])


# For Rate Limiting  : 

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address) # bases in remote address not the user_id for user_id we have to create a new logic 


# ROLE_LIMITS = {
#     "ADMIN": "5/hour",
#     "USER": "2/hour"
# }

# def get_user_key(request: Request):

#     auth_header = request.headers.get("Authorization")

#     if not auth_header:
#         return request.client.host

#     try:
#         token = auth_header.replace("Bearer ", "")

#         payload = JWTService().decode(token)

#         return str(payload["user_id"])

#     except Exception:
#         return request.client.host


# limiter = Limiter(
#     key_func=get_user_key
# )


# def get_role(request: Request):

#     auth_header = request.headers.get("Authorization")

#     if not auth_header:
#         return None

#     try:

#         token = auth_header.replace("Bearer ", "")

#         payload = JWTService().decode(token)

#         return payload.get("role")

#     except Exception:
#         return None


# =========================
# Report Model
# =========================

class Report(BaseModel):
    user_id: UUID
    total_income: float
    total_expense: float
    total_budget: float
    remaining_budget: float
    savings: float

    model_config = ConfigDict(from_attributes=True)

# =========================
# Response Model
# =========================

class Report_Response(BaseModel):
    data: list[Report] = Field(default_factory=list)
    msg: str
    error: str = "***NO ERROR***"

# =========================
# Report API
# =========================

@report.get("/summary",response_model=Report_Response,description="Generate Financial Report")
# @limiter.limit("5/hour")
async def Generate_Report(
    request: Request,
    db: AsyncSession = Depends(get_db),
    curr_user=Depends(get_current_user)
):

    # =====================================================
    # FOR INTERNAL DB
    # =====================================================

    # total_income = 0.0
    # total_expense = 0.0
    # total_budget = 0.0
    # total_remaining_budget = 0.0

    # for income in income_DB:
    #     if income.user_id == curr_user.user_id:
    #         total_income += income.amount

    # for expense in expense_DB:
    #     if expense.user_id == curr_user.user_id:
    #         total_expense += expense.amount

    # for budget in budget_DB:
    #     if budget.user_id == curr_user.user_id:
    #         total_budget += budget.budget_amount
    #         total_remaining_budget += budget.remaining_amount

    # if (
    #     total_income == 0
    #     and total_expense == 0
    #     and total_budget == 0
    # ):
    #     return Response(
    #         content=Report_Response(
    #             data=[],
    #             msg="ERROR",
    #             error="NO DATA FOUND FOR THIS USER !!!"
    #         ).model_dump_json(),
    #         status_code=404,
    #         media_type="application/json"
    #     )

    # report_data = Report(
    #     user_id=curr_user.user_id,
    #     total_income=total_income,
    #     total_expense=total_expense,
    #     total_budget=total_budget,
    #     remaining_budget=total_remaining_budget,
    #     savings=total_income - total_expense
    # )

    # return Response(
    #     content=Report_Response(
    #         data=[report_data],
    #         msg="REPORT GENERATED SUCCESSFULLY !!!"
    #     ).model_dump_json(),
    #     status_code=200,
    #     media_type="application/json"
    # )

    # =====================================================
    # FOR REAL DATABASE
    # =====================================================

    await Rate_limiter(curr_user)

    income_result = await db.execute(
        select(IncomeModel).where(
            IncomeModel.user_id == curr_user.user_id
        )
    )

    incomes = income_result.scalars().all()
    # ----------------------------------------------

    expense_result = await db.execute(
        select(ExpenseModel).where(
            ExpenseModel.user_id == curr_user.user_id
        )
    )

    expenses = expense_result.scalars().all()
    # ---------------------------------------------=

    budget_result = await db.execute(
        select(BudgetModel).where(
            BudgetModel.user_id == curr_user.user_id
        )
    )

    budgets = budget_result.scalars().all()
    # -----------------------------------------------=

    total_income = sum(
        income.amount
        for income in incomes
    )

    total_expense = sum(
        expense.amount
        for expense in expenses
    )

    total_budget = sum(
        budget.budget_amount
        for budget in budgets
    )

    total_remaining_budget = sum(
        budget.remaining_amount
        for budget in budgets
    )

    if (
        total_income == 0
        and total_expense == 0
        and total_budget == 0
    ):
        return Response(
            content=Report_Response(
                data=[],
                msg="ERROR",
                error="NO DATA FOUND FOR THIS USER !!!"
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    report_data = Report(
        user_id=curr_user.user_id,
        total_income=total_income,
        total_expense=total_expense,
        total_budget=total_budget,
        remaining_budget=total_remaining_budget,
        savings=total_income - total_expense
    )

    return Response(
        content=Report_Response(
            data=[report_data],
            msg="REPORT GENERATED SUCCESSFULLY !!!"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )