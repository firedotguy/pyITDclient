# Концепция

## Анти-рейт-лимит
Если вызываемая функция уже использовалась, автоматически включается ожидание пердустановленных задержек.

### Псевдокод
```python
if функция есть в предустановленных значениях: # (1)
    задержка = предустановленное значение
elif rate_limit_mode == RateLimitMode.NO:
    задержка = 0
elif any((задержка_функции_min, задержка_функции_mid, задержка_функции_max)):
    задержка = eval(f'задержка_{min or mid or max}') # (2)
else:
    задержка = задержка_для_обычных_запросов # (3)

if datetime.now() - задержка < время_последнего_вызова_функции:
    задержка -= datetime.now() - время_последнего_вызова_функции # (4)
    l.debug('anti rate limit on %s; wait %ss', имя_функции, задержка)
    sleep(задержка)
время_последнего_вызова_функции = datetime.now()
```

1. см. [rate_limit_actions](config.md#rate_limit_actions-dictstr-float)
2. взависимости от установленного значения [rate_limit](config.md#rate_limit-ratelimitmode)
3. см. [rate_limit_default](config.md#rate_limit_default-float)
4. отнимается уже прошедшее время (если функция вызвана 10сек назад, то ждать только 5сек вместо 15сек)

## Авто-загрузка
При инициализации модели она не загружается из API.  
В базовой модели стоит метод `__getattribute__`, перехватывающий попытку получения значений, и автоматически загружает данные, если они еще не загружены.  
Можно выключить в конфиге (см. [auto_load](config.md#auto_load-bool)) (тогда нужно будет вручную вызывать `refresh`).

### Пример триггера
```python
post = Post('b6f9e0c6-f6bc-4b40-9906-8735ec76368d')
post.content
```

### Псевдокод
```python
if (
    name.startswith('_') or # приватный аттрибут
    name == 'client' or
    not self._refreshable or # (1)
    self.client.config.auto_load or # (3)
    callable(value) or # (2)
    (self.client.config.load_comments_from_post and isinstane(self, Post) and isinstance(value, Comment)) # (4)
):
    return value

if isinstance(value, FieldInfo) or (isinstance(value, ITDBaseModel) and value._load_with_parent and not value._loaded): # тип - pydantic field или модель
    l.info('refresh %s (caused by %s)', self.__class__.__name__, name)
    self.refresh()
    return object.__getattribute__(self, name)

return value
```

1. Пропуск необновляемых моделей, например уведомление (можно получить только из списка)
2. Пропуск функций, чтобы не обновлять пользователя при действиях (например для post.like() необязательно получать сам пост)
3. см. [auto_load](config.md#auto_load-bool)
4. см. [load_comments_from_post](config.md#load_comments_from_post-bool)

## Авто-дозагрузка списков
Дозагрузка листов при итерации или получении индекса.  
В базовой модели стоят методы `__getitem__` и `__next__`, перехватывающие попытку получения значения которого пока не существует.  
Можно выключить в конфиге (см. [load_on_getitem](config.md#load_on_getitem-all-batchint-all-batch))
```python
posts = Posts()
posts[0] # равносильно posts.load(1)
for post in posts: # равносильно for post in posts.load_all():
    pass
```
После получения значения оно сохраняется, и при повторном получении индекса повторная загрузка не произойдет. Также и с итерацией - после ее окончания весь список будет загружен.

## Авто-ожидание рейт лимитов
При ошибке `RateLimit` автоматически ожидает указанное время и повторяет запрос.

### Псевдокод
```python
while True:
    try:
        return функция()
    except RateLimitError as e:
        l.info('rate limit on %s; wait %ss', имя_функции, e.время_ожидания_из_API or 10) # (1)
        sleep(e.время_ожидания_из_API or 10)
```

1. Если рейт-лимит на уровне метода, в ответе приходит необходимое время ожидания (`json['error']['retryAfter']`). Также бывает рейт-лимит на уровне всех запросов (скорее всего по IP), в таком случае отдает только {'error': 'Too Many Requests'}