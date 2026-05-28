days = 31

# Узел дерева, ключом служит пара (сумма, номер расхода)
# Номер делает ключи уникальными, поэтому равные суммы не мешают удалению
# Дополнительно в каждом узле хранится день и категория
class Node:
    def __init__(self, key, day, category):
        self.key = key
        self.day = day
        self.category = category
        self.l_child = None
        self.r_child = None

# Бинарное дерево поиска
class BST:
    def __init__(self):
        self.root = None
    # Вставка нового расхода, ключи сравниваются как пары и всегда различны
    def insert(self, key, day, category):
        self.root = self._insert(self.root, key, day, category)

    def _insert(self, node, key, day, category):
        if node is None:                       # дошли до пустого места, тут и создаем узел
            return Node(key, day, category)
        if key < node.key:
            node.l_child = self._insert(node.l_child, key, day, category)
        else:                                  # ключи уникальны, значит key больше текущего, уходим вправо
            node.r_child = self._insert(node.r_child, key, day, category)
        return node
    # Симметричный обход, выдает расходы по возрастанию суммы
    def in_order(self):
        result = []
        self._in_order(self.root, result)
        return result

    def _in_order(self, node, result):
        if node is None:
            return
        self._in_order(node.l_child, result)
        result.append((node.key[0], node.day, node.category))   # key[0] - сумма расхода
        self._in_order(node.r_child, result)

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, node, key):
        if node is None:                      # ключа в дереве нет
            return None
        if key < node.key:
            node.l_child = self._delete(node.l_child, key)
        elif key > node.key:
            node.r_child = self._delete(node.r_child, key)
        else:
            # Нашли узел. Если есть только один ребенок, возвращаем второго
            if node.l_child is None:
                return node.r_child
            if node.r_child is None:
                return node.l_child
            # При двух потомках заменяем узел на минимум правого поддерева,
            # затем удаляем узел из правого поддерева, где он уже без левого ребенка
            successor = self._min_node(node.r_child)
            node.key = successor.key
            node.day = successor.day
            node.category = successor.category
            node.r_child = self._delete(node.r_child, successor.key)
        return node
    # Самый левый узел поддерева (минимальный ключ)
    def _min_node(self, node):
        while node.l_child is not None:
            node = node.l_child
        return node


# Стек для отмены последнего добавления

class Stack:
    def __init__(self):
        self.elements = []

    def is_empty(self):
        return len(self.elements) == 0

    def push(self, item):
        self.elements.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.elements.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.elements[-1]


expenses = []                 # Список расходов [день, сумма, категория, номер]
daily = [0] * (days + 1)      # Суммарный расход по дням, нулевой индекс для удобства не используем
prefix = [0] * (days + 1)     # Префиксные суммы
undo_stack = Stack()
tree = BST()
counter = 0


# Операции над расходами

def add_expense(day, amount, category):
    # Добавляет расход во все структуры и обновляет префиксные суммы
    global counter
    counter += 1
    expense = [day, amount, category, counter]
    expenses.append(expense)
    daily[day] += amount
    undo_stack.push(expense)
    tree.insert((amount, counter), day, category)
    rebuild_prefix()


def undo_last():
    # Отменяет последний добавленный расход
    if expense is None:
        return None
    day, amount, category, number = expense
    expenses.remove(expense)
    daily[day] -= amount
    tree.delete((amount, number))
    rebuild_prefix()
    return expense


def rebuild_prefix():
    # Пересчитывает префиксные суммы
    for i in range(1, days + 1):
        prefix[i] = prefix[i - 1] + daily[i]


def range_sum(a, b):
    # Возвращает сумму расходов с дня A по день B по префиксным суммам
    return prefix[b] - prefix[a - 1]


def max_expense_day():
    # Линейный поиск
    best_day = 1
    for day in range(1, days + 1):
        if daily[day] > daily[best_day]:
            best_day = day
    return best_day, daily[best_day]


def insertion_sort(pairs):
    for i in range(1, len(pairs)):
        current = pairs[i]
        j = i - 1
        while j >= 0 and pairs[j][1] < current[1]:
            pairs[j + 1] = pairs[j]
            j -= 1
        pairs[j + 1] = current
    return pairs


def top_categories(limit=5):
    # Считает сумму трат по каждой категории и сортирует их вставками
    totals = {}
    for day, amount, category, number in expenses:
        totals[category] = totals.get(category, 0) + amount
    pairs = list(totals.items())
    insertion_sort(pairs)
    return pairs[:limit]


# Ввод от пользователя

def read_int(prompt, low, high):
    # Читает целое число в нужных границах, повторяя запрос при неверном вводе
    while True:
        text = input(prompt).strip()
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print("Введите целое число от", low, "до", high)

# Команды для меню

def command_add():
    day = read_int("День (1-31): ", 1, days)
    amount = read_int("Сумма: ", 1, 10 ** 9)
    category = input("Категория: ").strip()
    if not category:
        category = "без категории"
    add_expense(day, amount, category)
    print("Расход добавлен")


def command_undo():
    expense = undo_last()
    if expense is None:
        print("Отменять нечего")
    else:
        day, amount, category, number = expense
        print("Отменен расход: день", day, "сумма", amount, "категория", category)


def command_range():
    a = read_int("День A: ", 1, days)
    b = read_int("День B: ", 1, days)
    if a > b:
        a, b = b, a  # можно вводить границы в любом порядке
    print("Сумма расходов с дня", a, "по день", b, "равна", range_sum(a, b))


def command_max_day():
    day, amount = max_expense_day()
    if amount == 0:
        print("Расходов пока нет")
    else:
        print("Больше всего потрачено в день", day, "на сумму", amount)


def command_top():
    top = top_categories()
    if not top:
        print("Расходов пока нет")
        return
    print("Топ категорий по тратам:")
    for category, total in top:
        print(" ", category, "-", total)


def command_tree():
    items = tree.in_order()
    if not items:
        print("Расходов пока нет")
        return
    print("Траты по возрастанию суммы:")
    for amount, day, category in items:
        print(" сумма", amount, "день", day, "категория", category)

#-----------------------------------------------------
# Главный цикл

def main():
    menu = (
        "\n    Бюджетный помощник\n"
        "1. Добавить расход\n"
        "2. Отменить последний расход\n"
        "3. Сумма расходов за период\n"
        "4. День с максимальным расходом\n"
        "5. Топ-5 категорий по тратам\n"
        "6. Все траты по возрастанию суммы\n"
        "0. Выход"
    )
    actions = {
        "1": command_add,
        "2": command_undo,
        "3": command_range,
        "4": command_max_day,
        "5": command_top,
        "6": command_tree,
    }
    while True:
        print(menu)
        choice = input("Выберите команду: ").strip()
        if choice == "0":
            print("Выход")
            break
        action = actions.get(choice)
        if action is None:
            print("Нет такой команды")
        else:
            action()


if __name__ == "__main__":
    main()
