from providers.boq import handle_boq
from providers.coles import handle_coles
from providers.commbank import handle_commbank
from providers.hsbc import handle_hsbc
from providers.ing import handle_ing


if __name__ == "__main__":
    handle_boq()
    handle_coles()
    handle_commbank()
    handle_hsbc()
    handle_ing()
