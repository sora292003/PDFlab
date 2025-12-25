# PDFlab

**Herramienta de escritorio para la gestión, fusión y optimización de documentos PDF.**

Esta aplicación permite combinar múltiples archivos PDF en un único documento de forma local, garantizando la privacidad de los datos al no requerir subidas a servidores externos. Diseñada para ofrecer un flujo de trabajo rápido y eficiente en entornos Windows.

![Estado](https://img.shields.io/badge/Estado-Estable-success) ![Plataforma](https://img.shields.io/badge/Plataforma-Windows-blue) ![Versión](https://img.shields.io/badge/Versión-12.0-lightgrey)

## Funcionalidades Principales

* **Fusión de Documentos:** Unificación de múltiples archivos PDF en un solo archivo resultante.
* **Sistema Drag & Drop:** Soporte nativo para arrastrar y soltar archivos. Incluye filtrado automático de archivos no válidos.
* **Generación de Índice:** Creación automática de una tabla de contenidos (TOC) con referencias a las páginas de inicio de cada documento.
* **Separadores y Numeración:** Opción para insertar páginas separadoras con títulos y renumeración automática de capítulos.
* **Optimización:** Algoritmo de compresión integrado para reducir el tamaño del archivo final.
* **Persistencia de Configuración:** El sistema guarda automáticamente las preferencias del usuario (rutas, opciones de visualización y parámetros de fusión) entre sesiones.
* **Interfaz Adaptable:** Soporte para Modo Oscuro y diferentes temas visuales para adaptarse al entorno de trabajo.

## Instrucciones de Uso

1.  Ejecute el archivo `PDFlab.exe`.
2.  Importe los documentos PDF arrastrándolos a la lista principal o utilizando el botón "Añadir Archivos".
3.  Organice el orden de los documentos mediante los controles de desplazamiento.
4.  Seleccione las opciones de procesamiento deseadas (Índice, Compresión, etc.).
5.  Pulse "Ejecutar Fusión" para procesar los documentos.

## Requisitos del Sistema

* **Sistema Operativo:** Windows 10 / 11.
* **Instalación:** No requiere instalación (Software Portable).

## Información Técnica

Desarrollado en Python. Utiliza las siguientes librerías para su funcionamiento:
* `CustomTkinter` (Interfaz gráfica)
* `PyPDF` (Manipulación de PDF)
* `ReportLab` (Generación de gráficos y texto)
* `TkinterDnD` (Funcionalidad de arrastrar y soltar)

---
**Licencia:** Software de uso gratuito.
