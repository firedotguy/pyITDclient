# :material-bell: Notification

!!! note
    В билиотеке есть пока еще нерабочие типы уведомлений, такие как `follow_request`, `mention`, `comment_like` и др. Все эти типы взяты из [декомпилированного фронтенда](https://github.com/itd-sdk/itd-frontend), то есть на оф. клиенте они также работают. Ождиается только появление на бэкенде.

## Аттрибуты

#### id <span class="mdx-badge"><span class="mdx-badge__icon">:material-identifier:</span><span class="mdx-badge__text">UUID</span></span>
ID уведомления.

#### type <span class="mdx-badge"><span class="mdx-badge__icon">:material-form-select:</span><span class="mdx-badge__text">[NotificationType](enums.md#notificationtype)</span></span>
Тип уведомления (например лайк подписка и тд).

#### target_type <span class="mdx-badge"><span class="mdx-badge__icon">:material-form-select:</span><span class="mdx-badge__text">[NotificationTargetType](enums.md#notificationtargettype)</span></span>
Тип цели (например пост). `None`, если цель - пользователь (например при подписках).

#### target_id <span class="mdx-badge"><span class="mdx-badge__icon">:material-identifier:</span><span class="mdx-badge__text">UUID</span></span>
ID цели. `None`, если цель - пользователь (например при подписках).

#### preview <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Описание уведолмения.

 - У лайков и репостов содержание поста.
 - У комментариев и ответов содержание комментария.
 - У подписок и заявок `None`.

#### is_read <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Прочитано ли уведомление.

#### read_at <span class="mdx-badge"><span class="mdx-badge__icon">:material-calendar:</span><span class="mdx-badge__text">datetime</span></span>
Дата прочетния уведомления. `None`, если `is_read` == `False`.

#### created_at <span class="mdx-badge"><span class="mdx-badge__icon">:material-calendar:</span><span class="mdx-badge__text">datetime</span></span>
Дата создания уведомления.

#### actor <span class="mdx-badge"><span class="mdx-badge__icon">:fontawesome-solid-user:</span><span class="mdx-badge__text">[User](users.md#user)</span></span>
Актор.

!!! note "glossary"
    Актор (англ. actor) - "создатель" уведомления - комментатор, репостер, подписчик и тд.

#### sound <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли воспроизвести уведомление со звуком. Работает только при стриме уведомлений. Вычисляется на основе настроек уведомлений пользователя.


## :material-eye: Прочитать
```py
notification.read()
```

### Ошибки
 - `NotFoundError` - уведомление не найдено, уже прочитано или не принадлежит клиенту.

## Получить текст
```py
notification.get_text(
    avatar=False
)
```
Получить текст уведомления (вида `fdg оценил(а) ваш комментарий`) (не API метод, сделано для удобства, создается на основе `type`).

### Параметры
#### avatar <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли добавлять аватар актора. По умолчанию `False`.

## Получить цвет
```py
color = notification.get_color()
```
Получить цвет уведомления (`blue`, `green`, `red` или `purple`) (не API метод, сделано для удобства, создается на основе `type`).

---

# :material-code-brackets: :material-bell: Уведомления

 - [x] has_more
 - [ ] total

## Получить
```py
notifications = Notifications()
```

## Стрим уведолмений
```py
for notification in notifications.stream():
    pass
```

## Стрим уведомлений в фоне
```py
thread = notifications.stream_bg(
    daemon=True
)
```

### Параметры
#### daemon <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Влючен ли `daemon` для thread'а.

Чтобы получать уведомления из фона, установите каллбэки.

## Остановка фонового стрима
```py
notifications.stop_stream()
```

## Каллбэки

### Общий
=== "Через декоратор"
    ```py
    @notifications.on()
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_notification = lambda notification: notification.read()
    ```

### Лайки (на постах)
=== "Через декоратор"
    ```py
    @notifications.on("like")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_like = lambda notification: notification.read()
    ```

### Комментарии
=== "Через декоратор"
    ```py
    @notifications.on("comment")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_comment = lambda notification: notification.read()
    ```

### Ответы
=== "Через декоратор"
    ```py
    @notifications.on("reply")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_reply = lambda notification: notification.read()
    ```

### Репосты
=== "Через декоратор"
    ```py
    @notifications.on("repost")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_repost = lambda notification: notification.read()
    ```

### Упоминания (в постах)
=== "Через декоратор"
    ```py
    @notifications.on("mention")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_mention = lambda notification: notification.read()
    ```

### Подписчики
=== "Через декоратор"
    ```py
    @notifications.on("follow")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_follow = lambda notification: notification.read()
    ```

### Запросы на подписку
=== "Через декоратор"
    ```py
    @notifications.on("follow_request")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_follow_request = lambda notification: notification.read()
    ```

### Принятие запросов на подписку
=== "Через декоратор"
    ```py
    @notifications.on("follow_accepted")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_follow_accepted = lambda notification: notification.read()
    ```

### Лайки комментариев
=== "Через декоратор"
    ```py
    @notifications.on("comment_like")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_comment_like = lambda notification: notification.read()
    ```

### Упоминания (в комментариях)
=== "Через декоратор"
    ```py
    @notifications.on("comment_mention")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_comment_mention = lambda notification: notification.read()
    ```
### Посты на стене
=== "Через декоратор"
    ```py
    @notifications.on("wall_post")
    def callback(notification: Notification):
        notification.read()
    ```
=== "Через переопределение"
    ```py
    notifications.on_wall_post = lambda notification: notification.read()
    ```
