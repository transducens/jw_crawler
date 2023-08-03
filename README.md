# JW Crawler
Debido a la intransigencia de los Testigos de Jehová, nos vemos obligados a implementar [nuestro propio](https://gitlab.com/Feasinde/jw_crawler) *crawler* para extraer los invaluables *corpora* paralelos de [JW.org](https://www.jw.org/es/).

La estrategia actual, que puede ser refinada más adelante, consiste en utilizar el archivo [`sitemap.xml`](https://www.jw.org/es/sitemap.xml) de la versión en español del sitio para visitar todos los URLs contenidos en este y comprobar si existen versiones en las diez lenguas mayas en las que nos enfocamos (cak, kek, mam, kjb, ctu, quc, poh, tzh, tzo, yua). La estrategia podría expandirse para comenzar desde otros idiomas con *corpora* grandes, como el inglés.

## Por hacer
- [x] Incluir un listado de strings que deban ser excluidos de los URLs recopilados
- [ ] Incluir un listado de strings en los que haya que enfocarse para reducir el número de URLs recopilados, eg `"noticias"`, para que el *crawler* se enfoque en noticias
- [ ] Codificar una CLI
- [ ] Elucidar la estructura en común que tienen las páginas en múltiples idiomas.
	- Actualmente, parece ser que las etiquetas de la forma  `<p id='px'>` corresponden a textos paralelos.  
- [ ] Funcionalidad para pausar y retomar el *crawling* una vez comenzado.
	- Guardar el progreso cada cierto tiempo o cada cierto número de documentos procesados.