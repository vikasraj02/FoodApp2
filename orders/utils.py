import datetime
import simplejson as json


def generate_order_number(pk):
    crrent_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    order_number = crrent_datetime + str(pk)
    return order_number
def order_total_by_vendor(order,vendor_id):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    subtotal =0
    tax = 0
    tax_dict = {}
    for key, value in data.items():
        subtotal += float(key)
        val = value.replace("'",'"')
        val = json.loads(val)
        tax_dict.update(val)
        for i in val:
            for j in val[i]:
                tax += float(val[i][j])
    grand_total = float(subtotal)+float(tax) 
    context = {
        "subtotal":subtotal,
        "grand_total":grand_total,
        "tax_dict":tax_dict,
    }
    return context 
