def status(ping: float) -> str:
    if 0 < ping < 25:
        res = "Отличное"
    elif 25 <= ping < 65:
        res = "Нормальное"
    elif 65 <= ping < 100:
        res = "Медленное"
    elif 100 <= ping < 250:
        res = "Плохое"
    elif 250 <= ping < 400:
        res = "Возможна кибератака"
    else:
        res = "Сайт упал"
    return res
