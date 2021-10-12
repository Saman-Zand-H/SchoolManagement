from django.db.models import Q

from datetime import datetime, date


def filter_by_timestamp(since, till):
    if since and till:
        return Q(timestamp__range=[since, till])
    elif since and not till:
        return Q(timestamp__gt=since)
    elif not since and till:
        return Q(timestamp__lt=till)
    else:
        return None


def loop_through_month_number(month_number):
    """
    This way we will never get an unexpected result
    """
    year = date.today().year

    if month_number >= 13:
        return [(month_number % 13) + 1, year + 1]
    elif month_number < 0:
        return [(month_number % 13), year-1]
    elif month_number == 0:
        return [month_number + 1, year]
    else:
        return [month_number, year]


def get_month_from_number(number):
    strf_number = str(number)
    datetime_object = datetime.strptime(strf_number, "%m")
    return datetime_object.strftime("%b")
