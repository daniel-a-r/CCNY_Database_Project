from datetime import datetime, date

def get_hours_minutes_seconds(duration):    
    hours, minutes, seconds = list(map(int, str(duration).split(':')))

    return hours, minutes, seconds


def format_album_duration(duration):
    hours, minutes, seconds = list(map(int, str(duration).split(':')))

    if hours >= 1:
        return f'{hours} hr {minutes} min'
    else:
        return f'{minutes} min {seconds} sec'


def format_track_duration(duration):
    hours, minutes, seconds = list(map(int, str(duration).split(':')))
    
    if hours >= 1:
        return f'{hours}:{minutes:02d}:{seconds:02d}'
    else:
        return f'{minutes}:{seconds:02d}'


def format_release_date(release_date):
    months = {
        1: 'January',
        2: 'February ',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }

    if isinstance(release_date, str):
        year, month, day = list(map(int, release_date.split('-')))
    else:
        year = release_date.year
        month = release_date.month
        day = release_date.day

    return f'{months[month]} {day}, {year}'