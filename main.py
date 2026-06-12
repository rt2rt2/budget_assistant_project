# консольный интерфейс бюджетного помощника, числовое меню и главный цикл

from model import Ledger, DAYS, record_line
from analytics import top_categories, category_report, limit_report, daily_chart


MENU = (
    "\n    Бюджетный помощник\n"
    " 1. Добавить расход\n"
    " 2. Отменить последний расход\n"
    " 3. Сумма расходов за период\n"
    " 4. День с максимальным расходом\n"
    " 5. Общая сумма за месяц\n"
    " 6. Топ категорий по тратам\n"
    " 7. Статистика по категориям\n"
    " 8. Задать лимит категории\n"
    " 9. Проверка лимитов\n"
    "10. Все траты по возрастанию суммы\n"
    "11. Траты в диапазоне суммы\n"
    "12. Расходы по дням\n"
    " 0. Выход"
)


# читает целое число в нужных границах, повторяя запрос при ошибке
def read_int(prompt, low, high):
    while True:
        text = input(prompt).strip()
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print(f"Введите целое число от {low} до {high}.")


# выводит список троек (сумма, день, категория) из дерева
def show_rows(rows):
    for amount, day, category in rows:
        print(f"  {amount} | день {day} | {category}")


def action_add(ledger):
    day = read_int(f"День (1-{DAYS}): ", 1, DAYS)
    amount = read_int("Сумма: ", 1, 10 ** 9)
    category = input("Категория (введите enter для пропуска): ").strip()
    record = ledger.add(day, amount, category)
    print(f"Добавлен расход #{record['id']}.")


def action_undo(ledger):
    record = ledger.undo()
    if record is None:
        print("Отменять нечего.")
    else:
        print("Отменен расход: " + record_line(record) + ".")


def action_period(ledger):
    a = read_int("День A: ", 1, DAYS)
    b = read_int("День B: ", 1, DAYS)
    if a > b:
        a, b = b, a   # границы можно вводить в любом порядке
    print(f"Сумма расходов с дня {a} по день {b} равна {ledger.period_sum(a, b)}.")


def action_peak(ledger):
    day, amount = ledger.peak_day()
    if amount == 0:
        print("Расходов пока нет.")
    else:
        print(f"Больше всего потрачено в день {day} на сумму {amount}.")


def action_total(ledger):
    print(f"Всего за месяц потрачено: {ledger.month_total()}.")


def action_top(ledger):
    top = top_categories(ledger.records)
    if not top:
        print("Расходов пока нет.")
        return
    print("Топ категорий по тратам:")
    for category, total in top:
        print(f"  {category}: {total}")


def action_stats(ledger):
    rows = category_report(ledger.records)
    if not rows:
        print("Расходов пока нет.")
        return
    print("Статистика по категориям:")
    for category, total, count, average, share in rows:
        print(f"  {category}: сумма {total}, трат {count}, "
              f"средний чек {round(average)}, доля {round(share, 1)}%")


def action_set_limit(ledger):
    category = input("Категория: ").strip()
    if not category:
        print("Категория не может быть пустой.")
        return
    amount = read_int("Лимит: ", 1, 10 ** 9)
    ledger.set_limit(category, amount)
    print(f"Лимит для категории {category} равен {amount}.")


def action_limits(ledger):
    rows = limit_report(ledger.records, ledger.limits)
    if not rows:
        print("Лимиты пока не заданы.")
        return
    print("Проверка лимитов:")
    for category, spent, limit, over in rows:
        mark = "превышен" if over else "в норме"
        print(f"  {category}: потрачено {spent} из {limit} ({mark})")


def action_by_amount(ledger):
    rows = ledger.by_amount()
    if not rows:
        print("Трат нет.")
        return
    print("Траты по возрастанию суммы:")
    show_rows(rows)


def action_in_range(ledger):
    low = read_int("Сумма от: ", 0, 10 ** 9)
    high = read_int("Сумма до: ", 0, 10 ** 9)
    if low > high:
        low, high = high, low
    rows = ledger.in_range(low, high)
    if not rows:
        print("Подходящих трат нет.")
        return
    print(f"Траты с суммой от {low} до {high}:")
    show_rows(rows)


def action_daily(ledger):
    lines = daily_chart(ledger.daily)
    if not lines:
        print("Расходов пока нет.")
        return
    print("Расходы по дням:")
    for line in lines:
        print("  " + line)


# несколько расходов для демонстрации работы программы
def load_demo(ledger):
    samples = [
        (3, 1200, "продукты"), (3, 450, "транспорт"), (5, 300, "кафе"),
        (7, 2500, "продукты"), (10, 800, "развлечения"), (12, 150, "транспорт"),
        (15, 5000, "одежда"), (18, 600, "продукты"), (20, 350, "кафе"),
        (25, 1000, "развлечения"),
    ]
    for day, amount, category in samples:
        ledger.add(day, amount, category)
    ledger.undo_stack.items = []   # демо расходы не считаем действиями пользователя


def main():
    ledger = Ledger()
    answer = input("Загрузить демонстрационные расходы? (да/нет): ").strip().lower()
    if answer == "да":
        load_demo(ledger)
        print(f"Добавлено расходов: {len(ledger.records)}.")
    print(MENU)
    while True:
        choice = input("Выберите команду: ").strip()
        if choice == "0":
            print("Выход.")
            break
        elif choice == "1":
            action_add(ledger)
        elif choice == "2":
            action_undo(ledger)
        elif choice == "3":
            action_period(ledger)
        elif choice == "4":
            action_peak(ledger)
        elif choice == "5":
            action_total(ledger)
        elif choice == "6":
            action_top(ledger)
        elif choice == "7":
            action_stats(ledger)
        elif choice == "8":
            action_set_limit(ledger)
        elif choice == "9":
            action_limits(ledger)
        elif choice == "10":
            action_by_amount(ledger)
        elif choice == "11":
            action_in_range(ledger)
        elif choice == "12":
            action_daily(ledger)
        else:
            print("Нет такой команды.")


if __name__ == "__main__":
    main()
