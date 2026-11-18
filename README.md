# AsmPath Checker

[English](#english) | [Русский](#русский)

---

## English

### Overview
**AsmPath Checker** is an isolated code execution and verification engine for **AsmPath** — an interactive learning platform for x86-64 Assembly.

The checker runs inside an ephemeral Docker container spawned by a backend worker service subscribed to a RabbitMQ task queue. It compiles user-submitted Assembly code, executes it against a set of test cases inside a debugger, verifies CPU register states, memory values, and standard output, and produces a structured JSON report.

### Tech Stack
* **Language:** Python 3.10+ (standard library only, zero external dependencies)
* **Assembler & Linker:** NASM (`elf64`), GNU `ld`
* **Debugger / Inspector:** GDB (batch mode)
* **Runtime Environment:** Docker

### Configuration (Environment Variables)
| Variable | Default | Description |
| :--- | :--- | :--- |
| `CHECKER_WORK_DIR` | `source` | Directory mounted with input files and used for output |
| `CHECKER_TEST_TIMEOUT` | `5` | Execution timeout per test case (in seconds) |
| `CHECKER_OBJ_FILE` | `solution.o` | Temporary object file path |
| `CHECKER_EXEC_FILE` | `solution` | Temporary compiled binary path |

### Workspace Files
Before starting the container, the worker mounts the `source/` directory containing:
1. `source/solution.asm` — User's x86-64 Assembly source code.
2. `source/test_cases.json` — Test suite specification.

After execution, the checker writes:
3. `source/results.json` — Detailed verification report.

### Input & Output Format

#### Input: `test_cases.json`
* `initialState` and `stdin` are **optional**.
* At least one expected assertion (`expectedState` or `expectedStdout`) is **required** per test case.
* Keys starting with `$` denote CPU registers (e.g., `$rax`), keys starting with `&` denote memory labels/addresses (e.g., `&result`).

```json
{
  "id": "65f1a2b3c4d5e6f7a8b9c0d1",
  "unitId": 4,
  "testCases": [
    {
      "id": "test_1",
      "description": "Addition of two positive integers",
      "initialState": {
        "$rdi": 10,
        "$rsi": 15
      },
      "expectedState": {
        "$rax": 25
      },
      "stdin": [],
      "expectedStdout": []
    }
  ]
}
```

#### Output: `results.json`
Internal `description` fields are stripped from the output so test hints are not exposed to the client.

```json
{
  "compilationError": false,
  "checkerError": false,
  "checkerErrorInfo": null,
  "totalTests": 1,
  "passedTests": 1,
  "accepted": true,
  "results": [
    {
      "testId": "test_1",
      "passed": true,
      "timeoutReached": false,
      "error": false,
      "errorInfo": null,
      "actualState": { "$rax": 25 },
      "expectedState": { "$rax": 25 },
      "actualStdout": [],
      "expectedStdout": []
    }
  ]
}
```

---

## Русский

### Описание
**AsmPath Checker** — изолированный модуль сборки и проверки пользовательских решений практических задач для интерактивного тренажёра по ассемблеру **AsmPath**.

Чекер запускается внутри одноразового Docker-контейнера, который поднимается воркером-консьюмером, подписанным на очередь задач в брокере сообщений **RabbitMQ**. Сервис компилирует код студента, прогоняет его через набор тест-кейсов под управлением отладчика, сверяет состояние регистров, памяти и стандартного вывода (`stdout`), после чего формирует итоговый отчёт.

### Стек технологий
* **Язык:** Python 3.10+ (только стандартная библиотека, без внешних зависимостей)
* **Ассемблер и компоновщик:** NASM (`elf64`), GNU `ld`
* **Отладчик:** GDB (в пакетном режиме `-batch`)
* **Изоляция:** Docker

### Конфигурация (переменные окружения)
| Переменная | По умолчанию | Описание |
| :--- | :--- | :--- |
| `CHECKER_WORK_DIR` | `source` | Директория с входными данными и итоговым отчётом |
| `CHECKER_TEST_TIMEOUT` | `5` | Таймаут выполнения одного тест-кейса (в секундах) |
| `CHECKER_OBJ_FILE` | `solution.o` | Путь ко временному объектному файлу |
| `CHECKER_EXEC_FILE` | `solution` | Путь ко временному исполняемому файлу |

### Файлы рабочей директории
Перед запуском контейнера воркер монтирует директорию `source/`, содержащую:
1. `source/solution.asm` — исходный код решения пользователя (x86-64 NASM).
2. `source/test_cases.json` — набор тест-кейсов для задачи.

По завершении работы чекер генерирует:
3. `source/results.json` — структурированный результат проверки.

### Формат входных и выходных данных

#### Входные данные: `test_cases.json`
* Поля `initialState` и `stdin` являются **необязательными**.
* Наличие хотя бы одного ожидаемого результата (`expectedState` или `expectedStdout`) **обязательно**.
* Ключи с префиксом `$` обозначают регистры процессора (например, `$rax`), с префиксом `&` — адреса/метки в памяти (например, `&buffer`).

```json
{
  "id": "65f1a2b3c4d5e6f7a8b9c0d1",
  "unitId": 4,
  "testCases": [
    {
      "id": "test_1",
      "description": "Сложение двух положительных чисел",
      "initialState": {
        "$rdi": 10,
        "$rsi": 15
      },
      "expectedState": {
        "$rax": 25
      },
      "stdin": [],
      "expectedStdout": []
    }
  ]
}
```

#### Выходные данные: `results.json`
Служебное поле `description` исключается из выходного файла, чтобы не раскрывать студенту подсказки к краевым случаям.

```json
{
  "compilationError": false,
  "checkerError": false,
  "checkerErrorInfo": null,
  "totalTests": 1,
  "passedTests": 1,
  "accepted": true,
  "results": [
    {
      "testId": "test_1",
      "passed": true,
      "timeoutReached": false,
      "error": false,
      "errorInfo": null,
      "actualState": { "$rax": 25 },
      "expectedState": { "$rax": 25 },
      "actualStdout": [],
      "expectedStdout": []
    }
  ]
}
```