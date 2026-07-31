# Laboratorio N2 — EduFlex

## Estructura actual

El laboratorio implementa una arquitectura de microservicios. El código fuente que forma parte de este repositorio se agrupa en `MICROSERVICES/`; la infraestructura Docker se mantiene separada en `INFRA/`.

```text
Laboratorio_N2/
├── INFRA/
│   ├── build/
│   │   ├── Dockerfile
│   │   └── supervisord.conf
│   ├── micro_bff_app/
│   │   └── docker-compose.yml
│   ├── micro_dbs/
│   │   └── docker-compose.yml
│   ├── micro_webapp/
│   │   └── docker-compose.yml
│   └── reverse_proxy/
│       ├── docker-compose.yml
│       └── dnsmasq.d/
│           └── lms.conf
├── MICROSERVICES/
│   ├── micro_bff_app/
│   │   ├── app.py
│   │   ├── wsgi.py
│   │   ├── services.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── courses.py
│   │   │   ├── enrollments.py
│   │   │   ├── reports.py
│   │   │   └── users.py
│   │   └── templates/
│   │       ├── auth/
│   │       ├── courses/
│   │       ├── enrollments/
│   │       ├── reports/
│   │       └── users/
│   └── micro_app_reports/
│       ├── main.py
│       ├── requirements.txt
│       └── routes/
│           └── routes.py
└── LEER_IMPORTANTE.md
```

## Componentes

- `INFRA/build/`: imagen base Ubuntu con Supervisor para ejecutar los procesos de los contenedores.
- `INFRA/micro_bff_app/`: declara el BFF web, sus variables de entorno, el túnel ngrok y la URL de cada API, incluida `REPORTS_URL`.
- `INFRA/micro_webapp/`: declara los contenedores de usuarios (8001), cursos (8002), inscripciones (8003) y reportes (8004) en la red Docker externa `ADSL`.
- `INFRA/micro_dbs/`: crea una base PostgreSQL independiente para usuarios, cursos e inscripciones. Reportes no tiene base de datos.
- `INFRA/reverse_proxy/`: contiene la configuración de `nginx-proxy` y `dnsmasq` para resolver los subdominios locales `*.lms.local`.
- `MICROSERVICES/micro_bff_app/`: aplicación Flask que presenta las vistas HTML, mantiene la sesión y aplica las reglas de autorización.
- `MICROSERVICES/micro_app_reports/`: API FastAPI consumible, sin modelos, esquemas ni conexión a datos propia.

## Flujo de reportes

```text
Navegador
    │
    ▼
micro_bff_app (Flask, :8000)
    │  GET /api/reports/overview + JWT
    ▼
micro_app_reports (FastAPI, :8004)
    ├──► micro_app_user (:8001)
    ├──► micro_app_courses (:8002)
    └──► micro_app_enrollments (:8003)
```

La ruta web `GET /reports/` del BFF verifica la sesión del docente y llama a `services.reports_overview(token)`. El BFF no calcula ocupación ni consulta matrículas directamente.

El microservicio de reportes expone:

```text
GET /api/reports/overview
Authorization: Bearer <JWT>
```

Después de validar el JWT, consulta el perfil del usuario, los cursos del docente y los conteos de inscripción. Con esas respuestas arma `summary` y `reports` para que el BFF los renderice.