# модель данных бюджетного помощника
# здесь собраны структуры данных и класс Ledger, который ведет учет расходов

DAYS = 31

# стек на списке, в нем держим номера расходов для отмены последнего добавления
class Stack:

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.items:
            return self.items.pop()
        return None

    def is_empty(self):
        return len(self.items) == 0


# узел дерева, ключ это пара (сумма, номер), номер делает ключи уникальными
# поэтому равные суммы не сталкиваются ни при вставке, ни при удалении
class Node:

    def __init__(self, key, day, category):
        self.key = key
        self.day = day
        self.category = category
        self.left = None
        self.right = None


# бинарное дерево поиска расходов по сумме
class BST:

    def __init__(self):
        self.root = None

    def insert(self, key, day, category):
        self.root = self._insert(self.root, key, day, category)

    def _insert(self, node, key, day, category):
        if node is None:
            return Node(key, day, category)
        if key < node.key:
            node.left = self._insert(node.left, key, day, category)
        else:                       # ключи уникальны, значит key больше, идем вправо
            node.right = self._insert(node.right, key, day, category)
        return node

    # симметричный обход, расходы по возрастанию суммы
    def in_order(self):
        out = []
        self._walk(self.root, out)
        return out

    def _walk(self, node, out):
        if node is None:
            return
        self._walk(node.left, out)
        out.append((node.key[0], node.day, node.category))   # key[0] это сумма
        self._walk(node.right, out)

    # все расходы с суммой от low до high
    # берем обход по возрастанию и оставляем только подходящие суммы
    def in_range(self, low, high):
        out = []
        for amount, day, category in self.in_order():
            if low <= amount <= high:
                out.append((amount, day, category))
        return out

    # удаляет узел по ключу, нужен для отмены расхода
    def remove(self, key):
        self.root = self._remove(self.root, key)

    def _remove(self, node, key):
        if node is None:
            return None
        if key < node.key:
            node.left = self._remove(node.left, key)
        elif key > node.key:
            node.right = self._remove(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # два потомка, ищем минимум правого поддерева и переносим его в узел
            heir = node.right
            while heir.left is not None:
                heir = heir.left
            node.key, node.day, node.category = heir.key, heir.day, heir.category
            node.right = self._remove(node.right, heir.key)
        return node

# проверяет поля и собирает запись о расходе, при ошибке возвращает ValueError
def make_record(number, day, amount, category):
    if not 1 <= day <= DAYS:
        raise ValueError(f"день должен быть от 1 до {DAYS}")
    if amount <= 0:
        raise ValueError("сумма должна быть больше нуля")
    name = category.strip()
    if name == "":
        name = "без категории"
    return {
        "id": number,
        "day": day,
        "amount": amount,
        "category": name,
    }


# строка с данными расхода для вывода на экран
def record_line(record):
    number = record["id"]
    day = record["day"]
    amount = record["amount"]
    category = record["category"]
    return f"#{number} день {day}, {amount}, {category}"


# ведет список расходов, дневные и накопленные суммы, дерево, стек отмены и лимиты
class Ledger:

    def __init__(self):
        self.records = []               # все расходы по порядку добавления
        self.by_id = {}                 # номер расхода -> расход
        self.next_id = 1                # номер для следующего расхода
        self.daily = [0] * (DAYS + 1)   # сумма расходов по дням, индекс 0 не используем
        self.prefix = [0] * (DAYS + 1)  # префиксные суммы по дням
        self.tree = BST()               # дерево расходов по сумме
        self.undo_stack = Stack()       # номера расходов для отмены
        self.limits = {}                # категория -> лимит трат

    # пересчитывает префиксные суммы по дневным суммам
    def recompute_prefix(self):
        for i in range(1, DAYS + 1):
            self.prefix[i] = self.prefix[i - 1] + self.daily[i]

    # добавляет расход во все структуры и запоминает его номер для отмены
    def add(self, day, amount, category):
        record = make_record(self.next_id, day, amount, category)
        self.next_id += 1
        self.records.append(record)
        self.by_id[record["id"]] = record
        self.daily[day] += amount
        self.tree.insert((amount, record["id"]), day, record["category"])
        self.recompute_prefix()
        self.undo_stack.push(record["id"])
        return record

    # отменяет последний добавленный расход, убирает его из всех структур
    def undo(self):
        number = self.undo_stack.pop()
        if number is None:
            return None
        record = self.by_id.pop(number, None)
        if record is None:
            return None
        self.records.remove(record)
        self.daily[record["day"]] -= record["amount"]
        self.tree.remove((record["amount"], number))
        self.recompute_prefix()
        return record

    # сумма расходов за период с дня a по день b
    def period_sum(self, a, b):
        return self.prefix[b] - self.prefix[a - 1]

    # линейный поиск дня с максимальным расходом
    def peak_day(self):
        best = 1
        for day in range(1, DAYS + 1):
            if self.daily[day] > self.daily[best]:
                best = day
        return best, self.daily[best]

    # общая сумма всех расходов за месяц
    def month_total(self):
        return self.prefix[DAYS]

    # все расходы по возрастанию суммы из дерева
    def by_amount(self):
        return self.tree.in_order()

    # расходы с суммой от low до high из дерева
    def in_range(self, low, high):
        return self.tree.in_range(low, high)

    # задает лимит трат для категории
    def set_limit(self, category, amount):
        self.limits[category] = amount
