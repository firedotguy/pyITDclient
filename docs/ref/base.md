# ITDBaseModel

!!! warning "WIP"
    Страница не доделана.

### Аттрибуты
#### client <span class="mdx-badge"><span class="mdx-badge__icon">client</span><span class="mdx-badge__text">Client</span></span>
Установленный по умолчанию клиент.  
Почти ко всем функциям можно передать `client` как именованный параметр. Если он не задан, берется дефолтный `self.client`.

---

<a id="refresh"></a>
## Обновить
```py
base.refresh()
```

### Ошибки
 - `NotFoundError` - объект не найден

---

## ITDlist

### Аттрибуты
#### client <span class="mdx-badge"><span class="mdx-badge__icon">client</span><span class="mdx-badge__text">Client</span></span>
Установленный по умолчанию клиент.  
Почти ко всем функциям можно передать `client` как именованный параметр. Если он не задан, берется дефолтный `self.client`.

#### has_more <span class="mdx-badge"><span class="mdx-badge__icon">:material-toggle-switch:</span><span class="mdx-badge__text">bool</span></span>
Есть ли еще не загруженные объекты. Работает, только если дочерний класс переопределил `_get_has_more`.

---

## Перезагрузить
```py
base.refresh(
    count=1,
    limit=5
)
```

# TODO
