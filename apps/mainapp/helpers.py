from django.db.models import Q

from datetime import datetime, date


def filter_by_timestamp(since, till):
    if since is not None and till is not None:
        return Q(timestamp__range=[since, till])
    elif since is not None and till is None:
        return Q(timestamp__gte=since)
    elif since is None and till is not None:
        return Q(timestamp__lte=till)
    else:
        return None


def loop_through_month_number(month: int):
    """
    Takes care of negative numbers and numbers greater than 12 by updating the year
    """
    year = date.today().year

    if month >= 13:
        month = (month % 13) + 1
        year += 1
    elif month < 0:
        month %= 13
        year -= 1
    elif month == 0:
        month += 1
    return (year, month)


def get_month_from_number(number):
    strf_number = str(number)
    datetime_object = datetime.strptime(strf_number, "%m")
    return datetime_object.strftime("%b")
