from dateutil import relativedelta
from datetime import date


def get_charts_labels_ready():
    eight_months_chart_time = date.today() - relativedelta.relativedelta(months=4)
    six_months_chart_time = date.today() - relativedelta.relativedelta(months=3)
    eight_months_chart_months = [
        eight_months_chart_time 
        + relativedelta.relativedelta(months=i) for i in range(8)]
    six_months_chart_months = [
        six_months_chart_time 
        + relativedelta.relativedelta(months=i) for i in range(6)]
    # The way the names are formatted lets chart.js recognize the values
    eight_months_chart_month_names = [
        f'"{month.strftime("%b")}"' for month in eight_months_chart_months]
    six_months_chart_month_names = [
        f'"{month.strftime("%b")}"' for month in six_months_chart_months]
    return [eight_months_chart_month_names, six_months_chart_month_names]
