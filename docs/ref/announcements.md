# :material-bullhorn: Announcement
Анонс - плашка, которую ИТД показывает в официальном клиенте (обновление, новость итд).

## Аттрибуты
#### id <span class="mdx-badge"><span class="mdx-badge__icon">:material-identifier:</span><span class="mdx-badge__text">str</span></span>
ID анонса. Тут не UUID, а строка вроде `update-2-8`.

#### title <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Заголовок. `str(announcement)` вернет его же.

#### description <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Описание. `None`, если его нет.

#### additional_text <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Дополнительный текст под описанием. `None`, если его нет.

#### image <span class="mdx-badge"><span class="mdx-badge__icon">:material-image:</span><span class="mdx-badge__text">AnnouncementImage</span></span>
Картинка анонса: `url`, `width` и `height`. `None`, если картинки нет.

#### buttons <span class="mdx-badge"><span class="mdx-badge__icon">:material-code-brackets: :material-gesture-tap-button:</span><span class="mdx-badge__text">list[[AnnouncementButton](#announcementbutton)]</span></span>
Кнопки анонса.

## :material-eye: Отметить прочитанным
```python
announcement.read()
```
Запоминает ID в файле сессии, чтобы [Announcements](#announcements) больше его не показывали. В API ничего не уходит - это чисто локально, поэтому нужен клиент, созданный через [from_file](client.md) (иначе `AssertionError`).

---

# :material-gesture-tap-button: AnnouncementButton
Кнопка анонса.

## Аттрибуты
#### title <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Текст кнопки. `str(button)` вернет его же.

#### style <span class="mdx-badge"><span class="mdx-badge__icon">:material-form-select:</span><span class="mdx-badge__text">[AnnouncementButtonStyle](enums.md#announcementbuttonstyle)</span></span>
Стиль кнопки.

#### action <span class="mdx-badge"><span class="mdx-badge__icon">:material-gesture-tap:</span><span class="mdx-badge__text">AnnouncementButtonAction</span></span>
Что кнопка делает: `type` ([AnnouncementButtonType](enums.md#announcementbuttontype)) и `url` (`None` для `DISMISS`).

---

# :material-code-brackets: :material-bullhorn: Announcements
Список актуальных анонсов.

## Получить
```python
announcements = Announcements()
```

### Параметры
#### hide_seen <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Убирать ли анонсы, которые уже отметили через [read()](#announcement). По умолчанию `True`. Работает только с клиентом из файла сессии.

## Первый анонс
```python
announcement = Announcements().get()
```
Возвращает первый анонс или `None`, если анонсов нет.

## :material-refresh: Перезагрузить
```python
announcements.load(hide_seen=True)
```

## Пустой список
```python
announcements = Announcements.empty()
```
