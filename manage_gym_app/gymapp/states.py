from gymapp.models import StatusInvoice, StatusPackage
from datetime import datetime

class InvoiceState:
    def __init__(self, invoice):
        self.invoice = invoice

    def pay(self, calculate_date):
        raise Exception("Hành động không hợp lệ")

    def cancel(self):
        raise Exception("Hành động không hợp lệ")

class PendingState(InvoiceState):
    def pay(self, calculate_date):
        self.invoice.status = StatusInvoice.PAID
        self.invoice.payment_date = datetime.now()

        mp = self.invoice.member_package
        if mp:
            s, e = calculate_date(mp.member_id, mp.package.duration)
            mp.startDate = s
            mp.endDate = e
            mp.status = StatusPackage.ACTIVE
        return True, "Thanh toán và kích hoạt gói tập thành công!"

    def cancel(self):
        self.invoice.status = StatusInvoice.FAILED
        mp = self.invoice.member_package
        if mp:
            mp.status = StatusPackage.EXPIRED
        return True, "Hóa đơn đã được hủy thành công."

class PaidState(InvoiceState):
    def pay(self, calculate_date):
        return False, "Hóa đơn này đã được thanh toán trước đó."

class FailedState(InvoiceState):
    def cancel(self):
        return False, "Hóa đơn này đã bị hủy rồi"

def get_invoice_state(invoice):
    if invoice.status == StatusInvoice.PENDING:
        return PendingState(invoice)
    elif invoice.status == StatusInvoice.PAID:
        return PaidState(invoice)
    elif invoice.status == StatusInvoice.FAILED:
        return FailedState(invoice)