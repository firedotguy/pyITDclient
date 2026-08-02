"""Правило слоев: core и api ничего не знают о моделях

core   - транспорт, конфиг, авторизация, лимиты, базовая моделька и склейка с pydantic
api    - декларации эндпоинтов
models - модели предметной области, им можно импортировать core и api

Циклы вида "модель -> клиент -> модель" появлялись именно из-за нарушения этого правила,
поэтому проверяем структурно, а не на глаз.
"""

from ast import AST, ClassDef, If, ImportFrom, Name, parse, walk
from pathlib import Path

import pytest

ITD = Path(__file__).parent.parent / 'itd'
CORE = sorted((ITD / 'core').glob('*.py'))
API = sorted((ITD / 'api').glob('*.py'))


def _is_type_checking(node: AST) -> bool:
    return isinstance(node, If) and isinstance(node.test, Name) and node.test.id == 'TYPE_CHECKING'


def module_level_imports(path: Path) -> list[str]:
    """Импорты, которые выполняются при импорте модуля: без TYPE_CHECKING и без тел функций"""
    imports = []

    def collect(body: list):
        for node in body:
            if isinstance(node, ImportFrom) and node.module:
                imports.append(node.module)
            elif isinstance(node, If) and not _is_type_checking(node):
                collect(node.body + node.orelse)
            elif isinstance(node, ClassDef):
                collect(node.body)  # тела методов пропускаем: там импорты осознанно ленивые

    collect(parse(path.read_text(encoding='utf-8')).body)
    return imports


def runtime_imports(path: Path) -> list[str]:
    """Все импорты, кроме TYPE_CHECKING - включая ленивые внутри функций"""
    tree = parse(path.read_text(encoding='utf-8'))
    type_only = {node for parent in walk(tree) if _is_type_checking(parent) for node in walk(parent)}
    return [node.module for node in walk(tree) if isinstance(node, ImportFrom) and node.module and node not in type_only]


@pytest.mark.parametrize('path', CORE + API, ids=lambda p: f'{p.parent.name}/{p.name}')
def test_layer_does_not_import_models_on_import(path: Path):
    assert [i for i in module_level_imports(path) if i.startswith('itd.models')] == []


@pytest.mark.parametrize('path', API, ids=lambda p: p.name)
def test_api_does_not_touch_models_at_all(path: Path):
    """Эндпоинт принимает и отдает dict, поэтому моделей в api нет даже лениво"""
    assert [i for i in runtime_imports(path) if i.startswith('itd.models')] == []


def test_core_imports_models_only_lazily():
    """Если core все же нужна модель (Client.search и компания), то только импортом внутри метода"""
    lazy = {path.name for path in CORE if any(i.startswith('itd.models') for i in runtime_imports(path))}
    assert lazy == {'client.py'}, 'появился новый модуль core, зависящий от моделей - проверь, точно ли это нужно'


def test_package_root_has_only_facade():
    """В корне пакета остаются только фасад и общие типы"""
    assert sorted(p.name for p in ITD.glob('*.py')) == ['__init__.py', 'enums.py', 'exceptions.py']
