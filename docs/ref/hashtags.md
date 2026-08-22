# :material-pound: Hashtag
Хэштэг.

## Получить
```python
hashtag = Hashtag('итд')
```

### Параметры
#### name <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span> <span class="mdx-badge mdx-badge_required"><span class="mdx-badge__icon">:material-information:</span><span class="mdx-badge__text">Required</span></span>
Название хэштэга. Решетку в начале можно не убирать - `Hashtag('#итд')` то же самое.

### :material-magnify: Поиск
```python
hashtag = Hashtag.search('итд')
```
Возвращает первый найденный хэштэг, иначе выбрасывает `NotFoundError`.

## Аттрибуты
#### id <span class="mdx-badge"><span class="mdx-badge__icon">:material-identifier:</span><span class="mdx-badge__text">UUID</span></span>
ID хэштэга.

#### name <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Название без решетки. `str(hashtag)` вернет с решеткой.

#### posts_count <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Количество постов с этим хэштэгом. `int(hashtag)` вернет его же.

#### posts <span class="mdx-badge"><span class="mdx-badge__icon">:material-code-brackets: :material-post:</span><span class="mdx-badge__text">[HashtagPosts](posts.md#hashtagposts)</span></span> <span class="mdx-badge mdx-badge_alias"><span class="mdx-badge__icon">property</span></span>
Посты с этим хэштэгом.

## Ошибки при получении
 - `TooLargeError` - слишком длинное название.
 - `NotFoundError` - хэштэга не существует.
 - `ValidationError` - ошибка валидации.

---

# :material-code-brackets: :material-pound: Hashtags
Список хэштэгов: тренды или результат поиска.

## :fontawesome-solid-arrow-trend-up: Тренды
```python
hashtags = Hashtags()
```

### Параметры
#### limit <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Сколько хэштэгов загрузить. По умолчанию `10`.

## :material-magnify: Поиск
```python
hashtags = Hashtags.search('итд', limit=10)
```
или
```python
hashtags = Hashtags('итд')
```

## :material-refresh: Перезагрузить
```python
hashtags.load(limit=10)
```
Очищает список и загружает заново - тем же запросом, что и при создании (тренды или поиск, смотря с чем создавали).

## Пустой список
```python
hashtags = Hashtags.empty()
```
Ничего не загружает - нужно, когда список надо создать заранее.

## Ошибки при получении
 - `ValidationError` - ошибка валидации (например, из-за слишком большого лимита).
