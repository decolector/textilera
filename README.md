textilera
=========


Herramientas para convertir códigos qr en archivos .jef de Janome, para ser bordados en una maquina digital de bordado. Esta basada en [python-showjef](https://bitbucket.org/dboddie/python-showjef) para convertir vectores a puntadas.

##Instalación

Crear un entorno virtual con virtualenv:

    virtualenv --no-site-packages env/

Activarlo:

    source env/bin/activate

Instalar los paquetes usando pip y el archivo de requerimientos: 

Do 
    pip install -r requirements.txt

Si desea usar el conversor svg y el visor de .jef que viene con python-showjef debe instalar PyQt4.  Este paquete no es instalable por pip así que debe ser instalado en el sistema usando su gestor de paquetes preferido o manualmente:

    sudo apt-get install python-qt4

Después puede copiar el modulo en el directorio site-packages del entorno virtual, por ejemplo para debian/ubuntu:

    cp -r /usr/lib/python2.7/dist-packages/PyQt4/ env/lib/python2.7/site-packages

SIP tampoco es instalable con pip, entonces:

    cp /usr/lib/python2.7/dist-packages/sip.so env/lib/python2.7/site-packages/
    cp /usr/lib/python2.7/dist-packages/sipconfig_nd.py env/lib/python2.7/site-packages/
    cp /usr/lib/python2.7/dist-packages/sipconfig.py env/lib/python2.7/site-packages/
    cp /usr/lib/python2.7/dist-packages/sipdistutils.py env/lib/python2.7/site-packages/

Para sacar los mensajes de la base de datos del teléfono necesitamos la aplicación root-adb instalada en el dispositivo. Esta app es necesaria porque la política de permisos de Android nos impide ejecutar comandos como root desde adb. Esta es la url de la app.

https://play.google.com/store/apps/details?id=org.eslack.rootadb

    
##Configuración

La configuración se realiza editando un sencillo archivo xml en el directorio config. Primero haga una copia del template y luego edite esa copia usando su editor de texto preferido. No es buena idea editar el template.

    cp config/config.xml.template config/config.xml
    vim config/config.xml

##Ejecución

En el telefono, activar root-adb, luego conectarlo al computador usando el cable usb. Verificar que haya sido detectado el dispositivo, por ejemplo usando adb:

    ./adb devices

Si no esta activado el entorno virtual:

    source env/bin/activate

Luego ejecutar

    python textilera.py
