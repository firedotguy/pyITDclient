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
Прочитано ли уведолмение.

#### read_at <span class="mdx-badge"><span class="mdx-badge__icon">:material-calendar:</span><span class="mdx-badge__text">datetime</span></span>
Дата прочетния уведолмения. `None`, если `is_read` == `False`.

#### created_at <span class="mdx-badge"><span class="mdx-badge__icon">:material-calendar:</span><span class="mdx-badge__text">datetime</span></span>
Дата создания уведолмения.

#### actor <span class="mdx-badge"><span class="mdx-badge__icon">:fontawesome-solid-user:</span><span class="mdx-badge__text">[User](users.md#user)</span></span>
Актор.

!!! note "glossary"
    Актор (англ. actor) - "создатель" уведомления - комментатор, репостер, подписчик и тд.

#### sound <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли воспроизвести уведолмение со звуком. Работает только при стриме уведомлений. Вычисляется на основе настроек уведолмений пользователя.


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
Нужно ли добавлять аватар актора. По умолчанию False.

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
#### daуmon <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Влючен ли `daemon` для thread'а.

Чтобы получать уведомления из фона, утсановите каллбэки.

## Остановка фонового стрима
```py
notifications.stop_stream()
```

## Каллбэки

### Общий
```py
notifications.on_notification = lambda notification: notification.read()
```

### Лайки (на постах)
```py
notifications.on_like = lambda notification: notification.read()
```

### Комментарии
```py
notifications.on_comment = lambda notification: notification.read()
```

### Ответы
```py
notifications.on_reply = lambda notification: notification.read()
```

### Репосты
```py
notifications.on_repost = lambda notification: notification.read()
```

### Упоминания (в постах)
```py
notifications.on_mention = lambda notification: notification.read()
```

### Подписчики
```py
notifications.on_follow = lambda notification: notification.read()
```

### Запросы на подписку
```py
notifications.on_follow_request = lambda notification: notification.read()
```

### Принятие запросов на подписку
```py
notifications.on_follow_accepted = lambda notification: notification.read()
```

### Лайки комментариев
```py
notifications.on_comment_like = lambda notification: notification.read()
```

### Упоминания (в комментариях)
```py
notifications.comment_mention = lambda notification: notification.read()
```

### Посты на стене
```py
notifications.on_wall_post = lambda notification: notification.read()
```
