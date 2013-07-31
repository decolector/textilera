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


###Archivo de configuración

Significado de las entradas en el archivo de configuración.

Aquí va el puerto serial:

    <serial_port>/dev/ttyACM0</serial_port>

También puede especificar un patrón de puerto serial para detección automática del puerto, por ejemplo cuando cambia frecuentemente la numeración, serial_port tiene prioridad sobre este parámetro:

    <serial_port_pattern>/dev/ttyACM</serial_port_pattern>

Directorio donde va a residir el archivo que leerá la maquina de bordar, lo mas posible es que sea una partición desde la que se emula una unidad externa por usb.

    <out_dir>out/</out_dir>

En este directorio se guardan los archivos generados pero que no han sido bordados

    <queue_dir>queue/</queue_dir>

En este directorio se guardan todos los archivos generados, tanto los .jef como los png

    <backup_dir>archive/</backup_dir>

Ruta al directorio donde se encuentra la herramienta adb.

    <adb_path>/path/to/android-sdk/platform-tools/adb</adb_path>

Ruta en el teléfono de la base de datos de mensajes, en las diferentes versiones de android es la misma ruta, así que normalmente no tendría porque cambiar este parámetro.

    <remote_sms_db>/data/data/com.android.providers.telephony/databases/mmssms.db</remote_sms_db>

Ruta donde se va a copiar la base de datos para ser usada por la aplicación.

    <local_sms_db>db/</local_sms_db>


*Configuraciones para el bordado*

Longitud máxima de puntada, el máximo valor permitido por el conversor es 127.0, el valor debe ser un float. La unidad esta dada en unidades .jef .

    <max_stitch_length>100.0</max_stitch_length>

El ancho en unidades .jef de cada celda del qr.

    <unit_width>100</unit_width>

Lo mismo, para el alto de la celda

    <unit_height>100</unit_height>

Cantidad de líneas que van a rellenar cada celda del qr, este valor determina la "densidad" del relleno del qr.

    <step>10</step>

##Ejecución

En el teléfono, activar root-adb, luego conectarlo al computador usando el cable usb. Verificar que haya sido detectado el dispositivo, por ejemplo usando adb:

    ./adb devices

Si no esta activado el entorno virtual:

    source env/bin/activate

Luego ejecutar

    python textilera.py
