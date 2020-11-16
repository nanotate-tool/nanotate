# Nanotate

Herramienta para laa generacion de nanopublicaciones basada en annotaciones realizadas en la plataforma de [hypothesis](https://hypothes.is/).

# Instalacion

para ejecutar esta aplicacion necesitamos instalar las dependencias de `requirements.txt`, para ello necesitamos un virtual enviroment de python. 

```
$ python -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

# Tests

pruebas de annotaciones a nanopublicaciones

## Ejecucion del test
para ejecutar el `test` default ejecutamos:
```
$ python test.py
```
este tomara las anotaciones del archivo [annotation_hypothesis.json](test/annotation_hypothesis.json) y imprimira en pantallas la nanopublicacion en formato `trig`

## Desde un archivo propio
para reproducir las pruebas de `anotaciones` desde un archivo `json` propio a una `nanopublicacion` se debe tener en cuenta:

### Formato del json
el archivo `json` debe cumplir con el siguiente formato

```
[
    {
     "id":"7Z1sugBbEeu9_wtvk1iAjw",
     "authority":"__world__",
     "url":"https://protocolexchange.researchsquare.com/article/pex-1069/v1",
     "created":"2020-09-27T00:53:59.317703+00:00",
     "updated":"2020-09-30T00:39:50.822216+00:00",
     "title":[
        "Sample preparation and imaging procedures for fast and multiplexed superresolution..."
     ],
     "refs":[
     ],
     "isReply":false,
     "isPagenote":false,
     "user":"acct:miguel.ruano@hypothes.is",
     "displayName":null,
     "text":"",
     "prefix":"10 minutes. Wash with PBS3. Add ",
     "exact":"imaging buffer",
     "suffix":"",
     "start":15162,
     "end":15176,
     "tags":[
        "reagent"
     ],
     "group":"__world__",
     "ontologies":[
        "CHEBI"
     ],
     "settings":{
        "bio_annotations":[
           "http://purl.obolibrary.org/obo/CHEBI_35225"
        ]
     }
    },
    ....
]
```
puedes mirar un ejemplo completo en [ejemplo](test/annotation_hypothesis.json)

una vez que tengamos nuestro archivo `json` con las `anotaciones` ejecutaremos:

```
$ python test.py -i <ruta del archivo>
```
y nos imprimira en pantalla las `nanopublicaciones` que de este se puedan generar

para mas opciones del `test` ejecutar :

```
$ python test.py -h
```

Para ejecutar pruebas unitarias ejecutar:

```
$ pytest
```

# Development server

Ejecutar el archivo `run.py` este inicializa un Flask App

```
$ python run.py
```