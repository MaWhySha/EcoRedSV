# EcoRedSV

## Integrantes
- Robin Christopher Barrera Vasquéz
- Alexis Omar García Romero
- Daniela Ester López Varela
- Liliana Dalila Ulloa González
- Carlos Fernando Guardado García

## Descripción

EcoRedSV es una aplicación web orientada a facilitar la búsqueda y consulta de puntos de reciclaje, permitiendo conocer su ubicación, horarios y materiales que reciben. El proyecto busca organizar esta información y facilitar a las personas la entrega adecuada de materiales reciclables.

Proyecto de Proyección Social  
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

EcoRedSV contempla los siguientes tipos de usuarios:

- **Miembro de la comunidad:** consulta información sobre reciclaje, puntos de recepción y campañas, además de poder registrar reportes.
- **Administrador:** administra usuarios, puntos de recepción, materiales, campañas y reportes.
- **Gestor de residuos o encargado de un punto de recepción:** proporciona y mantiene información relacionada con los materiales, horarios y condiciones de recepción.
- **Institución u organización:** puede gestionar información sobre campañas y actividades relacionadas con reciclaje.
- **Estudiante o voluntario:** consulta y participa en actividades de reciclaje y puede apoyar mediante reportes o actividades comunitarias.

## Requisitos funcionales

### RF-01. Registro de usuarios
El sistema deberá permitir registrar usuarios proporcionando la información necesaria para crear una cuenta y utilizar las funciones correspondientes.

### RF-02. Inicio de sesión
El sistema deberá permitir a los usuarios registrados iniciar sesión para acceder a las funciones disponibles según sus permisos.

### RF-03. Consulta de puntos de recepción
El sistema deberá permitir consultar los puntos de recepción y centros de acopio registrados.

### RF-04. Consulta de información de los puntos
El sistema deberá mostrar la ubicación, horarios, condiciones de entrega y materiales recibidos por cada punto.

### RF-05. Búsqueda y filtrado de puntos
El sistema deberá permitir buscar y filtrar puntos de recepción según criterios como ubicación o tipo de material.

### RF-06. Registro de puntos de recepción
El sistema deberá permitir a los usuarios autorizados registrar nuevos puntos de recepción o centros de acopio.

### RF-07. Actualización de información
El sistema deberá permitir a los usuarios autorizados modificar la información de los puntos registrados.

### RF-08. Registro de campañas y jornadas
El sistema deberá permitir registrar campañas, jornadas o actividades relacionadas con la recolección y reciclaje.

### RF-09. Consulta de campañas y actividades
El sistema deberá permitir consultar las campañas y actividades registradas.

### RF-10. Registro de reportes ambientales
El sistema deberá permitir registrar reportes relacionados con acumulación o disposición inadecuada de residuos.

### RF-11. Gestión de reportes
El sistema deberá permitir a los usuarios autorizados consultar los reportes y actualizar su estado.

### RF-12. Información educativa sobre reciclaje
El sistema deberá permitir consultar información y recomendaciones sobre separación, clasificación y manejo adecuado de residuos.

### RF-13. Administración de registros
El administrador deberá poder gestionar los registros almacenados en el sistema según los permisos establecidos.

### RF-14. Consulta de información por categoría
El sistema deberá permitir organizar y consultar información mediante categorías relacionadas con residuos, puntos, campañas y reportes.

## Requisitos no funcionales

### RNF-01. Adaptabilidad
La interfaz deberá adaptarse a computadoras, tabletas y dispositivos móviles.

### RNF-02. Facilidad de uso
La aplicación deberá contar con una interfaz sencilla, clara y organizada.

### RNF-03. Validación de información
Los formularios deberán validar los campos obligatorios y los datos ingresados antes de almacenarlos.

### RNF-04. Seguridad
El sistema deberá utilizar autenticación y control de permisos para restringir el acceso a las funciones correspondientes a cada usuario.

### RNF-05. Protección de datos personales
La aplicación deberá evitar solicitar o almacenar datos personales que no sean necesarios para su funcionamiento.

### RNF-06. Tecnologías de desarrollo
La aplicación deberá utilizar Django para el backend, HTML, CSS y JavaScript para la interfaz, y SQL Server como sistema gestor de base de datos.

### RNF-07. Rendimiento
La aplicación deberá responder adecuadamente a las consultas y operaciones habituales.

### RNF-08. Mantenibilidad
El código deberá mantenerse organizado y estructurado para facilitar futuras modificaciones, correcciones y ampliaciones.

## Tecnologías propuestas

- **Backend:** Django
- **Frontend:** HTML, CSS y JavaScript
- **Base de datos:** SQL Server
- **Control de versiones:** Git y GitHub

## Estado del proyecto

Actualmente, el proyecto se encuentra en la etapa de diagnóstico de la problemática y definición de requisitos. Los resultados obtenidos servirán como base para el diseño técnico posterior, incluyendo la identificación de entidades, clases y estructura inicial de la base de datos.
