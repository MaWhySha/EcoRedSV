\# Feedback de prueba - Daniela Ester López Varela



\## Equipo



| Dato | Valor |

|---|---|

| Sistema operativo | Windows 11 |

| Versión de Python | 3.13 |

| SQL Server | Instancia por defecto (`localhost`, MSSQLSERVER) |

| ODBC Driver | ODBC Driver 18 for SQL Server |

| Herramienta de base de datos | SQL Server Management Studio (SSMS) |



\## Instalación



\*\*¿Se instaló sin problemas?\*\* Sí, con un error de conexión que se resolvió durante la instalación.



\### Pasos realizados



1\. Se verificó que Python, Git, SQL Server, SSMS y el ODBC Driver 18 estuvieran instalados.

2\. Se activó el modo de autenticación de SQL Server y Windows desde SSMS.

3\. Se habilitó TCP/IP en el puerto 1433 desde el Administrador de configuración de SQL Server.

4\. Se creó la base de datos `ecoredsv` y el usuario `ecoredsv\_app` con permisos de `db\_owner`.

5\. Se clonó el repositorio, se creó el entorno virtual y se instalaron las dependencias con `pip install -r requirements.txt`.

6\. Se creó el archivo `.env` a partir de `.env.example`, con una SECRET\_KEY propia y los datos de conexión.

7\. Se ejecutaron `check`, `migrate`, `createsuperuser` y `runserver`.



\### Error encontrado



Al correr `python manage.py migrate` salió este error:



> Proveedor de TCP: No se puede establecer una conexión ya que el equipo de destino denegó expresamente dicha conexión (10061).



\*\*Causa:\*\* SQL Server no estaba escuchando en el puerto 1433, porque el servicio no se había reiniciado después de habilitar TCP/IP.



\*\*Solución:\*\* Se reinició el servicio \*\*SQL Server (MSSQLSERVER)\*\* desde el Administrador de configuración de SQL Server. Se comprobó con `Test-NetConnection localhost -Port 1433` (resultado `True`), y después `migrate` aplicó todas las migraciones correctamente.



\### Evidencias



Las capturas de la instalación y de las pruebas se entregan adjuntas en una carpeta aparte, fuera del repositorio.



\## Pruebas del sistema



| Prueba | Resultado | Observaciones |

|---|---|---|

| Conexión con SQL Server | Funciona | `migrate` creó todas las tablas en `ecoredsv` y se ven en SSMS |

| Creación de superusuario | Funciona | `createsuperuser` creó el usuario sin errores |

| Ejecución del servidor | Funciona | `runserver` levanta el sistema en `http://127.0.0.1:8000` |

| Página de inicio | Funciona | Muestra el estado de conexión con SQL Server y la versión del servidor |

| Prueba de clases | Funciona | Se muestran los datos de ejemplo de puntos, materiales, reportes y roles |

| Panel de administración (`/admin`) | Funciona | Se inició sesión con el superusuario creado |



\## Errores encontrados



\- Error de conexión TCP en el puerto 1433 durante el primer `migrate`, resuelto reiniciando el servicio de SQL Server.

\- No se encontraron errores en el sistema una vez instalado.



\## Sugerencias



\- Recalcar en la guía de instalación que hay que \*\*reiniciar el servicio de SQL Server\*\* después de habilitar TCP/IP, y comprobarlo con `Test-NetConnection` antes de correr `migrate`.

\- Indicar en la guía dónde se guarda el repositorio al clonarlo, porque si no se usa `cd` antes, queda en la carpeta de usuario.

\- Aclarar que `venv` (entorno virtual) y `.env` (configuración) son cosas distintas, porque se confunden por el nombre.

