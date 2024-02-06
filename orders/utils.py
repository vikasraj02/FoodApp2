import datetime


def generate_order_number(pk):
    crrent_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    order_number = crrent_datetime + str(pk)
    return order_number