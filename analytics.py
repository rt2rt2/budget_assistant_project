# отчеты и аналитика по расходам

from model import DAYS


# сортировка вставками по убыванию суммы, меняет список на месте
def insertion_sort(pairs):
    for i in range(1, len(pairs)):
        cur = pairs[i]
        j = i - 1
        while j >= 0 and pairs[j][1] < cur[1]:
            pairs[j + 1] = pairs[j]
            j -= 1
        pairs[j + 1] = cur
    return pairs


# суммарные траты по каждой категории
def category_totals(records):
    totals = {}
    for r in records:
        totals[r["category"]] = totals.get(r["category"], 0) + r["amount"]
    return totals


# категории по убыванию суммы трат, отсортированы вставками
def top_categories(records, limit=5):
    pairs = list(category_totals(records).items())
    insertion_sort(pairs)
    if limit is None:
        return pairs
    return pairs[:limit]


# по каждой категории: сумма, число трат, средний чек и доля в процентах
def category_report(records):
    totals = category_totals(records)
    counts = {}
    for r in records:
        counts[r["category"]] = counts.get(r["category"], 0) + 1
    grand = sum(totals.values())
    rows = []
    for category, total in totals.items():
        average = total / counts[category]
        if grand > 0:
            share = total / grand * 100
        else:
            share = 0
        rows.append((category, total, counts[category], average, share))
    insertion_sort(rows)   # по убыванию суммы, сортировка сравнивает второй элемент строки
    return rows


# сравнивает траты по категориям с заданными лимитами
def limit_report(records, limits):
    totals = category_totals(records)
    rows = []
    for category in sorted(limits):     # категории по алфавиту
        limit = limits[category]
        spent = totals.get(category, 0)
        rows.append((category, spent, limit, spent > limit))
    return rows


# расходы по дням, для каждого дня с тратами. строка вида: день и сумма
def daily_chart(daily):
    lines = []
    for day in range(1, DAYS + 1):
        if daily[day] > 0:
            lines.append(f"{day}: {daily[day]}")
    return lines
