# Laboratorio N2 — EduFlex

## Arquitectura del proyecto

El laboratorio adopta una arquitectura de microservicios. El BFF concentra la interfaz web y coordina las llamadas a los servicios de usuarios, cursos e inscripciones; cada servicio se ejecuta de forma independiente y dispone de su propia base de datos PostgreSQL.

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
├── micro_bff_app/
│   ├── app.py
│   ├── wsgi.py
│   ├── services.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── courses.py
│   │   ├── enrollments.py
│   │   ├── reports.py
│   │   └── users.py
│   └── templates/
│       ├── auth/
│       ├── courses/
│       ├── enrollments/
│       ├── reports/
│       └── users/
└── lab2.md
```

### Componentes

- `INFRA/build/`: define la imagen base Ubuntu y Supervisor, encargado de administrar los procesos de los contenedores.
- `INFRA/micro_bff_app/`: levanta el BFF web, configura las URL de los servicios y permite exponerlo mediante ngrok para desarrollo.
- `INFRA/micro_webapp/`: declara los contenedores de los microservicios de usuarios, cursos e inscripciones. Cada uno se publica internamente en la red `ADSL`.
- `INFRA/micro_dbs/`: crea tres instancias PostgreSQL independientes: una para usuarios, otra para cursos y otra para inscripciones. Esta separación mantiene los datos aislados por dominio.
- `INFRA/reverse_proxy/`: incorpora `nginx-proxy` para enrutar los subdominios `*.lms.local` y `dnsmasq` para resolverlos en el entorno local.
- `micro_bff_app/`: aplicación Flask que presenta la interfaz y funciona como Backend for Frontend. `services.py` concentra las llamadas HTTP hacia los microservicios.
- `micro_bff_app/templates/`: vistas HTML agrupadas por funcionalidad, incluyendo la pantalla de reportes.

### Flujo principal

El navegador accede al BFF a través del proxy inverso. El BFF mantiene la sesión del usuario, aplica las reglas de autorización y consulta los microservicios por HTTP. Los servicios persisten sus datos en la base PostgreSQL correspondiente, sin compartir una misma base de datos.
