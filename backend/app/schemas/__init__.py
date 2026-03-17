from app.schemas.clinic import ClinicCreate, ClinicOut
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut, PatientWithStatus
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.schemas.expense import ExpenseCategoryCreate, ExpenseCategoryOut, ExpenseCreate, ExpenseOut
from app.schemas.goal import GoalCreate, GoalOut
from app.schemas.dashboard import (
    Level1Summary, Level2Revenue, Level2Expenses,
    Level3ContributionMargin, ProductRanking,
)
