# Newman CLI - API Testing Guide

## ¿Qué es Newman?

Newman es la herramienta de línea de comandos (CLI) de Postman que permite ejecutar colecciones de Postman de forma automatizada, sin necesidad de abrir la interfaz gráfica.

**Nota:** Este cambio es para validar que el pipeline de GitHub Actions funciona correctamente.

## Instalación

Newman ya está instalado en este proyecto como dependencia de desarrollo.

```bash
# Verificar versión instalada
npx newman --version
```

## Uso

### 1. Ejecutar tests con el script bash

```bash
./run_api_tests.sh
```

### 2. Ejecutar tests con npm

```bash
npm run test:api          # CLI + HTML + JSON
npm run test:api:json     # Solo JSON
npm run test:api:junit    # JUnit (para CI/CD)
```

### 3. Ejecutar Newman directamente

```bash
npx newman run collections/postman_environment.json
```

## Reportes

Los reportes se generan en la carpeta `reports/`:

- **api-tests.html** - Reporte visual interactivo
- **api-tests.json** - Datos en formato JSON

## Integración con CI/CD

Los workflows de GitHub Actions ejecutan Newman automáticamente:

- En cada push a main/develop
- En cada Pull Request
- Diariamente a las 2 AM UTC

Ver [GITHUB_ACTIONS_GUIDE.md](./GITHUB_ACTIONS_GUIDE.md) para más detalles.

## Troubleshooting

### Error: "Collection file not found"

```bash
# Asegúrate de estar en el directorio correcto
cd anb-rising-stars
./run_api_tests.sh
```

### Error: "Connection refused"

```bash
# Asegúrate de que la API está corriendo
docker compose up -d
```

## Recursos

- [Newman Documentation](https://learning.postman.com/docs/running-collections/using-newman-cli/)
- [Postman Collection Format](https://www.postman.com/collection/)
