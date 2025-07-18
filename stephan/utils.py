from .models import BoardingReceipt


def get_next_serial(landlord):
    latest_receipt = BoardingReceipt.objects.filter(landlord=landlord).order_by('-serial_number').first()
    if latest_receipt:
        return latest_receipt.serial_number + 1
    return 1
