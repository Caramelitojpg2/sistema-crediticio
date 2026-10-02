# Sistema de Consultas Crediticias - V1

Aplicación de escritorio para Windows desarrollada con Python, PySide6, SQLite y ReportLab.

## IMPORTANTE

Esta V1 utiliza únicamente DATOS FICTICIOS de demostración.
No consulta Infocorp, Equifax ni ninguna central de riesgo real.

Para incorporar información crediticia real deberá utilizarse una integración autorizada
con el proveedor correspondiente y aplicar las obligaciones legales de protección de datos.

## Requisitos

- Windows 10/11
- Python 3.11 o superior
- Visual Studio Code

## Instalación

Abre la terminal de VS Code dentro de esta carpeta y ejecuta:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

Luego:

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
python main.py
```

## Usuario de demostración

Usuario: `admin`
Contraseña: `admin123`

## DNI de prueba

- 76302274
- 70451236
- 45871263

No utilizar estos datos como información crediticia real.

## Carpetas

- `data/` contiene la base SQLite.
- `reports/` contiene los PDF generados.

La base de datos se crea automáticamente la primera vez que ejecutas el programa.
