# Enums

### RateLimitMode
Режим анти-рейтлимита.

 - `RateLimitMode.NO`: 0 сек - для простых скриптов.
 - `RateLimitMode.MIN`: Небольшие задержки (0 сек для обычных запросов) - для кастомных клиентов или маленьких скриптов.
 - `RateLimitMode.MID`: Средние задержки (0.2 сек для обычных запросов) - для обычных скриптов.
 - `RateLimitMode.MAX`: Большие задержки (0.4 сек для обычных запросов) - для больших ботов, парсеров.

### DebugResponseMode
Режим показа ответов сервера.

 - `DebugResponseMode.NO`: Не показывать ответ.
 - `DebugResponseMode.BEFORE`: Показывать ответ до обработки (сырой).
 - `DebugResponseMode.AFTER`: Показывать ответ после обработки (если при обработке возникла ошибка, ответ не выведется).
 - `DebugResponseMode.KEYS`: Показывать только ключи ответа (после обработки).

### ParseMode
 Режим парсинга.
 
 - `ParseMode.NO`: Выключить парсинг.
 - `ParseMode.MARKDOWN`: Markdown парсинг.
 - `ParseMode.HTML`: HTML парсинг.

### AuthLevel
Уровень авторизации.

 - `AuthLevel.NO`: Без авторизации.
 - `AuthLevel.ACCESS`: access токен.
 - `AuthLevel.REFRESH`: refresh токен.

### PostsTab
Вкладка постов.

 - `PostsTab.POPULAR`: Обычная лента постов.
 - `PostsTab.FOLLOWING`: Лента постов от авторов, на которых вы подписаны.
 - `PostsTab.CLAN`: Лента постов от авторов, у которых одинаковый с вами клан.

### UserPostSorting
Режим сортировки постов пользователя.

 - `UserPostSorting.NEW`: Сортировка постов по дате создания.
 - `UserPostSorting.POPULAR`: Сортировка постов по количеству лайков.

### AccessType
Уровень доступа.

 - `AccessType.NOBODY`: Никто.
 - `AccessType.MUTUAL`: Взаимные подписки (вы подписаны на пользователя и он подписан на вас).
 - `AccessType.FOLLOWERS`: Подписчики.
 - `AccessType.EVERYONE`: Все.

### ReportReason
Причина жалобы.

 - `ReportReason.SPAM`: Спам или нежелательный контент.
 - `ReportReason.VIOLENCE`: Насилие или опасные действия.
 - `ReportReason.HATE`: Ненависть или травля.
 - `ReportReason.ADULT`: Контент для взрослых (18+).
 - `ReportReason.FRAUD`: Дезинформация или обман.
 - `ReportReason.OTHER`: Другое.

### Role
Роль пользователя.

 - `Role.USER`: Обычный пользователь.
 - `Role.ADMIN`: Администратор.

### SpanType
Тип спана.

 - `SpanType.MONOSPACE`: `Моноширный` (код).
 - `SpanType.STRIKE`: ~~Зачеркнутый~~.
 - `SpanType.BOLD`: **Жирный**.
 - `SpanType.ITALIC`: *Курсив*.
 - `SpanType.UNDERLINE`: <u>Подчеркнутый</u>.
 - `SpanType.HASHTAG`: Хэштэг. Заполняется самим ИТД при создании поста.
 - `SpanType.LINK`: Ссылка. При создании надо указать `url`.
 - `SpanType.QUOTE`: <q>Цитата</q>.
 - `SpanType.MENTION`: Упоминание. ~~Заполняется~~ Должно заполняться самим ИТД при создании поста.

!!! warning
    Цитаты (`SpanType.QUOTE`) не добавлены на бэкенд (есть только на клиенте).
