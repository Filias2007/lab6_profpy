# Система обліку та обробки замовлень інтернет-магазину (LAB_06)

Даний проєкт є лабораторною роботою №6 з дисципліни "Автоматизоване тестування Python-програм". Проєкт реалізує доменну логіку інтернет-магазину та містить повний тестовий набір (unit та integration tests) з використанням фреймворку `pytest`.

## 📁 Структура проєкту

```text
LAB_05/
├── pyproject.toml
├── README.md
├── src/
│   └── shop/
│       ├── __init__.py
│       ├── exceptions.py
│       ├── models.py
│       ├── value_objects.py
│       ├── services.py
│       ├── repositories.py
│       ├── exporters.py
│       └── config.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── test_models.py
    │   ├── test_value_objects.py
    │   ├── test_services.py
    │   ├── test_repositories.py
    │   └── test_config.py
    └── integration/
        └── test_import_export_pipeline.py