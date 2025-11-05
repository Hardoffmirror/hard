# Архитектура приложения

Подробное описание архитектуры PoE Currency Exchange Helper.

## Обзор

Приложение построено по модульной архитектуре с разделением на слои:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (PyQt5 UI - Overlay Window)            │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│         Business Logic Layer            │
│  (Currency Tracker, Profit Calculator)  │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│          Data Access Layer              │
│     (Database Manager, API Clients)     │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│         External Services               │
│   (poe.ninja API, PoE Trade API)        │
└─────────────────────────────────────────┘
```

## Компоненты

### 1. Presentation Layer (UI)

#### OverlayWindow (`src/ui/overlay_window.py`)
Главное окно приложения, которое отображается поверх игры.

**Ответственность:**
- Отображение прозрачного окна поверх игры
- Управление вкладками (Exchange, History, Statistics)
- Обработка пользовательских действий
- Обновление данных в реальном времени

**Ключевые методы:**
```python
init_ui()              # Инициализация интерфейса
update_data()          # Обновление всех данных
update_exchange_rates() # Обновление таблицы курсов
update_statistics()    # Обновление статистики
```

**Особенности:**
- Использует Qt Flags для создания borderless окна
- Поддерживает drag-and-drop для перемещения
- Автоматическое обновление через QTimer

#### ChartWidget (`src/ui/chart_widget.py`)
Виджет для отображения графиков и визуализаций.

**Ответственность:**
- Отображение различных типов графиков
- Переключение между видами визуализации
- Интерактивный выбор валюты

**Типы графиков:**
- Price History (история цен)
- Profitability (сравнение прибыльности)
- Trend Comparison (сравнение трендов)
- Volatility (волатильность)

### 2. Business Logic Layer

#### CurrencyTracker (`src/core/currency_tracker.py`)
Центральный компонент для отслеживания валют.

**Ответственность:**
- Периодическое получение данных о ценах
- Расчет метрик (тренды, волатильность)
- Управление состоянием данных
- Координация обновлений

**Поток работы:**
```
Start → Fetch Prices → Process Data → Calculate Metrics →
Save to DB → Update UI → Wait → Repeat
```

**Ключевые методы:**
```python
start()                    # Запуск отслеживания
fetch_prices()             # Получение цен
_calculate_profitability() # Расчет прибыльности
get_current_rates()        # Получение текущих курсов
```

#### ProfitCalculator (`src/core/profit_calculator.py`)
Калькулятор выгодности сделок.

**Ответственность:**
- Расчет прибыли от обмена
- Поиск арбитражных возможностей
- Анализ многошаговых обменов
- Определение лучшего времени для торговли

**Алгоритмы:**

1. **Расчет простого обмена:**
```
profit = (want_value - have_value) / have_value * 100
с учетом спредов buy/sell
```

2. **Поиск арбитража:**
```
Для каждой пары валют:
  Рассчитать обмен A → B
  Рассчитать обмен B → A
  Если профит > threshold:
    Добавить в список возможностей
```

3. **Многошаговый обмен:**
```
start_value → currency1 → currency2 → ... → final_value
total_profit = (final_value - start_value) / start_value * 100
```

### 3. Data Access Layer

#### DatabaseManager (`src/database/db_manager.py`)
Управление базой данных SQLite.

**Схема базы данных:**

```sql
-- История цен
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    currency_name TEXT NOT NULL,
    chaos_value REAL NOT NULL,
    change_24h REAL,
    profitability REAL,
    pay_value REAL,
    receive_value REAL,
    timestamp TEXT NOT NULL,
    league TEXT NOT NULL
);

-- Статистика сделок
CREATE TABLE trade_statistics (
    id INTEGER PRIMARY KEY,
    currency_name TEXT NOT NULL,
    trade_type TEXT NOT NULL,
    profit REAL,
    trade_date TEXT NOT NULL,
    notes TEXT
);
```

**Ключевые операции:**
- CRUD для истории цен
- Агрегация статистики
- Очистка старых данных
- Индексация для быстрого поиска

#### PoeNinjaClient (`src/api/poe_ninja_client.py`)
Клиент для работы с poe.ninja API.

**Endpoints:**
- `/currencyoverview?league=X&type=Currency`
- `/currencyoverview?league=X&type=Fragment`

**Обработка данных:**
```python
Raw API Response → _process_currency_data() → Structured Dict
{
  "Currency Name": {
    "chaosEquivalent": float,
    "change24h": float,
    "profitability": float,
    ...
  }
}
```

#### PoeTradeClient (`src/api/poe_trade_client.py`)
Клиент для официального Trade API.

**Endpoints:**
- POST `/exchange/{league}` - поиск предложений
- GET `/fetch/{ids}` - получение деталей

**Workflow:**
```
Search → Get IDs → Fetch Details → Extract Best Rate
```

### 4. Utilities

#### ChartGenerator (`src/utils/chart_generator.py`)
Генератор графиков с использованием matplotlib.

**Типы визуализаций:**
- Line charts (временные ряды)
- Bar charts (сравнение)
- Scatter plots (корреляции)
- Multi-line comparison (тренды)

**Настройки:**
- Dark theme для соответствия игре
- PNG output для отображения в Qt
- Настраиваемые размеры и DPI

#### Helpers (`src/utils/helpers.py`)
Вспомогательные функции.

**Функции:**
- Форматирование данных
- Валидация
- Конвертация типов
- Безопасные операции

## Поток данных

### Основной цикл обновления:

```
1. Timer Trigger (каждые 60 сек)
   ↓
2. CurrencyTracker.fetch_prices()
   ↓
3. PoeNinjaClient.get_all_currencies()
   ↓
4. Process & Calculate Metrics
   ↓
5. DatabaseManager.save_price_snapshot()
   ↓
6. OverlayWindow.update_data()
   ↓
7. UI Refresh
```

### Пользовательское взаимодействие:

```
User Action (click button)
   ↓
UI Event Handler
   ↓
Business Logic Method
   ↓
Data Access / API Call
   ↓
Update UI
```

## Многопоточность

### Фоновые задачи:

1. **Currency Tracker Thread:**
```python
Thread(target=_update_loop, daemon=True)
```
- Периодическое обновление цен
- Не блокирует UI
- Graceful shutdown через Event

2. **API Requests:**
- Выполняются в отдельном потоке tracker
- Timeout для предотвращения зависаний
- Обработка ошибок

### Синхронизация:

- Qt Signals/Slots для обновления UI
- Thread-safe операции с БД (SQLite)
- Event для остановки потоков

## Обработка ошибок

### Стратегия:

1. **API Errors:**
```python
try:
    response = api_call()
except RequestException:
    logger.error()
    return default_value
```

2. **Database Errors:**
```python
try:
    db_operation()
except sqlite3.Error:
    logger.error()
    rollback()
```

3. **UI Errors:**
```python
try:
    update_ui()
except Exception:
    show_error_message()
```

### Логирование:

```python
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Конфигурация

### config.py структура:

```python
# API Settings
POE_NINJA_API = "..."
REQUEST_TIMEOUT = 10

# Database Settings
DB_NAME = "..."
MAX_HISTORY_DAYS = 30

# UI Settings
OVERLAY_OPACITY = 0.9
OVERLAY_WIDTH = 400

# Business Logic
MIN_PROFIT_PERCENTAGE = 5.0
UPDATE_INTERVAL = 60
```

## Расширяемость

### Добавление нового API источника:

1. Создать новый client в `src/api/`
2. Реализовать методы получения данных
3. Добавить обработку в `CurrencyTracker`
4. Обновить UI при необходимости

### Добавление нового типа анализа:

1. Создать метод в `ProfitCalculator`
2. Добавить в `CurrencyTracker` если нужна периодичность
3. Создать UI компонент для отображения

### Добавление нового типа графика:

1. Добавить метод в `ChartGenerator`
2. Добавить опцию в `ChartWidget`
3. Создать обработчик в UI

## Производительность

### Оптимизации:

1. **Кэширование:**
- Текущие курсы в памяти
- Минимальные запросы к API

2. **Индексы БД:**
- По currency_name + timestamp
- По trade_date

3. **Пакетная обработка:**
- Сохранение всех валют одной транзакцией

4. **Асинхронность:**
- API запросы не блокируют UI
- Фоновое обновление данных

### Метрики:

- Время запроса к API: ~1-2 сек
- Обработка данных: <100 мс
- Обновление UI: <50 мс
- Размер БД: ~10 MB/месяц

## Безопасность

### Меры:

1. **API:**
- Timeout для всех запросов
- Валидация ответов
- Rate limiting respect

2. **Database:**
- Prepared statements (защита от SQL injection)
- Валидация входных данных
- Регулярная очистка

3. **UI:**
- Санитизация отображаемых данных
- Безопасное форматирование

## Тестирование

### Подходы:

1. **Unit Tests:**
```python
test_calculate_profit()
test_process_currency_data()
test_database_operations()
```

2. **Integration Tests:**
```python
test_fetch_and_save_prices()
test_ui_update_flow()
```

3. **Manual Testing:**
- Проверка оверлея в игре
- Тестирование всех функций UI
- Проверка графиков

## Развертывание

### Сборка:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

### Результат:
- Standalone executable
- Включает все зависимости
- Работает без Python

## Мониторинг

### Логи:

- Application logs в stdout
- Error logs с traceback
- Performance metrics

### Метрики:

- Успешность API запросов
- Время обработки
- Размер БД
- Использование памяти

## Заключение

Архитектура построена по принципам:
- **Модульность** - независимые компоненты
- **Расширяемость** - легко добавлять функции
- **Надежность** - обработка ошибок
- **Производительность** - оптимизированная работа
