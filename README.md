# DevTools Playground - Backend

## Architecture

```
backend/
├── app/
│   ├── core/           # Configuración y utilidades centrales
│   │   ├── config.py   # Configuración de la aplicación
│   │   ├── database.py # Configuración de base de datos
│   │   ├── exceptions.py # Excepciones personalizadas
│   │   └── startup.py  # Lógica de inicio
│   ├── dictionary/     # Módulo de diccionario
│   │   ├── db_models.py    # Modelos SQLAlchemy
│   │   ├── schemas.py      # Esquemas Pydantic
│   │   ├── repository.py   # Capa de acceso a datos
│   │   ├── service.py      # Lógica de negocio
│   │   └── router.py       # Endpoints API
│   ├── shopping/       # Módulo de calculadora de compras
│   └── words/          # Módulo de concatenación de palabras
├── tests/              # Tests unitarios e integración
├── alembic/           # Migraciones de base de datos
└── requirements.txt    # Dependencias Python
```

