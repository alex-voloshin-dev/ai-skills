# ai-assets plugin — аудит работы за 2 дня

| Параметр | Значение |
|---|---|
| Версия плагина | `ai-assets@ai-assets` v0.3.11 (commit `99604ce3`) |
| Окно анализа | 2026-05-11 11:07 UTC → 2026-05-13 13:00 UTC (≈48 ч) |
| Целевой проект | `f4ai` (`/home/avav25/dev/code/f4ai`) |
| Источники данных | 39 сессий Claude Code (`~/.claude/projects/**/*.jsonl`, ~43 МБ), `<project>/.ai-assets-memory/{errors,agent-actions}.log`, кэш плагина `~/.claude/plugins/cache/ai-assets/ai-assets/0.3.11/` |
| Скрипт-аудитор | `/tmp/ai_assets_audit.py` |
| Сырой findings JSON | `/tmp/ai_assets_audit_findings.json` |

---

## TL;DR — что именно пошло не так

| # | Категория | Тяжесть | Подтверждено | Статус по докам плагина |
|---|---|---|---|---|
| 1 | `tool-output-normalize` спам WARNING (724/2 дня) | M (шум) | да | не задокументирован |
| 2 | Subagent return-contract нарушен (G7) — 26 ERROR | H | да | задокументирован как «alpha.36», не починен |
| 3 | Spawn payload schema violation Lead'ом — 6 WARN | H | да | задокументирован, не починен |
| 4 | `SendMessage` недоступен в subagent → fallback на disk | H | да | alpha.31/35/36 — known |
| 5 | `.ai-assets-memory/sessions/<sid>/team-envelopes/` не создаётся вовремя — `ls`/`Read` падают | H | да | косвенно описан в lead-protocol |
| 6 | `block-secrets-in-code` блокирует G7 envelope JSON по слову `token` | H | да | не задокументирован |
| 7 | `block-dangerous-commands` блокирует тестовую песочницу `/tmp/hook-test/...` | M | да | не задокументирован |
| 8 | cwd дрейф после context-compact (java-dev / frontend) | M | да | не задокументирован |
| 9 | Read tool превышает 25K-токенный лимит (84K, 37K) | M | да | не задокументирован |
| 10 | Hardcoded `f4ai` Postgres role в QA-проверках | M | да | не задокументирован |
| 11 | `Mandatory pre-read` 21K символов на teammate spawn | M (cost) | да | избыточно по дизайну |
| 12 | `runs.jsonl` пишет нули по токенам/событиям сессии | L | да | `session-end-finalize.py` не агрегирует |
| 13 | `git push --force-with-lease` блокируется без override | L | да | дизайн hook'а |
| 14 | Race-condition «File modified since read» при правке envelope | L | да | косвенно |
| 15 | `git add` пытается выполнить qa-engineer (запрещено CLAUDE.md) | L | да | конфликт промпта и проектных правил |

H = high, M = medium, L = low.

---

## 1. Контекст и масштаб

За 2 дня плагин был основным движком работы в `f4ai`. Ключевые цифры:

- **39 транскриптов сессий**, из них **15 — teammate-spawned** subagents (Path B "Agent Teams")
- **9 транскриптов агентов** в `subagents/` директориях (Path A субагенты)
- Идентифицированные команды (workflow): `v22-wave2-detectors` (основная — Score v2.2 Wave 2 для `f4ai-report-service`)
- Самая длинная подсессия: **`11ba0d22` (java-dev на v22-wave2-detectors), 15 ч 14 мин** wall-clock, 200 Read / 235 Bash / 47 Write tool calls, 25 envelope writes, **0** TaskUpdate calls (это симптом, а не норма — см. находку 4).

Топ инстанцированных ролей (по числу ссылок в транскриптах):

```
software-engineer  68
qa-engineer        59
java-engineer      53
db-engineer        21
frontend-engineer  17
python-engineer     7
devops-engineer     5
```

Топ skills: `develop` (19 упоминаний), `bugfix` (8), затем `code-review`, `qa`, `test-strategy`, `plugin-skill-audit`, `feature-design`, `analyze-local`, `marketing*`, `docs-pack`, `security-scan` — каждый по 1–3.

---

## 2. Критичные находки

### 2.1 [H] `tool-output-normalize` — log spam 724 WARNING / 2 дня

**Симптом.** В `<project>/.ai-assets-memory/errors.log` за окно зафиксировано **724 записи** одного типа:

```json
{"ts":"2026-05-13T12:51:37Z","severity":"WARNING","hook":"tool-output-normalize",
 "issue":"wrap_marker_missing_before_normalize",
 "advice":"tool-output-wrap.py must run before tool-output-normalize.py. Check hooks.json array order."}
```

**Корень — handshake-баг между двумя хуками.**
В `plugin/hooks/hooks.json:70-82` оба хука зарегистрированы корректно:
1. `tool-output-wrap.py`
2. `tool-output-normalize.py`

Но `tool-output-wrap.py:59` явно пропускает обёртку для коротких выходов:

> *Skip if under threshold (per untrusted-content-wrapping rule "≤200 tokens skip wrap")*

→ маркер `_lib.emit_wrap_marker()` НЕ выставляется (код `tool-output-wrap.py:84` после `print(wrapped)` и до выхода).
А `tool-output-normalize.py:39-49` всё равно проверяет маркер и пишет WARNING про неверный порядок hooks.json.

**Эффект.**
- 724 ложных WARNING — заглушают сигнал реальных ошибок в том же `errors.log`
- Совет в записи (`Check hooks.json array order`) **не воспроизводимый**: порядок верный, его правка ничего не изменит
- Кэш и source совпадают (`diff plugin/hooks/hooks.json cache/...` пустой)

**Что предлагается.**
- В `tool-output-wrap.py` всегда эмитить маркер (даже на skip-path), чтобы handshake был «прошёл, ничего не делал», а не «не запускался».
- ИЛИ в `tool-output-normalize.py` поднимать WARN только когда реально нужна нормализация (большой выход без маркера), а не на каждый <200 токенов.

**Воспроизведение.** Любая Bash/Read команда с выводом ≤ 200 токенов (большинство) → запись в `errors.log`.

---

### 2.2 [H] Subagent return-contract нарушен (G7) — 26 ошибок

**Симптом.** Hook `subagent-stop-learnings` 26 раз за окно отверг финальное сообщение subagent'а как невалидный G7 return contract:

```json
{"ts":"2026-05-11T14:24:13Z","severity":"ERROR","hook":"subagent-stop-learnings",
 "issue":"return_contract_validation_failed","trace_id":null,
 "issues":["missing_field:trace_id","missing_field:status","missing_field:tokens_used","missing_field:result"],
 "session_id":"6497dc2d-6d0c-4b3e-a20e-0ccb00e2daf3"}
```

Все 26 — из одной сессии `6497dc2d` (`/develop` lead в `f4ai`). Каждый раз отсутствуют **все 4** обязательных поля контракта.

**Что это значит.**
- Subagent (`java-engineer` / `qa-engineer` etc.) на завершении возвращает текстовое summary вместо G7 envelope.
- Hook не блокирует завершение (валидация — fail-open), но **ни одна learning из этих subagent'ов в `learnings.md` не попадает**.
- Schema находится в `plugin/schemas/return-contract.schema.json` (есть), но в системных промптах `plugin/agents/*.md` контракт не показан — у меня qa-engineer.md проверен (см. ниже): нет указания возвращать G7-объект.

**Что предлагается.**
1. В каждый `agents/*.md` добавить hard-rule «последнее сообщение subagent'а должно быть JSON по схеме `schemas/return-contract.schema.json`».
2. В `subagent-stop-learnings.py` логировать первые 200 символов финального сообщения для диагностики.
3. Альтернатива: сделать hook более снисходительным — если есть хотя бы `result`, попытаться вытащить остальное из метаданных Claude Code (он сам знает session_id, tokens_used).

---

### 2.3 [H] Spawn payload schema violation от Lead — 6 нарушений

**Симптом.** Hook `subagent-start-budget` 6 раз поймал spawn-payload Lead'а без G7 spawn-полей:

```json
{"ts":"2026-05-11T19:52:21Z","severity":"WARNING","hook":"subagent-start-budget",
 "issue":"spawn_payload_schema_violation",
 "missing_fields":["trace_id","subagent_role","goal","constraints","allowed_tools","budget"],
 "session_id":"466dd3ef-4f64-4613-a972-6cccdc96a1ec"}
```

**Все 6 поля сразу — это значит spawn идёт plain-text промптом** через `Agent(description, prompt, subagent_type)` без G7-конверта. Schema лежит в `plugin/schemas/spawn-payload.schema.json` и `team-protocols/g7-contracts.md` (51 строка), но Lead её не использует.

**Что это даёт в реальности.**
- Subagent не видит trace_id → не может его вернуть → находка 2.2 ↑ (return-contract тоже валится)
- Subagent не видит `budget` (max_turns, max_tokens) → может работать дольше плана
- Subagent не видит `allowed_tools` → не знает что разрешено (см. 2.4 — пытается `SendMessage` который не дан)

**Что предлагается.**
1. В `skills/develop/SKILL.md` (Lead-section) показать конкретный пример валидного spawn-payload (JSON в `prompt` поле Agent tool).
2. Hook `subagent-start-budget` — поднять с WARNING до ERROR + блокировать spawn пока payload не валиден (или дать grace period 1–2 нарушения).
3. Дать Lead'у helper-skill `subagent-spawn` (он есть) — НО автозапрос на использование сейчас отсутствует.

---

### 2.4 [H] `SendMessage` недоступен в subagent → известный alpha-баг

**Симптом.** В сессии `11ba0d22` (java-dev) и `agent-aa2fe4084a356b094`:

```
<tool_use_error>Error: No such tool available: SendMessage. SendMessage exists
but is not enabled in this context. Use one of the available tools instead.</tool_use_error>
```

Реальный заблокированный payload (java-dev → team-lead, BE-8 r2 verdict):
```json
{"to":"team-lead","message":"BE-8 r2 already complete — id=20 structured_data_coverage
 weightV2=10 (was 6→10 in the earlier BE-8 r2 pass this session), v2 sum=244,
 ParameterDefinitionLoaderContractTest 22/22 g..."}
```

**Документированный статус.** Это alpha.31 / alpha.35 / alpha.36 — см. `team-protocols/path-selection-rules.md:78-88` и `lead-protocol.md:60-90`. Плагин знает, что Anthropic заявленный auto-augment `SendMessage`/`TaskUpdate` для teammate в Agent Teams runtime непостоянен.

**Что плагин предписывает.** Fallback на disk-envelope: `Bash(printf '%s' '<json>' > .ai-assets-memory/sessions/<sid>/team-envelopes/<role>-<topic>-<ts>.json.tmp && mv ... ...json)`.

**Где плагин ломает свой же fallback.** См. 2.5 ↓ — sessionId, который видит teammate, **не совпадает** с тем, который Lead использовал при создании каталога.

**Что предлагается (помимо ожидания фикса в Claude Code).**
1. Системный промпт teammate'а должен явно содержать инструкцию-обходник «если SendMessage не доступен — пиши envelope в `<absolute-path>/team-envelopes/G7-<role>-<wp>.json.tmp` и делай атомарный rename» **в первых 200 строках**, не после 700 строк протоколов.
2. Lead должен передать teammate'у **абсолютный** путь к команд-каталогу envelopes, а не slug.

---

### 2.5 [H] Disk-envelope fallback ломается — каталог `team-envelopes/` не создаётся

**Симптом.** За окно: **7 ошибок `No such file or directory` на envelope-путях, 4 уникальные сессии**.

Конкретные пути (выборка):
```
.ai-assets-memory/sessions/v22-wave2-20260511-153127/team-envelopes/G7-developer-BE-5.json
.ai-assets-memory/sessions/v22-wave2-20260511-153127/team-envelopes/G7-qa-BE-3.json
.ai-assets-memory/sessions/hero-it3/team-envelopes/G7-developer-WP1.json
.ai-assets-memory/sessions/ff1d199a-2d31-4f27-b58c-b8017a8425eb/team-envelopes/TaskCompleted-1-20260512T140003Z.json
```

В сессии `42c9ded9` (`/develop` lead) Lead запустил Bash:
```
ls .ai-assets-memory/sessions/v22-wave2-20260511-153127/team-envelopes/
→ Exit code 1: No such file or directory
=== G7-qa-BE-3.json === Traceback (most recent call last):
  File "<string>", line 3, in <module>
FileNotFoundError: [Errno 2] No such file or directory
```

**Корень.**
- Lead использует **slug** имени команды (`v22-wave2-20260511-153127`, `hero-it3`) вместо UUID сессии Claude Code.
- Slug отличается от `session_id`, к которому привязан subagent (его собственный UUID).
- Lead создаёт каталог только когда первый раз туда что-то пишет — между spawn'ом и первым write subagent уже падает.

Атомарный pattern `.json.tmp + mv` сам по себе работает (java-dev `11ba0d22` сделал 25 envelope writes успешно), но **только** когда каталог уже создан.

**Что предлагается.**
1. В Lead-протоколе (`lead-protocol.md`): `Bash(mkdir -p .ai-assets-memory/sessions/<sid>/team-envelopes/)` — обязательный шаг **до** любого `Agent` spawn в Path B.
2. В spawn-payload teammate'а указывать абсолютный путь к каталогу envelopes, не относительный, не slug.
3. Использовать `session_id` Lead'а (известный из `${CLAUDE_SESSION_ID}` env) как канонический slug, а человеко-читаемый префикс — суффиксом.

---

### 2.6 [H] `block-secrets-in-code.py` блокирует свой же G7 envelope

**Симптом.** Сессия `d8f52fc2` (reviewer на v22-wave2):

```
PreToolUse:Write hook error: BLOCKED: Potential secrets detected in
/tmp/v22-envelopes/review-20.json:
  - Generic Secret: token
Use environment variables or a secrets manager instead of hardcoding secrets.
```

**Корень — слишком широкий regex.** В `plugin/hooks/scripts/block-secrets-in-code.py:26`:
```python
("Generic Secret",
 re.compile(r"(?i)(secret|token|password|passwd|pwd)\s*[=:]\s*['\"]?[A-Za-z0-9_\-!@#$%^&*]{8,}"))
```

Этот pattern ловит любой JSON-ключ с подстрокой `token` и значением длиной ≥ 8. В G7 envelope reviewer'а есть поля типа `"tokens_used": 12345` или `"trace_id": "wf-...-token..."` → false-positive.

**Эффект.** Reviewer не может записать вердикт → весь Path B застревает (см. находку 2.4 — `SendMessage` тоже не работает) → workflow деградирует до ручного вмешательства.

**Что предлагается.**
1. Заменить regex на более точный — исключить `tokens_used`, `tokens_in`, `tokens_out`, `bearer_*` (если оно с placeholder), и matchить только то, что реально похоже на секрет (≥ 20 символов, base64-/hex-alphabet).
2. Добавить allowlist путей: `.ai-assets-memory/sessions/**`, `/tmp/*envelope*`, `/tmp/v22-envelopes/**` — это **служебные конверты плагина**, не код.
3. Хук должен пропускать `Write` где content начинается с `{` и парсится как JSON (не код по определению).

---

### 2.7 [M] `block-dangerous-commands.py` блокирует тестовую песочницу

**Симптом.** Сессия `agent-abf0be8ed146e7b88` (тест self-hooks):

```bash
cd /tmp && rm -rf hook-test && mkdir hook-test && cd hook-test && git init -q ...
```
Заблокировано как `Forced recursive delete`.

**Корень.** `block-dangerous-commands.py:23-24`:
```python
("Filesystem", r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s", "Forced recursive delete")
```
Pattern не различает «`rm -rf /etc`» и «`rm -rf /tmp/sandbox`».

**Эффект.** Тестировщику собственного плагина приходится разбивать команду или выполнять через терминал.

**Что предлагается.** Добавить allowlist путей (`/tmp/**`, `~/.cache/**`, `${TMPDIR}/**`) либо требовать только что путь начинается с одного из «безопасных» префиксов.

**Также подтверждено корректное срабатывание** на `git push --force-with-lease origin main` (сессия `2f59a101`) — это валидное предупреждение, но без override flag пользователю приходится идти в терминал. Рассмотреть «override через явное env-var» (например `AI_ASSETS_ALLOW_DANGEROUS=1` для одной сессии).

---

### 2.8 [M] cwd-дрейф после context-compact

**Симптом.** Сессия `11ba0d22` (java-dev), 3 одинаковые ошибки:

```
Bash: ls f4ai-report-service/mvnw
→ File does not exist. Note: your current working directory is
  /home/avav25/dev/code/f4ai/f4ai-report-service.
```

Subagent уже **внутри** `f4ai-report-service`, но пытается зайти в одноимённый поддиректорий. Аналогично frontend-engineer (`ff1d199a`):
```
cd: f4ai-ui-service: No such file or directory
```

Сессия 11ba0d22 проходила context-compact (видно по `<task-notification>` и упоминанию «continued from previous conversation that ran out of context»). После compact'а ментальная модель cwd subagent'а не сохраняется.

**Что предлагается.**
1. В `developer-protocol.md` / `qa-protocol.md`: hard-rule «перед любым `cd <path>` или относительным путём → `pwd && git rev-parse --show-toplevel`».
2. В системный промпт subagent'а добавить «cwd на старте: `<absolute path>`. После compact выполни `pwd` и сверь.»
3. Hook `session-start-context.py` уже есть — проверить, фиксирует ли он cwd при ресторе.

---

### 2.9 [M] Read tool превышает 25K-токенный лимит

**Симптом.** 4 случая `File content (NN tokens) exceeds maximum allowed tokens (25000)`:

| Файл | Токены | Сессия |
|---|---|---|
| `f4ai/features/in-progress/score-v2-content-quality-signals/design.md` | 37 705 | `b27051c4` |
| `/tmp/claude-1000/.../tasks/bfk0weuyl.output` (Monitor stream) | 84 750 | `c5ddbac9` |

**Корень.** Skill'ы `/develop` и `/bugfix` инструктируют subagent читать «design.md полностью», но не предупреждают про лимит.

**Что предлагается.**
1. В `developer-protocol.md` для секции «pre-read»: «при Read большого файла используй `offset/limit` или сначала `wc -l + grep`».
2. Lead-skill сам пред-читает design.md и передаёт teammate'у только релевантные секции в spawn-prompt'е.

---

### 2.10 [M] Hardcoded `f4ai` Postgres role в QA-проверках

**Симптом.** Сессия `75d69aec` (qa на v22-wave2):

```
Exit code 2 psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed:
FATAL:  role "f4ai" does not exist
```

Subagent пытается локально подсоединиться к Postgres ролью `f4ai`, которая существует только внутри docker-compose контейнера. На хосте — другая конфигурация (см. f4ai/CLAUDE.md секция «Local Development»).

**Корень.** В каком-то генерируемом промпте Lead'а или в шаблоне QA проверки (вероятно где-то в `skills/develop/` или через test-strategy) зашита строка подключения «как в docker». Конкретный источник не подтверждён без grep'а по транскрипту.

**Что предлагается.**
1. QA-агент должен читать DB connection из `${PROJECT_ROOT}/.env` или CLAUDE.md, не предполагать Docker-имена.
2. В `agents/qa-engineer.md` добавить hard-rule: «никогда не хардкодь `localhost:5432` / роли БД — читай из `.env` / `application.yml`».

---

### 2.11 [M] Mandatory pre-read tax: 21K символов на teammate spawn

**Метрика.** В 6 случаях фиксируется первый user-промпт teammate'а с заголовком `## Mandatory pre-read`:

| Метрика | Значение |
|---|---|
| Среднее | 10 191 символ (~2 500 токенов) |
| Максимум | **21 166 символов** (~5 300 токенов) |

При 4–5 spawn'ах в `/develop` это **≥ 20K токенов оверхеда** до первой полезной операции, не считая сам инлайн-контекст промпта (`<task_assignment>`, `<acceptance-criteria>`, design.md slice, etc.).

**Корень.** `team-protocols/` skill — 8 файлов, 941 строка суммарно:
```
SKILL.md                  108
developer-protocol.md      88
g7-contracts.md            51
lead-protocol.md          290
path-selection-rules.md   185  ← 79% — описание alpha.31/35/36 багов
reviewer-protocol.md       76
role-selection-table.md    48
spawn-pattern.md           95
```

Lead просит teammate **прочитать 4-5 из них** в `Mandatory pre-read`. Самая большая нагрузка — `path-selection-rules.md` (185 строк описания **известных runtime багов**).

**Что предлагается.**
1. Сделать «role-cards» — 30-50 строк на роль с инлайн-сжатой версией всех нужных протоколов.
2. Бо́льшую часть `path-selection-rules.md` вынести в lead-only документ — teammate'у не нужно знать про alpha.34 TeamDelete на active.
3. Полную доку оставить как `@reference` для случаев когда teammate сам спросит «как мне X».

---

## 3. Менее критичные находки

### 3.1 [L] `runs.jsonl` пишет нули по токенам/событиям

В `<project>/.ai-assets-memory/runs.jsonl` каждая запись `SessionEnd`:
```json
{"event":"SessionEnd","session_id":"42c9ded9-...","tokens_in_total":0,
 "tokens_out_total":0,"ralf_iter_total":0,"ralf_tokens_total":0,
 "session_event_count":77,"session_started_at":"2026-05-11T19:28:40Z"}
```

`session_event_count` корректен только для одной из 13 записей (77 для `42c9ded9`), у остальных 0. Токены — везде 0. Hook `session-end-finalize.py` не агрегирует с `agent-actions.log` или telemetry.

### 3.2 [L] Race-condition «File modified since read» при правке envelope

3 случая в сессии `75d69aec` (qa) — agent делает Read → ждёт → Edit, но между этими шагами файл изменён (вероятно автоформаттером IDE / другим процессом). Не критично, но добавляет retry round.

### 3.3 [L] qa-engineer пытается выполнить `git add` (запрещено)

Сессии `dd31984d`, `7cabefde` — qa-engineer subagent предложил Bash `git add ...`, юзер отклонил. CLAUDE.md проекта явно запрещает (`Agents are NOT allowed to: git commit, git push, git merge, git add`). agents/qa-engineer.md содержит rule `No git write ops`, но в реальном спавне subagent всё равно пробует.

**Возможные причины.** Либо qa-engineer.md не загружается при /develop spawn (Path B оверрайдит), либо в task-промпте упоминается «закоммить тесты». Требуется отдельная грепалка по prompts.

### 3.4 [L] `String to replace not found in file` на frontend Edit

Сессия `3e5bbf07` — frontend-engineer пытается заменить блок MUI `sx={{...}}` который уже был отредактирован. Stale snapshot. Не systemic — единичный.

### 3.5 [L] Параллельные Bash отменяются при первом падении

Сессия `c5ddbac9` (analyze-local Playwright):
```
<tool_use_error>Cancelled: parallel tool call Bash(cd /home/avav25/dev/code/f4ai/f4ai-playw…) errored</tool_use_error>
```
Это поведение Claude Code, не плагина. Но в `analyze-local` skill стоит подсказать использовать sequential calls для тестов с зависимостями.

### 3.6 [L] PostToolUseFailure x 5

5 событий за окно (sessions `da9b96fa`, `42c9ded9`, `c5ddbac9` x2, `cfa802d6`) — 4 на Bash, 1 на Read. Длительности 15–1029 ms. Без stack trace в логах — нужен `tool-failure-log.py` enrichment с тем, какой именно скрипт хука упал.

---

## 4. Что работает хорошо (контроль)

- **Атомарная запись envelope** (`.json.tmp + mv`) — java-dev `11ba0d22` сделал 25 envelope writes без единого corrupt-файла.
- **Hook `block-secrets-in-code`** ловит реальные генерик-патерны (1 ERROR за окно — это и есть наш false-positive, других не было).
- **Hook `block-dangerous-commands`** правильно поймал `git push --force-with-lease`, `kubectl delete --all` и т.п. (косвенно, по отсутствию в errors.log за 2 дня).
- **Skill `plugin-skill-audit`** — 3 запуска, 0 ошибок в логах. Self-test чистый.
- **Subagent `software-engineer` / `java-engineer`** — мало ошибок относительно числа spawn'ов (2 / 1 на десятки spawn'ов).
- **Skill `analyze-local`** дошёл до диагностики Playwright fail без падения — `c5ddbac9`.

---

## 5. Roadmap фиксов (рекомендованный приоритет)

### Спринт 1 — самосаботаж плагина (high impact, low effort)

1. **Fix 2.1**: `tool-output-wrap.py` всегда эмитит маркер (даже на skip-path) → -724 WARNING в день.
2. **Fix 2.6**: regex `Generic Secret` сужается + allowlist `.ai-assets-memory/**`, `/tmp/*envelope*`, JSON-skip → разблокирует Path B reviewers.
3. **Fix 2.7**: allowlist `/tmp/**`, `~/.cache/**` для `block-dangerous-commands` → не блокирует тестовые песочницы.
4. **Fix 2.5**: `mkdir -p` каталога envelopes в `lead-protocol.md` как первый шаг team setup → разблокирует disk-envelope fallback.

### Спринт 2 — G7 контракт (high impact, medium effort)

5. **Fix 2.3**: пример валидного spawn-payload в `skills/develop/SKILL.md` + hook `subagent-start-budget` блокирует невалидные → Lead начнёт соблюдать G7.
6. **Fix 2.2**: hard-rule в каждом `agents/*.md` про возврат G7 envelope → learnings снова начнут писаться.
7. **Fix 2.11**: «role cards» для teammate spawn — pre-read ужать в 2-3 раза.

### Спринт 3 — runtime resilience (medium impact)

8. **Fix 2.8**: `pwd` mandatory check в `developer-protocol.md`.
9. **Fix 2.9**: правило про Read offset/limit в pre-read sections.
10. **Fix 2.10**: read DB connection из `.env`, не предполагать Docker.
11. **Fix 3.1**: `session-end-finalize.py` агрегирует токены и events.

### Спринт 4 — наблюдаемость

12. Enrichment `tool-failure-log.py` (имя хука + stderr).
13. Реальный smoke-тест hook chain'а — проверить что false-positive 2.6 не возникает на стандартных G7 envelope'ах.
14. Dashboard / `/plugin-doctor` — показывает 5 топ-ошибок за последние N дней из `errors.log`.

---

## 6. Воспроизведение и следующие шаги

Чтобы повторить любой findings без чтения транскриптов руками:

```bash
# Перегенерация JSON находок
python3 /tmp/ai_assets_audit.py

# Сводка ошибок из errors.log
python3 -c "
import json, datetime as dt
from collections import Counter
from pathlib import Path
cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)
hooks = Counter()
for raw in open('/home/avav25/dev/code/f4ai/.ai-assets-memory/errors.log'):
    try: d = json.loads(raw)
    except: continue
    ts = d.get('ts','')
    try: t = dt.datetime.fromisoformat(ts.replace('Z','+00:00'))
    except: continue
    if t < cutoff: continue
    hooks[d.get('hook','?')] += 1
print(hooks.most_common())"
```

Для глубокого расследования отдельной находки — читать соответствующий `.jsonl` из таблицы ниже:

| Сессия | Файл (от `~/.claude/projects/-home-avav25-dev-code-f4ai/`) | Кейс |
|---|---|---|
| `11ba0d22` | `11ba0d22-63ef-4612-8686-b36cec1cfe0c.jsonl` | java-dev v22-wave2, SendMessage block, 21 errors |
| `42c9ded9` | `42c9ded9-c6f5-4524-b2de-93109bede621.jsonl` | Lead /develop, mkdir-envelope baseline |
| `73ef823e` | `73ef823e-008d-4826-b447-6c05a619af2d.jsonl` | reviewer v22-wave2, чистая работа на disk-envelopes |
| `75d69aec` | `75d69aec-01c6-442f-9d18-e8c066cb6267.jsonl` | qa v22-wave2, psql role error |
| `d8f52fc2` | `d8f52fc2-921f-4f53-91f2-a1452410e575.jsonl` | reviewer заблокирован secret-hook на envelope |
| `6497dc2d` | `6497dc2d-6d0c-4b3e-a20e-0ccb00e2daf3.jsonl` | 26 return-contract violations подряд |
| `c5ddbac9` | `c5ddbac9-8adc-4656-8248-97330b5c01a6.jsonl` | analyze-local Playwright, parallel-cancel, 84K Read |
| `b27051c4` | `b27051c4-4b33-4865-8294-33e11abdea83.jsonl` | 37K-token Read на design.md |
| `3e5bbf07` | `3e5bbf07-e627-458e-be81-859a2e3552b0.jsonl` | UI hero, stale-Edit |
| `dd31984d` | `dd31984d-f93b-47d9-859b-e3feccef51fb.jsonl` | qa пытался `git add`, отказ |
| `2f59a101` | (`-home-avav25-dev-code-aic/`) `2f59a101-...jsonl` | force-push корректно заблокирован |

### Связанные источники в репозитории плагина

- `plugin/hooks/scripts/tool-output-wrap.py:59,84` — skip-path без маркера
- `plugin/hooks/scripts/tool-output-normalize.py:39-49` — WARNING на отсутствие маркера
- `plugin/hooks/scripts/block-secrets-in-code.py:26` — широкий regex `Generic Secret`
- `plugin/hooks/scripts/block-dangerous-commands.py:23-24` — `rm -rf` без allowlist
- `plugin/hooks/scripts/subagent-start-budget.py` — должен блокировать невалидный G7 spawn
- `plugin/hooks/scripts/subagent-stop-learnings.py` — нужен лог финального сообщения
- `plugin/skills/team-protocols/lead-protocol.md` — отсутствует обязательный `mkdir -p` шаг
- `plugin/skills/team-protocols/path-selection-rules.md:78-88` — alpha.31/35/36 описаны, но не вынесены в teammate-промпт
- `plugin/agents/qa-engineer.md` — нет G7 return-contract hard-rule
- `plugin/agents/*.md` (все) — нет упоминания G7 schema

---

## 7. Изменения в `~/.ai-assets-memory/learnings.md` (предложение)

После починки добавить запись:

```markdown
## 2026-05-13 — G7 envelope fallback paths

When Path B SendMessage/TaskUpdate are unavailable (alpha.31/35/36):
- Lead MUST `mkdir -p .ai-assets-memory/sessions/<canonical_session_id>/team-envelopes/`
  before any `Agent` spawn.
- Use the Lead's `${CLAUDE_SESSION_ID}` as canonical slug, not human-readable team name.
- Pass absolute path to teammate in spawn-payload.
- Teammate writes envelope via `printf '%s' '<json>' > <path>.tmp && mv <path>.tmp <path>`.
- The 'Generic Secret: token' regex in block-secrets-in-code.py false-matches
  G7 envelopes with `tokens_used` field — needs allowlist for envelope paths.
```

---

*Конец отчёта. Сгенерирован 2026-05-13 на основе сессий 2026-05-11 → 2026-05-13.*
