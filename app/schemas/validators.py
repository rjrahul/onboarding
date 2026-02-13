from datetime import datetime, date

def is_customer_less_than_18(value: str):
    if value is None:
        return value
    
    born = datetime.strptime(value, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    if age < 18:
        raise ValueError(f'Customer is less than 18 years')
    return value  

