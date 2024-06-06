# 📄🔍 Desafío de Extracción de Información de Facturas Eléctricas

¡Bienvenidos a mi repositorio de extracción de información de facturas eléctricas! 🚀
(Prueba técnica para Decides)

Este proyecto tiene como objetivo desarrollar una solución genérica para extraer información clave de facturas eléctricas en formato PDF, independientemente del diseño o la disposición de los campos en las diferentes facturas. 🧠💡

## 📚 Pasos del Proyecto

### 1. Recopilación de Recursos

- ✅ Instalación de Python en mi ordenador.
- ✅ Descarga del dataset de entrenamiento con facturas PDF y sus correspondientes archivos JSON.
- ✅ Selección de librerías de Python adecuadas para la extracción de texto, procesamiento de texto y aprendizaje automático.

### 2. Preprocesamiento de Datos

- 📥 Lectura de los archivos PDF y JSON del dataset de entrenamiento.
- 🧹 Limpieza del texto extraído, eliminando caracteres irrelevantes y normalizando el texto.
- 📑 Estructuración de los datos para facilitar su procesamiento.

### 3. Exploración y Análisis de Datos

- 🔍 Análisis de la estructura y el contenido de las facturas PDF y JSON.
- 📊 Identificación de patrones y características comunes, así como variaciones en los formatos de las facturas.
- 🗂 Segmentación de los datos en diferentes grupos según sus características.

### 4. Definición de la Estrategia de Extracción

- 🛠 Decisión entre un enfoque basado en reglas o un modelo de aprendizaje automático.
  - **Enfoque basado en reglas:** Definición de reglas manuales utilizando expresiones regulares y técnicas de procesamiento del lenguaje natural.
  - **Enfoque basado en aprendizaje automático:** Entrenamiento de un modelo adecuado y evaluación de su rendimiento.

### 5. Implementación de la Solución

- 💻 Implementación del algoritmo de extracción de información.
- 🔄 Desarrollo de la lógica para procesar cada factura PDF y almacenar la información en un formato estructurado.
- 🚨 Manejo de errores y casos excepcionales.

### 6. Evaluación y Mejora

- 🧪 Evaluación del rendimiento utilizando el script proporcionado para obtener el score de Levenshtein.
- 🔄 Refinamiento de la estrategia de extracción en base a los resultados obtenidos.
- ♻ Repetición del proceso de evaluación y mejora hasta alcanzar un score satisfactorio.

### 7. Consideraciones Adicionales

- 🌐 Aseguramiento de la generalización del método de extracción para diferentes formatos y estructuras de facturas.
- 🛠 Utilización de técnicas de procesamiento del lenguaje natural para mejorar la precisión.
- 📋 Implementación de mecanismos para manejar errores y casos excepcionales.
- 📝 Documentación del código y la estrategia de extracción.

## 🛠 Tecnologías Utilizadas

- **Python** 🐍
- **PyPDF2 / Poppler / pdfminer.six** 📄
- **re / string / nltk** 🔍
- **scikit-learn / TensorFlow** 🤖

## 🚀 Cómo Empezar

1. Clona este repositorio:
    ```bash
    git clone https://github.com/tuusuario/extraccion-facturas-electricas.git
    ```
2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3. Ejecuta el script de extracción:
La factura que quieres procesar debe estar en el mismo directorio que el script "ejecutable" que está en la carpeta ./dist
    ```bash
    ./ejecutable.exe nombre_factura.pdf
    ```
    o
    ```bash
    ./ejecutable.exe path_factura
    ```

## 📞 Contacto

¿Tienes preguntas o sugerencias? No dudes en contactarme en [LinkedIn](https://www.linkedin.com/in/tuperfil) 💬

¡Gracias por visitar mi repositorio! Espero que encuentres este proyecto interesante y útil. 🙌

---

⭐ **Si te gustó este proyecto, por favor dale una estrella y sígueme en LinkedIn para más contenido similar.** ⭐
