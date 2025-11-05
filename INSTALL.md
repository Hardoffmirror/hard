# Руководство по установке

Подробное руководство по установке и настройке PoE Currency Exchange Helper.

## Системные требования

### Минимальные требования:
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.8 или выше
- **RAM**: 2 GB
- **Диск**: 100 MB свободного места
- **Интернет**: Требуется для получения данных

### Рекомендуемые требования:
- **Python**: 3.10 или выше
- **RAM**: 4 GB
- **Диск**: 500 MB (для истории данных)

## Установка Python

### Windows

1. Скачайте Python с [python.org](https://www.python.org/downloads/)
2. Запустите установщик
3. **ВАЖНО**: Отметьте "Add Python to PATH"
4. Выберите "Install Now"
5. Проверьте установку:
```cmd
python --version
```

### Linux

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

Fedora:
```bash
sudo dnf install python3 python3-pip
```

### macOS

```bash
brew install python3
```

## Установка приложения

### Способ 1: Клонирование репозитория

```bash
# Клонировать репозиторий
git clone <repository-url>
cd hard

# Создать виртуальное окружение (рекомендуется)
python -m venv venv

# Активировать виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### Способ 2: Загрузка ZIP

1. Скачайте ZIP архив репозитория
2. Распакуйте в удобную папку
3. Откройте терминал в папке проекта
4. Выполните команды из способа 1 (начиная с создания venv)

## Настройка

### 1. Базовая настройка

Отредактируйте `config.py`:

```python
# Укажите вашу текущую лигу
CURRENT_LEAGUE = "Crucible"  # Измените на актуальную лигу

# Настройте интервал обновления (в секундах)
UPDATE_INTERVAL = 60  # Рекомендуется 60-120

# Минимальный процент прибыли для отображения
MIN_PROFIT_PERCENTAGE = 5.0
```

### 2. Настройка оверлея

Настройте положение и размер окна:

```python
OVERLAY_WIDTH = 400
OVERLAY_HEIGHT = 600
OVERLAY_X = 10  # Отступ от левого края экрана
OVERLAY_Y = 10  # Отступ от верхнего края экрана
OVERLAY_OPACITY = 0.9  # Прозрачность (0.0-1.0)
```

### 3. Настройка игры Path of Exile

Для корректной работы оверлея:

1. Откройте Path of Exile
2. Перейдите в Settings → Graphics
3. Установите режим отображения:
   - **Windowed Fullscreen** (рекомендуется)
   - или **Windowed**
4. НЕ используйте **Fullscreen** (эксклюзивный полноэкранный режим)

## Первый запуск

### 1. Тестирование подключения

```bash
python -c "from src.api.poe_ninja_client import PoeNinjaClient; print('Connected!' if PoeNinjaClient().test_connection() else 'Connection failed')"
```

### 2. Запуск примеров

```bash
python examples.py
```

Это загрузит данные и покажет примеры работы с API.

### 3. Запуск приложения

```bash
python main.py
```

Должно появиться окно оверлея с данными о валютах.

## Проверка работоспособности

После запуска проверьте:

1. ✅ Окно оверлея отображается
2. ✅ Данные о валютах загружены
3. ✅ Окно можно перетаскивать
4. ✅ Кнопки работают
5. ✅ Вкладки переключаются

## Устранение проблем при установке

### Ошибка: "python: command not found"

**Windows**: Python не добавлен в PATH. Переустановите Python с опцией "Add to PATH".

**Linux**: Используйте `python3` вместо `python`.

### Ошибка: "No module named 'PyQt5'"

```bash
pip install PyQt5
```

Если не помогло:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Ошибка: "Failed to fetch prices"

Проверьте:
1. Интернет-соединение
2. Доступность poe.ninja (откройте в браузере)
3. Правильность имени лиги в config.py

### Ошибка при установке matplotlib (Linux)

```bash
sudo apt install python3-tk
pip install matplotlib
```

### Проблемы с правами доступа (Linux/macOS)

```bash
chmod +x main.py
chmod +x examples.py
```

### Окно не отображается поверх игры

1. Убедитесь, что игра в оконном режиме
2. Попробуйте изменить `OVERLAY_OPACITY` в config.py
3. На Linux может требоваться установка дополнительных пакетов:
```bash
sudo apt install libxcb-xinerama0
```

## Автозапуск (опционально)

### Windows

1. Создайте ярлык `main.py`
2. Переместите в папку автозагрузки:
   - `Win+R` → `shell:startup`
3. Или используйте Task Scheduler для запуска при старте игры

### Linux

Добавьте в автозапуск через настройки системы или создайте `.desktop` файл:

```bash
[Desktop Entry]
Type=Application
Name=PoE Currency Helper
Exec=/path/to/venv/bin/python /path/to/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

### macOS

Используйте Automator для создания приложения или добавьте скрипт в Login Items.

## Обновление

```bash
cd hard
git pull
pip install -r requirements.txt --upgrade
```

## Удаление

```bash
# Деактивировать виртуальное окружение
deactivate

# Удалить папку проекта
rm -rf hard  # Linux/macOS
# или просто удалите папку в Windows
```

## Следующие шаги

После успешной установки:

1. Прочитайте [README.md](README.md) для изучения возможностей
2. Настройте параметры в `config.py` под себя
3. Запустите игру и приложение
4. Изучите интерфейс и функции

## Получение помощи

Если возникли проблемы:

1. Проверьте раздел "Устранение неполадок" в README.md
2. Создайте issue на GitHub с описанием проблемы
3. Приложите логи из консоли

## Полезные команды

```bash
# Обновить зависимости
pip install -r requirements.txt --upgrade

# Очистить базу данных
rm poe_currency_history.db

# Проверить версию Python
python --version

# Проверить установленные пакеты
pip list

# Создать резервную копию БД
cp poe_currency_history.db poe_currency_history.db.backup
```
