# Cypher — краткий справочник

Язык декларативных запросов к графу Neo4j. Версиия доки: **Cypher Manual 4.4**.
Граф = **узлы** (`()`) и **отношения** (`-[]->`). Данные — это поток «набор
связываний переменных со значениями», который уточняется по ходу запроса.

---

## 1. Модель данных и идентификаторы

| Элемент              | Синтаксис                                  |
|----------------------|--------------------------------------------|
| Узел                 | `(p)`                                      |
| Узел с лейблом       | `(p:Person)`                               |
| Несколько лейблов    | `(p:Person:Employee)`                      |
| Свойства             | `(p:Person {name:'Andy', age:36})`         |
| Отношение            | `-[r:LIKES]->`                             |
| Несколько типов      | `-[r:LIKES|OWNS]->`                        |
| Путь (переменная)    | `p = (a)-[:KNOWS*1..3]->(b)`               |

Имена лейблов, типов и переменных, содержащие спецсимволы или пробелы,
обрамляются обратными кавычками: `` `Weird Name` ``.

Параметры пишутся с `$`: `$name`, `$props`. Передаются через драйвер.

---

## 2. Паттерны — сердце Cypher

Паттерн — это ASCII-«рисунок» графа. Используется в `MATCH`, `CREATE`, `MERGE`,
а также как **предикат** в `WHERE`.

```cypher
(a)-[r:KNOWS]->(b)            -- направленное отношение
(a)-[r:KNOWS]-(b)             -- ненаправленное (любая сторона)
(a)-[*1..5]->(b)              -- переменная длина 1..5
(a)-[*]->(b)                  -- любая длина (1..∞ по умолчанию)
(a)-[*0..3]->(b)              -- допускается 0 (a и b могут совпасть)
(a {name:'A'})-[:ACTED_IN {role:'Neo'}]->(b)
shortestPath((a)-[*..15]-(b)) -- функция, даёт ОДИН кратчайший путь
allShortestPaths((a)-[*]-(b)) -- ВСЕ кратчайшие пути
```

Важно:
- `-->` означает **исходящее**; `<--` — входящее; `--` — любое направление.
- Внутри одного паттерна одно отношение матчится только один раз.
- Узлы и отношения в паттерне — это **одновременно выражения и предикаты**:
  пустой список путей = `false`, непустой = `true`.

---

## 3. Чтение: MATCH / OPTIONAL MATCH / WHERE

### MATCH
```cypher
MATCH (n)                              -- все узлы
MATCH (n:Person)                       -- все :Person
MATCH (a:Person {name:'A'})-[r:KNOWS]->(b:Person)
WHERE r.since >= 2000
RETURN a, b, r.since
```

### OPTIONAL MATCH
Как `MATCH`, но если часть паттерна не нашлась — переменные получают
`null` (аналог LEFT JOIN в SQL).

### WHERE
`WHERE` — это **НЕ отдельная клауза**, а **под-клауза** `MATCH`,
`OPTIONAL MATCH` и `WITH`. Привязывается к **непосредственно предшествующему**
`MATCH/OPTIONAL MATCH`. Если поставить `WHERE` не туда — другая
производительность и другие результаты.

Операторы:
- Сравнение: `=`, `<>`, `<`, `<=`, `>`, `>=`
- Булевы: `AND`, `OR`, `XOR`, `NOT`
- Строки: `STARTS WITH`, `ENDS WITH`, `CONTAINS` (все case-sensitive)
- Регулярки: `=~ '(?i)Lon.*'` (синтаксис Java regex)
- Принадлежность: `n.name IN ['A','B']`
- Существование свойства: `n.belt IS NOT NULL` (function `exists()` deprecated)
- Динамическое свойство: `n[toLower($k)] = '...'`
- Метка в WHERE: `WHERE n:Swedish`
- Тип отношения: `WHERE type(r) =~ 'K.*'`
- Фильтрация по паттерну-предикату:
  `WHERE (person)-->(peter)`, `WHERE NOT (a)-[:KNOWS]->(b)`

### EXISTS { subquery }
Современная замена паттернов-предикатов: позволяет внутри `WHERE` написать
полноценный `MATCH`:
```cypher
MATCH (a:Person)
WHERE EXISTS { MATCH (a)-[:HAS_DOG]->(:Dog {name:'Rex'}) }
RETURN a
```

### Под-клаузы после `RETURN`/`WITH`
`ORDER BY [ASC|DESC]`, `SKIP n`, `LIMIT n`.

---

## 4. Запись: CREATE / MERGE / SET / REMOVE / DELETE

### CREATE — всегда создаёт, без проверок
```cypher
CREATE (n:Person {name:'Andy'})                   -- один узел
CREATE (n), (m)                                   -- несколько узлов
CREATE (a)-[r:RELTYPE]->(b)                       -- отношение между существующими
CREATE p = (a)-[:LIKES]->(b)<-[:LIKES]-(c)        -- целый путь за раз
CREATE (n:Person $props)                          -- свойства из параметра
```

### MERGE — «найди или создай»
```cypher
MERGE (n:Person {name:'Andy'})                    -- матч по (label+props)
MERGE (a)-[r:KNOWS]->(b)                          -- требует ≥1 уже bound узел
MERGE (n:Person {id:$id})
  ON CREATE SET n.created = timestamp()
  ON MATCH  SET n.lastSeen = timestamp()
```

Нюансы MERGE (важно!):
- **Атомарен по всему паттерну**: или весь матчится, или весь создаётся.
- Не работает с `null` в свойствах (`MERGE ... {age: null}` → ошибка).
- Поддерживает map-параметры, но **только через явное указание полей**, не
  через `$props` (как в CREATE).
- При конкурентных UPDATE гарантирует только **существование**, но не
  уникальность — для уникальности нужен unique constraint.
- С unique constraint требует **ровно одно** совпадение, иначе конфликт
  (`conflicting matches`).

### SET — обновление
```cypher
SET n.name = 'Andy'
SET n = {name:'Andy', age:36}                     -- заменить/дополнить все ключи
SET n:Person:Employee                             -- добавить лейблы
SET r += {since:2000}                             -- merge-map (только новые ключи)
```

### REMOVE
```cypher
REMOVE n:Person                                   -- убрать лейбл
REMOVE n.age                                      -- убрать свойство
```

### DELETE / DETACH DELETE
```cypher
DELETE n                          -- узел: ошибка, если есть связи
DETACH DELETE n                   -- узел + все его связи
DELETE r                          -- только связь
```

### FOREACH
```cypher
FOREACH (x IN [1,2,3] | CREATE (:Num {v:x}))
```

---

## 5. Проекция: RETURN / WITH / UNWIND

### RETURN
```cypher
RETURN n                                   -- узел
RETURN n.name                              -- только свойство (быстрее)
RETURN a, b, type(r)                       -- несколько выражений
RETURN *                                   -- все найденные переменные
RETURN DISTINCT b                          -- уникальные строки
RETURN count(n) AS total                   -- агрегат с alias через AS
```

### WITH — «конвейер» между частями запроса
Передаёт результат дальше как новый набор связываний. Используется для
группировки, фильтрации посередине, агрегации.
```cypher
MATCH (p:Person)-[:KNOWS]->(f)
WITH p, collect(f.name) AS friends
WHERE size(friends) >= 3
RETURN p.name, friends
```

### UNWIND — раскрыть список в строки
```cypher
UNWIND [1,2,3] AS x RETURN x          -- три отдельные строки
UNWIND $rows AS row CREATE (:Item {id:row.id})
```

---

## 6. Функции и выражения (наиболее частые)

- Агрегация: `count(n)`, `count(DISTINCT n)`, `sum()`, `avg()`, `min()`,
  `max()`, `collect()`, `size()`
- Строки: `toUpper`, `toLower`, `trim`, `substring`, `replace`, `split`,
  `length`
- Числа: `abs`, `round`, `ceil`, `floor`, `rand`
- Списки: `range(1,10)`, `size(l)`, `head/last`, `tail/l`，`[x IN l WHERE ...]` (list comprehension),
  `reduce(acc=0, x IN l | acc + x)`
- Узлы/отношения: `id(n)`, `labels(n)`, `keys(n)`, `type(r)`, `properties(n)`,
  `nodes(p)`, `relationships(p)`, `length(p)`
- Дата/время: `date()`, `datetime()`, `timestamp()`
- Coalesce/null-safe: `coalesce(n.name, 'n/a')`

Операторы сравнения и арифметики стандартные: `+ - * / %`, `= <> < <= > >=`.

`null` заразителен: `null = true → null`, `null AND true → null`. Фильтр
по WHERE не пропускает `null`-результаты (считает их «ложью»).

---

## 7. Set-операции и подзапросы

```cypher
MATCH (a:Person) RETURN a.name AS name
UNION                                          -- убирает дубли
MATCH (b:Movie)  RETURN b.title AS name

MATCH (b:Movie)  RETURN b.title AS name
UNION ALL                                      -- оставляет дубли

CALL {                                         -- подзапрос с собственной областью видимости
  MATCH (p:Person) RETURN p
  UNION
  MATCH (c:City)  RETURN c
}
```

`CALL { ... } IN TRANSACTIONS` — выполнение подзапроса порциями (для
больших импортов).

---

## 8. Параметры и `$`

```cypher
:param name => 'Andy'          -- интерактивно в браузере (cypher-shell/Neo4j Browser)

MATCH (n:Person {name:$name}) RETURN n
CREATE (n:Person $props)        -- map-параметр (ТОЛЬКО в CREATE)
```

> В `MERGE` map-параметр **не** подставляется автоматически — перечисляйте
> поля явно: `MERGE (n:P {name:$p.name, id:$p.id})`.

---

## 9. Администрирование и индексы (минимально)

```cypher
CREATE INDEX Person_name  FOR (n:Person)  ON (n.name);
CREATE CONSTRAINT FOR (n:Person) REQUIRE n.email IS UNIQUE;   -- уникальность
DROP INDEX Person_name;
DROP CONSTRAINT ... name IS UNIQUE;

SHOW INDEXES;
SHOW CONSTRAINTS;
```

Подсказки планировщику (использовать осторожно):
`USING INDEX n:Person(name)`, `USING SCAN n:Person`,
`USING JOIN ON ...`.

---

## 10. Важные нюансы (топ «наступать не стоит»)

1. **MATCH на связанный узел требует явного `MATCH` второй стороны.**
   Нельзя написать `CREATE (a)-[:X]->(b)` без предварительного получения
   `a` и `b` (например, через `MATCH`) — иначе `b` будет пустым узлом.

2. **`MERGE` без bound-узлов на отношениях** создаёт каждый раз новые
   узлы. Для отношения хотя бы один конец должен быть уже связан.

3. **`MERGE` с unique constraint требует ровно одно совпадение.**
   Partial-match или conflicting-match приведут к ошибке, даже если узел
   «по смыслу» подходит. Решение: матчить минимум, дозаполнять через `SET`.

4. **Null в WHERE — это «неправда».** Любое сравнение с `null` даёт `null`
   и строка отбрасывается. Для проверки «свойство есть» используйте
   `IS NOT NULL`.

5. **Пропущенные свойства при сравнении.** `WHERE n.belt = 'white'` НЕ
   вернёт узлы без `belt`. Чтобы включить «нет пояса»: добавлять
   `OR n.belt IS NULL`.

6. **DETACH DELETE vs DELETE.** Всегда уточняйте: одно `DELETE n` при
   наличии связей упадёт.

7. **`shortestPath` требует верхнюю границу длины** (`[*..15]`), без неё
   не сработает.

8. **Ноль-ловые пути.** `-[*0..3]-` допускает `a == b`. Следите за
   «лишними» self-match'ами.

9. **WHERE ≠ «фильтр после MATCH».** Это часть паттерна — двигает
   предикат в нужный `MATCH`, иначе меняется план и результаты.

10. **Подзапросы `CALL { ... }` ограничены по scope.** Переменные
    изнутри наружу не видны; переменные снаружи — видны. То же правило
    действует для `EXISTS { ... }`.

11. **`collect()` без `DISTINCT` оставляет дубли.** Для уникальных списков
    сначала `WITH ... DISTINCT` или `DISTINCT` внутри агрегата (где
    поддерживается).

12. **`delete` не каскадирует.** Удаление узла-«хаба» превратит
    связи-«висящие края» в невалидные (или упадёт, если есть
    constraints на relationship).

13. **`id(n)` — внутренний id, переиспользуется** после удаления. Не
    использовать как бизнес-ключ. Лучше заводить своё свойство с unique
    constraint.

14. **Регистр строковых операций.** `STARTS WITH` / `CONTAINS` /
    `ENDS WITH` — **case-sensitive**. Для нечувствительности — regex
    `(?i)` или `toLower(...)`.

15. **Параметры — защита от Cypher-injection.** Пользовательский ввод
    всегда через `$`.

---

## 11. Шпаргалка «как прочитать запрос»

Обычный порядок клауз:
```
[USE graph]
[OPTIONAL] MATCH ...        -- найти что-то
[WHERE ...]
[WITH ... [WHERE ...]]
[OPTIONAL] MATCH ...
[WHERE ...]
[WITH ... AS ... [ORDER BY ...] [SKIP n] [LIMIT n]]
[CREATE | MERGE | SET | REMOVE | DELETE | DETACH DELETE]
RETURN ... [ORDER BY ...] [SKIP n] [LIMIT n]
[UNION | UNION ALL]
```

Запрос всегда заканчивается на **RETURN** или пишется в **CALL** /
вызывается как процедура.
