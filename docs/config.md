# :fontawesome-solid-gear: Конфигурация

У `ITDClient` можно настраивать конфигурацию:

```python
from itd import ITDClient, ITDConfig

config = ITDConfig()

ITDClient('xxx', config=config)
```

## Параметры

#### rate_limit <span class="mdx-badge"><span class="mdx-badge__icon">:material-form-select:</span><span class="mdx-badge__text">[RateLimitMode](ref/enums.md#ratelimitmode)</span></span>
Устанавливает дефолтные значения задержек.
<!-- Также планируется режим `SMART`, который будет выставлять динамическую задержку (например при первых трех комментариях не делать задержку). -->
По умолчанию `RateLimitMode.MID`.

#### rate_limit_default <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">float</span></span>
Задержка для обычных запросов (overrides rate_limit_mode). Значение по умолчанию зависит от [rate_limit](#rate_limit-ratelimitmode).

#### rate_limit_actions <span class="mdx-badge"><span class="mdx-badge__icon">:material-code-braces: :material-text:: :octicons-number-16:</span><span class="mdx-badge__text">dict[str, float]</span></span>
Кастомная задержка для каждого вида запроса (например `get_user`). Названия фукнций можно посмотреть в `itd.api`. Можно использовать, если ваш скрипт повторяет одно и тоже действие (например, постоянно комментирует).

!!! example
    ```python
    {'get_me': 5, 'get_followers': 6, 'add_comment': 15.4}
    ```

#### is_default <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Сделать ли клиент дефолтным по умолчанию. По умолчанию дефолтным становится первый инициализированный клиент.

#### userposts_add_pinned_post <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Добавлять ли закрепленный пост при получении постов пользователя (`UserPosts`). Для этого потребуется отдельный запрос. По умолчанию `True`.

#### auto_load <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли автоматически загружать данные при попытке получение (перехват в `__getattribute__`). Если выключено, то для получения данных придется перед получением писать `obj.refresh()`. По умолчанию `True`.

#### load_on_getitem <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | ALL | BATCH</span><span class="mdx-badge__text">int | All | Batch</span></span>
Количество загружаемых объектов при попытке получить еще не загруженный элемент списка (например `Posts()[10]`). Может выдать `AttributeError`, если даже после загрузки всех объектов количество меньше желаемого индекса, или если известно общее количество объектов и индекс будет больше него. По умолчанию `1`. `All` - загрузить все. `Batch` - загрузить следующий батч (следующий по курсору). `None` - выключить авто загрузку.

!!! example
    ```python
    config.load_on_getitem = 1
    posts[5]
    len(posts) # 6

    config.load_on_getitem = 5
    posts[6]
    len(posts) # 12

    config.load_on_getitem = ALL
    posts[7]
    len(posts) # 50

    posts.clear()
    config.load_on_getitem = None
    posts[8] # AttributeError
    ```

#### load_on_iter <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16: | ALL | BATCH</span><span class="mdx-badge__text">int | All | Batch</span></span>
Количество загружаемых объектов при итерации списка (например `for post in Posts()`) Если вы итеририуете сразу весь список без `break`, то этот пратаметр особо не играет роли. По умолчанию `BATCH`. `All` - загружать все. `Batch` - загружать следующий батч. `None` - выключить авто загрузку.

#### force_load_lists <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Загружать список, даже если `has_more = False`. Может уйти в бесконечный цикл при итерации. По умолчанию `False`.

#### debug_response <span class="mdx-badge"><span class="mdx-badge__icon">:material-form-select:</span><span class="mdx-badge__text">[DebugResponseMode](ref/enums.md#debugresponsemode)</span></span>
Режим показа сырых данных ответа API (response). Для работы должен быть установлен логгер с режимом `DEBUG`.

!!! warning
    Может раскрыть ваши ключи (при `refresh_auth` в терминале будет виден `access_token`)
По умолчанию `DebugResponseMode.NO`.

#### timeout <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">float</span></span>
Таймаут обычного запроса. По умолчанию `30`.

#### timeout_file <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">float</span></span>
Таймаут при загрузке файла. По умолчанию `120`.

#### url <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
Базовый URL ИТД (`xn--d1ah4a.com`).

#### url_api <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
URL к API ИТД (`https://xn--d1ah4a.com/api`). Если не указан, берется из [url](#url-str).

#### user_agent <span class="mdx-badge"><span class="mdx-badge__icon">:material-text:</span><span class="mdx-badge__text">str</span></span>
User-Agent, под которым обращатся к API ИТД. Если вы делаете свой клиент, можете поставить агент как его имя. По умолчанию стоит дефолтный браузерный user-agent.

#### solve_challenge <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли проходить JS-challenge (защита от скриптов). Иногда включается при запросах к API. Если выключена, скрипт может упасть с ошибкой `fail to parse json`.

#### load_comments_from_post <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли брать комментарии из уже полученного поста (ИТД дает 3-4 комментария при получении поста). При загрузке следующего батча комментарии могут дублироваться. По умолчанию `False`.

#### parse_mode <span class="mdx-badge"><span class="mdx-badge__icon">:simple-markdown:</span><span class="mdx-badge__text">[ParseMode](ref/enums.md#parsemode)</span></span>
Режим парсинга (автоматически генерирует `spans` при создании или редактировании постов). По умолчанию `ParseMode.NO`.

#### retry_enabled <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли повторять запрос при ошибке сети или рейт лимите. По умолчанию `True`.

#### retry_delay <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">float</span></span>
Задержка перед следующим повтором запроса.

#### retry_max_retries <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Максимальное количество попыток повторов запроса. По умолчанию `None`. `None` - без лимита.

#### retry_exceptions <span class="mdx-badge"><span class="mdx-badge__icon">:material-code-brackets: :material-close-circle:</span><span class="mdx-badge__text">list[type[Exception]] | tuple[type[Exception]]</span></span>
Список ошибок, при которых нужно повторить запрос. По умолчанию `RateLimitError`, `InternalError` и стандартные ошибки из `requests` (`RequestException`).

#### bypass_auth_level <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Bypass пре-валидации на проверку уровня авторизации. По умолчанию `False`.
!!! note
    В sdk существует 3 уровня авторизации:

     - `NO`: **Без авторизации** - доступен поиск
     - `ACCESS`: **Access-токен** - доступно большинство всех возможностей
     - `REFRESH`: **Refresh-token** - то же, что и `ACCESS` + обновление токена и выход

    Если вы попытаетесь выполнить запрос который выше по масти, будет вызвана ошибка `InsufficientAuthLevelError`.  
    Чтобы этой ошибки не было, нужно поставить `bypass_auth_level=True`. Тогда будет вызвана стандартная ошибка от самого ИТД (`RefreshTokenMissingError` / `UnauthorizedError` или похожие)

!!! warning
    При вызове ошибок `RefreshTokenMissingError` и `UnauthorizedError` может попросить оставить Issue на github. Если у вас включен `bypass_auth_level`, игнорируйте эту просьбу.

#### dwell_enabled <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли включать dwell tracker для просмотров. По умолчанию `True`.

#### dwell_max_buffer <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Максимальный буффер dwell tracker`а. После переполнения буффер автоматически отпарвится на сервер и очистится. По умолчанию 20 (в точности как у оф клиента).

#### dwell_send_interval <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">float</span></span>
Задержка между запросами dwell tracker`а (через сколько секунд повторять проверку на наличие новых записей, и если есть то отправлять их на сервер). По умолчанию 2 (в точности как у оф клиента).

#### dwell_save_on_quit <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Отправлять ли несохраненные записи перед закрытием скрипта (делается через atexit). По умолчанию `True`.

#### post_update_stats <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Нужно ли обновлять статистику видимых постов. По умолчанию `False`.

#### post_update_stats_interval <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">float</span></span>
Задержка между обнолвением статистики видимых постов. По умолчанию `3`.

#### view_read_speed <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Скорость чтения (в WPM). Используется для более правдоподобного времени просмотра поста. По умолчанию `250`.

#### view_images_speed <span class="mdx-badge"><span class="mdx-badge__icon">:octicons-number-16:</span><span class="mdx-badge__text">int</span></span>
Скорость понимания картинок. Используется для более правдоподобного времени просмотра поста. По умолчанию `130`.
