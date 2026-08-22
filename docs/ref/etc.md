# :material-flag: Report
Жалоба. Обычно создается не напрямую, а через объект, на который жалуетесь - [post.report()](posts.md), [comment.report()](comments.md) или [user.report()](users.md).

## Создать
```python
report = Report(
    target_id=post.id,
    target_type=ReportTargetType.POST,
    reason=ReportReason.SPAM,
    description='спамит'
)
```

### Параметры
#### target_id <span class="mdx-badge"><span class="mdx-badge__icon">:material-identifier:</span><span class="mdx-badge__text">UUID</span></span> <span class="mdx-badge mdx-badge_required"><span class="mdx-badge__icon">:material-information:</span><span class="mdx-badge__text">Required</span></span>
ID объекта, на который жалуетесь.

#### target_type <span class="mdx-badge"><span class="mdx-badge__icon">:material-form-select:</span><span class="mdx-badge__text">[ReportTargetType](enums.md#reporttargettype)</span></span> <span class="mdx-badge mdx-badge_required"><span class="mdx-badge__icon">:material-information:</span><span class="mdx-badge__text">Required</span></span>
Тип объекта.

#### reason <span class="mdx-badge"><span class="mdx-badge__icon">:material-form-select:</span><span class="mdx-badge__text">[ReportReason](enums.md#reportreason)</span></span> <span class="mdx-badge mdx-badge_required"><span class="mdx-badge__icon">:material-information:</span><span class="mdx-badge__text">Required</span></span>
Причина жалобы.

#### description <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Описание. По умолчанию пустое.

## Аттрибуты
#### id <span class="mdx-badge"><span class="mdx-badge__icon">:material-identifier:</span><span class="mdx-badge__text">UUID</span></span>
ID жалобы.

#### created_at <span class="mdx-badge"><span class="mdx-badge__icon">:material-calendar:</span><span class="mdx-badge__text">datetime</span></span>
Дата отправки.

Плюс то, с чем жалоба создавалась: `target_id`, `target_type`, `reason`, `description`.

## Ошибки
 - `AlreadyReportedError` - вы уже жаловались на этот объект.
 - `NotFoundError` - объекта не существует.
 - `ValidationError` - ошибка валидации.

---

# :material-link-variant: Portal
Портал - баннер со ссылкой, который показывается в официальном клиенте.

## Получить
```python
portal = Portal()
```
Загружается сразу при создании. Авторизация не нужна.

## Аттрибуты
#### active <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Показывается ли портал сейчас. `bool(portal)` вернет его же.

#### title <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Заголовок.

#### url <span class="mdx-badge"><span class="mdx-badge__icon">:material-link:</span><span class="mdx-badge__text">str</span></span>
Ссылка.

---

# :material-emoticon: Clan
Клан - эмодзи, по которому пользователи объединяются в группы.

## Аттрибуты
#### avatar <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Эмодзи клана. `str(clan)` вернет его же.

#### members_count <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Количество участников.

# :material-code-brackets: :material-emoticon: TopClans
Топ кланов.

```python
clans = TopClans()
```
Загружается сразу при создании. Перезагрузить - `clans.load()`, создать пустой - `TopClans.empty()`.

---

# :material-update: Apps
Версии официальных клиентов. Ведет себя как словарь, но к приложениям можно обращаться и через точку:

```python
apps = Apps()
apps.android.version
apps['android'].version
```

## Аттрибуты App
#### name <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Название приложения (оно же ключ в словаре).

#### version <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Последняя версия.

#### min_version <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Минимальная поддерживаемая версия.

#### update_url <span class="mdx-badge"><span class="mdx-badge__icon">:material-link:</span><span class="mdx-badge__text">str</span></span>
Ссылка на обновление.

#### version_tuple <span class="mdx-badge"><span class="mdx-badge__icon">:material-code-brackets: :octicons-number-16:</span><span class="mdx-badge__text">tuple[int, ...]</span></span> <span class="mdx-badge mdx-badge_alias"><span class="mdx-badge__icon">property</span></span>
Версия кортежем - чтобы сравнивать: `app.version_tuple > (2, 8, 0)`. Так же есть `min_version_tuple`.

# :material-format-list-bulleted: Changelog
Список изменений официального клиента.

```python
changelog = Changelog()
changelog[0].changes
```

## Аттрибуты Version
#### version <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Версия.

#### changes <span class="mdx-badge"><span class="mdx-badge__icon">:material-code-brackets: :material-text:</span><span class="mdx-badge__text">list[str]</span></span>
Список изменений.

#### date_str <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Дата так, как ее отдает ИТД (`13 мая`).

#### date <span class="mdx-badge"><span class="mdx-badge__icon">:material-calendar:</span><span class="mdx-badge__text">date</span></span> <span class="mdx-badge mdx-badge_alias"><span class="mdx-badge__icon">property</span></span>
Разобранная дата. Нужен экстра `date`:

```
uv add itd-sdk[date]
```

#### version_tuple <span class="mdx-badge"><span class="mdx-badge__icon">:material-code-brackets: :octicons-number-16:</span><span class="mdx-badge__text">tuple[int, ...]</span></span> <span class="mdx-badge mdx-badge_alias"><span class="mdx-badge__icon">property</span></span>
Версия кортежем.
