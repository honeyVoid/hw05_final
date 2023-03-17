import datetime as dt


def year(request):
    """Отображает текущий год в fotter.html"""
    today_year = dt.datetime.now()
    return {
        'year': today_year.year
    }
