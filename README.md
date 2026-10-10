# EcoRedSV

## Integrantes

- Robin Christopher Barrera Vásquez
- Alexis Omar García Romero
- Daniela Ester López Varela
- Liliana Dalila Ulloa González
- Carlos Fernando Guardado García

## Descripción

EcoRedSV es una aplicación web orientada a facilitar la búsqueda y consulta de puntos de reciclaje, permitiendo conocer su ubicación, horarios y materiales que reciben. El proyecto busca organizar esta información y facilitar a las personas la entrega adecuada de materiales reciclables.

**Proyecto de Proyección Social**
Ingeniería en Sistemas y Computación
UNAB
Grupo 6

## Problemática

La problemática identificada está relacionada con la disposición inadecuada de residuos y la dificultad para acceder a información sobre alternativas de reciclaje.

Durante la encuesta realizada participaron 8 personas, quienes mencionaron situaciones como:

- Acumulación de basura en calles y otros espacios.
- Personas que depositan residuos en lugares inadecuados.
- Contaminación de ríos.
- Escasez de depósitos de basura en algunos lugares.
- Dificultad para identificar lugares donde entregar materiales reciclables.

Los 8 participantes indicaron no conocer un lugar donde entregar materiales reciclables y ninguno manifestó conocer una campaña, organización o iniciativa de reciclaje.

## Beneficiarios

Los principales beneficiarios considerados para el proyecto son:

- Familias y habitantes de las comunidades.
- Estudiantes.
- Centros educativos.
- Recolectores y recicladores.
- Gestores de residuos.
- Organizaciones ambientales.
- Personas interesadas en el reciclaje.

El proyecto tiene como punto de partida la Colonia Veracruz, Chalatenango, con posibilidad de ampliar posteriormente su cobertura a otras comunidades.

## Usuarios del sistema

En la Semana 3 los tipos de usuario se agruparon en cuatro roles. Los estudiantes y voluntarios forman parte del rol de comunidad, ya que tienen los mismos permisos.

- **Comunidad:** consulta información sobre reciclaje, puntos de recepción y campañas; puede inscribirse a campañas y registrar reportes. Incluye a estudiantes y voluntarios.
- **Gestor de residuos o encargado de un punto de recepción:** proporciona y mantiene la información de su punto: materiales, horarios y condiciones de recepción.
- **Institución u organización:** registra campañas y actividades de reciclaje, así como los resultados de recolección.
- **Administrador:** administra usuarios, puntos de recepción, materiales, campañas, reportes y contenido educativo.

## Requisitos funcionales

**RF-01. Registro de usuarios**
El sistema deberá permitir registrar usuarios proporcionando la información necesaria para crear una cuenta y utilizar las funciones correspondientes.

**RF-02. Inicio de sesión**
El sistema deberá permitir a los usuarios registrados iniciar sesión para acceder a las funciones disponibles según sus permisos.

**RF-03. Consulta de puntos de recepción**
El sistema deberá permitir consultar los puntos de recepción y centros de acopio registrados.

**RF-04. Consulta de información de los puntos**
El sistema deberá mostrar la ubicación, horarios, condiciones de entrega y materiales recibidos por cada punto.

**RF-05. Búsqueda y filtrado de puntos**
El sistema deberá permitir buscar y filtrar puntos de recepción por municipio y por tipo de material.

**RF-06. Registro de puntos de recepción**
El sistema deberá permitir a los usuarios autorizados registrar nuevos puntos de recepción o centros de acopio.

**RF-07. Actualización de información**
El sistema deberá permitir a los usuarios autorizados modificar la información de los puntos registrados.

**RF-08. Registro de campañas y jornadas**
El sistema deberá permitir registrar campañas, jornadas o actividades de recolección, indicando la organización responsable y los materiales que se reciben.

**RF-09. Consulta de campañas y actividades**
El sistema deberá permitir consultar las campañas y actividades registradas.

**RF-10. Registro de reportes ambientales**
El sistema deberá permitir registrar reportes relacionados con acumulación o disposición inadecuada de residuos.

**RF-11. Gestión de reportes**
El sistema deberá permitir a los usuarios autorizados consultar los reportes y actualizar su estado, dejando registro de cada cambio.

**RF-12. Información educativa sobre reciclaje**
El sistema deberá permitir consultar información y recomendaciones sobre separación, clasificación y manejo adecuado de residuos.

**RF-13. Administración de registros**
El administrador deberá poder gestionar los registros almacenados en el sistema según los permisos establecidos.

**RF-15. Mapa interactivo**
El sistema deberá mostrar en un mapa los puntos de recepción, campañas y reportes.

**RF-16. Inscripción a campañas**
El sistema deberá permitir a los usuarios inscribirse a campañas de recolección.

**RF-17. Registro de peso recolectado**
El sistema deberá permitir registrar la cantidad de material recolectado en cada campaña.

**RF-18. Resultados de campañas**
El sistema deberá permitir consultar los resultados de recolección de cada campaña.

**RF-19. Estado de la información**
El sistema deberá indicar si la información de un punto de recepción está confirmada o pendiente de confirmar.

> En la Semana 3 se eliminó RF-14 (consulta por categoría) porque su función ya está cubierta por los filtros y la navegación. Su código no se reutiliza.

## Requisitos no funcionales

**RNF-01. Adaptabilidad**
La interfaz deberá adaptarse a computadoras, tabletas y dispositivos móviles.

**RNF-02. Facilidad de uso**
La aplicación deberá contar con una interfaz sencilla, clara y organizada.

**RNF-03. Validación de información**
Los formularios deberán validar los campos obligatorios y los datos ingresados antes de almacenarlos.

**RNF-04. Seguridad**
El sistema deberá utilizar autenticación y control de permisos para restringir el acceso a las funciones correspondientes a cada usuario.

**RNF-05. Protección de datos personales**
La aplicación deberá evitar solicitar o almacenar datos personales que no sean necesarios para su funcionamiento.

**RNF-06. Tecnologías de desarrollo**
La aplicación deberá utilizar Django para el backend, HTML, CSS y JavaScript para la interfaz, SQL Server como sistema gestor de base de datos y una biblioteca de mapas gratuita para el mapa interactivo.

**RNF-07. Rendimiento**
La aplicación deberá responder adecuadamente a las consultas y operaciones habituales.

**RNF-08. Mantenibilidad**
El código deberá mantenerse organizado y estructurado para facilitar futuras modificaciones, correcciones y ampliaciones.

**RNF-09. Gestión de imágenes**
Las fotografías de los reportes deberán limitarse en formato y tamaño, y la base de datos almacenará únicamente su ubicación.

**RNF-10. Escalabilidad territorial**
El sistema deberá permitir agregar nuevos municipios sin modificar la estructura de la base de datos.

## Diseño del sistema

### Clases principales

- **Usuario:** representa a una persona registrada y controla sus permisos según su rol.
- **PuntoRecepcion:** lugar donde se entregan materiales reciclables.
- **Material:** tipo de material reciclable y cómo prepararlo para su entrega.
- **Campania:** campaña o jornada de recolección.
- **Participacion:** inscripción de un usuario a una campaña.
- **RegistroRecoleccion:** cantidad recolectada por material en una campaña.
- **ReporteAmbiental:** problema ambiental reportado por la comunidad.
- **ContenidoEducativo:** información sobre separación y reciclaje.

### Aplicación de Programación Orientada a Objetos

- **Herencia:** los puntos de recepción, las campañas y los reportes comparten una clase base con su ubicación, ya que los tres se muestran en el mapa.
- **Polimorfismo:** cada uno de ellos define a su manera cómo se representa en el mapa, y el mapa los trata a todos por igual.
- **Encapsulamiento:** datos como el estado de un reporte solo se modifican mediante métodos que validan el cambio.
- **Abstracción:** las clases base solo definen lo esencial y no se usan directamente.

### Base de datos

La base de datos sigue un modelo relacional en SQL Server. Sus tablas principales corresponden a usuarios, municipios, organizaciones, materiales, puntos de recepción, campañas, participaciones, registros de recolección, reportes ambientales y contenido educativo.

## Tecnologías propuestas

- Backend: Django
- Frontend: HTML, CSS y JavaScript
- Base de datos: SQL Server
- Mapa: Leaflet con OpenStreetMap
- Control de versiones: Git y GitHub

## Estado del proyecto

Actualmente, el proyecto se encuentra en la etapa de diseño de clases y modelado de la base de datos (Semana 3). Este diseño servirá como base para la configuración del entorno con Django y SQL Server en la Semana 4.
