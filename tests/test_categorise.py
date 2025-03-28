from datetime import datetime

from lib.categorise import Category, categorise_transaction
from lib.transaction import Transaction, TransactionType


def dummy_type(type: TransactionType):
    return Transaction(datetime.now(), 0, type, "")


def dummy_desc(desc: str):
    return Transaction(datetime.now(), 0, TransactionType.CardPayment, desc)


def test_transaction_types():
    assert (
        categorise_transaction(dummy_type(TransactionType.TransferIn))
        == Category.TransferIn
    )
    assert (
        categorise_transaction(dummy_type(TransactionType.TransferOut))
        == Category.TransferOut
    )
    assert (
        categorise_transaction(dummy_type(TransactionType.Interest))
        == Category.Interest
    )
    assert (
        categorise_transaction(dummy_type(TransactionType.Credit)) == Category.Cashback
    )
    assert categorise_transaction(dummy_type(TransactionType.Salary)) == Category.Salary
    assert (
        categorise_transaction(dummy_type(TransactionType.Investment))
        == Category.Investments
    )


def test_transaction_descs():
    assert (
        categorise_transaction(
            dummy_desc("DOT MYKI RELOAD MELBOURNE Date 13/12/24 Card 6522")
        )
        == Category.Transport
    )
    assert (
        categorise_transaction(dummy_desc("Myki Payments Melbourne Au"))
        == Category.Transport
    )
    assert (
        categorise_transaction(dummy_desc("ART MEM VOL NetBank BPAY 38232 9029695526"))
        == Category.Investments
    )
    assert (
        categorise_transaction(dummy_desc("AGL Telco Moruya Au")) == Category.Utilities
    )
    assert (
        categorise_transaction(dummy_desc("COLES 0583 170491 FITZROY"))
        == Category.Groceries
    )
    assert (
        categorise_transaction(dummy_desc("WOOLWORTHS/313 VICTORIA 442720SABBOTSFORD"))
        == Category.Groceries
    )
    assert (
        categorise_transaction(dummy_desc("ALDI STORES - MOONEE P MOONEE PONDS"))
        == Category.Groceries
    )
    assert (
        categorise_transaction(dummy_desc("METRO PETROLEUM CARLTO CARLTON"))
        == Category.Transport
    )
    assert (
        categorise_transaction(dummy_desc("Paypal *Amaysimmobi 4029357733 Au"))
        == Category.Utilities
    )
