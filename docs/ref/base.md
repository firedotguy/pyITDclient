# ITDBaseModel
Каждая модель наследуется от `ITDBaseModel`.

### Аттрибуты
#### client <span class="mdx-badge"><span class="mdx-badge__icon">client</span><span class="mdx-badge__text">Client</span></span>
Установленный по умолчанию клиент.

Почти ко всем функциям можно передать `client` как именованный параметр. Если он не задан, берется дефолтный `self.client`.

<a id="refresh"></a>
## Обновить
```py
base.refresh()
```

### Ошибки
 - `NotFoundError` - объект не найден

## ITDlist
Каждый список с пагинацией наследуется от `ITDlist` (например `Posts`, `Followers`, `Comments` и тд).

### Аттрибуты
#### client <span class="mdx-badge"><span class="mdx-badge__icon">client</span><span class="mdx-badge__text">Client</span></span>
Установленный по умолчанию клиент.

#### has_more <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Есть ли еще не загруженные объекты. Работает, только если дочерний класс переопределил `_get_has_more`.

#### total <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Общее количество объектов. Работает, только если дочерний класс переопределил `_get_total`.

#### cursor <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | :material-text: | :material-calendar: | None</span><span class="mdx-badge__text">int | str | datetime | None</span></span>
Следующий курсор (или страница). Тип зависит от модели (например у `LikedPosts` - `datetime`). По умолчанию обычно `0` или `None`.

## Перезагрузить
```py
objects = base.refresh(
    count=1,
    limit=5
)
```
Удаляет текущие объекты и загружает их заново.

### Параметры
#### count <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | Batch | All</span><span class="mdx-badge__text">int | BATCH | ALL</span></span>
Количество объектов для загрузки. По умолчанию количество текущих объектов.

#### limit <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | Batch</span><span class="mdx-badge__text">int | BATCH</span></span>
Лимит получения за раз. По умолчанию `BATCH` (один батч, у каждого списка он свой).

## Загрузить
```py
new_objects = base.load(
    count=10,
    limit=5
)
```
Загрузить указанное количество объектов.

### Параметры
#### count <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | Batch | All</span><span class="mdx-badge__text">int | BATCH | ALL</span></span>
Количество объектов для загрузки. По умолчанию `BATCH`.

#### limit <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | Batch</span><span class="mdx-badge__text">int | BATCH</span></span>
Лимит получения за раз. По умолчанию `BATCH`.

## Загрузить все
```py
new_objects = base.load_all(
    limit=15
)
```
Загрузить все доступные объекты. Тоже самое, что и `base.load(ALL)`

#### limit <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | Batch</span><span class="mdx-badge__text">int | BATCH</span></span>
Лимит получения за раз. По умолчанию `BATCH`.
