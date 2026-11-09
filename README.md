# WaySmart
## Equipo

Organización: `PY-WaySmart`.

| Team | Se encarga de |
|---|---|
| Backend | Modelos, vistas, validaciones, admin, permisos |
| Frontend | Templates, CSS y lo que ve el usuario |
| Scrum Masters | Prioridad, revisión de PR e integración |

La web sigue en Django con templates. No se usa React ni Vue en esta etapa. La app móvil (Kotlin) consumirá una API más adelante; no hace falta separarla ahora.

Base Django del proyecto para trabajar con templates, HTML y CSS. Esta rama (`foundation`) es el punto de partida; nadie debe hacer commits directamente a `main`.

## Desarrollo local

Si es la 1ra vez que clonas este repo, desde la carpeta del proyecto en tu VS Code, ejecuta estos comandos en la consola de PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

(OPCIONAL DE MOMENTO) => Completa `SECRET_KEY` en `.env` con una clave local antes de iniciar el servidor.

## Ramas

Nadie trabaja directo sobre `main`.

| Rama | Uso |
|---|---|
| `main` | Estable. Solo entra por pull request. |
| `foundation` | Base limpia del proyecto. Punto de partida del equipo. |
| `feature/nombre` | Una funcionalidad. Ejemplo: `feature/registro-repartidor`. |
| `fix/nombre` | Un bug. Ejemplo: `fix/login-cuenta-rechazada`. |

## Flujo:

```bash
git checkout foundation
git pull
git checkout -b feature/registro-repartidor
# ...cambios...
git push -u origin feature/registro-repartidor
```

Abrir un pull request hacia `develop` (o hacia `main` cuando la base ya esté integrada). Antes de pedir la revisión:

```bash
git fetch origin
git rebase origin/foundation
```

Un pull request, un tema. Si hay que tocar modelos compartidos (`User`, `Repartidor`, `Empresa`), avisar en el equipo antes de abrir el PR.

## Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/).

### Reglas

- Un commit, un cambio. No juntes registro de repartidor, CSS y README en el mismo commit.
- Si el usuario ve algo nuevo, es `feat`. Si solo cambia cómo está escrito el código, es `refactor`.
- No uses `update`, `cambios`, `fix varios` ni `wip` en ramas que se van a integrar.
- Escribe en español, igual que el resto del proyecto.


El historial tiene que decir qué cambió sin abrir cada archivo. Con varias personas en el repo, mensajes como `update`, `arreglos` o `ya` no sirven para revisar un PR ni para explicar el proyecto el día de la entrega.

```text
tipo(alcance): descripción breve

cuerpo opcional. Qué cambió y por qué, no un diario.
```

- **tipo**: qué clase de cambio es (tabla de abajo).
- **alcance**: la app o el tema. Ejemplos: `drivers`, `companies`, `auth`, `services`, `routes`, `payments`, `readme`, `deps`.
- **descripción**: imperativo, minúscula, sin punto final. `agrega registro`, no `agregué el registro`.

| Tipo | Cuándo usarlo | Versión (Si aplica) |
|---|---|---|
| `feat` | Función nueva que el usuario o el admin nota | Menor (1.0 → 1.1) |
| `fix` | Algo que debía funcionar y fallaba | Parche (1.0 → 1.0.1) |
| `feat!` | Rompe lo que el resto del equipo ya usaba (modelo, URL, login) | Mayor (1.0 → 2.0) |
| `refactor` | Mismo comportamiento, código más ordenado | No |
| `docs` | Solo documentación | No |
| `style` | Formato: espacios, comillas, imports. Cero lógica | No |
| `test` | Agregar o corregir pruebas | No |
| `chore` | Dependencias, `.gitignore`, `.env.example`, mantenimiento | No |
| `ci` | GitHub Actions u otro pipeline | No |

El `!` después del tipo (o la línea `BREAKING CHANGE:` en el pie) avisa que hay que ajustar el código local. La reorganización de apps de la base es un cambio de ese tipo.

### Ejemplos

Base que reemplaza las apps viejas:

```text
feat(core)!: unifica modelos y reorganiza las apps

Fusiona Repartidor y Modelo duplicados.
Deja users, companies, drivers, services, routes y payments.

BREAKING CHANGE: las apps app_* anteriores ya no existen. Clonar de nuevo y migrar.
```

Función nueva:

```text
feat(drivers): agrega registro de repartidor con estado pendiente
```

Bug:

```text
fix(auth): impide login si la cuenta del repartidor está rechazada
```

Orden interno, sin cambio visible:

```text
refactor(companies): mueve Convenio a la app companies sin cambiar campos
```

Documentación:

```text
docs(readme): documenta conventional commits y el flujo de ramas
```

Dependencias:

```text
chore(deps): agrega django-environ y fija Django en requirements.txt
```

Pruebas:

```text
test(drivers): cubre que no se apruebe un vehículo sin placa
```

Formato:

```text
style(drivers): ordena imports en models.py
```

Pipeline:

```text
ci(github): corre migrate y tests en cada pull request
```

