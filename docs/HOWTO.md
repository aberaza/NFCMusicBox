
1. Bajar raspbian ISO y extraer el archivo _.img_
2. Quemar la imagen en una microsd
	* Insertar la microsd y averiguar el dispositivo (df -h o app disks)
	* Supongamos que es /dev/sda (y la partición en sda1)
	* desmontar `sudo umount /dev/sda1`
	* quemar con 
```
sudo dd bs=4M if=/path/to/raspbian/image.img of=/dev/sda
```
	* al terminar, ejecutar `sync`para asegurarnos de que no hay caches de escritura sin sincronizar
		
3. Activar SSH: crear un archivo llamado `ssh` (sin extension) en `boot/`
4. Configurar WIFI: editar archivo `rootfs/etc/wpa_supplicant/wpa_supplicant.conf` que quede tal que:
```
country=ES
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
        ssid="MOVISTAR_2406"
        psk="uP96xmFFC7GX5k5U3vhh"
        scan_ssid=1
}
```

5. Activar acceso por USB: en el archivo `boot/config.txt` añadir la liniea
```
dtoverlay=dwc2
```
y posteriormente en 'boot/cmdline.txt' añadir `modules-load=dwc2,g_ether`y que quede similar a 
```
console=serial0,115200 console=tty1 root=PARTUUID=aebb0a02-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait load=dwc2,g_ether
```

6. Arrancar la raspberry y ssh a ella:
	* Normalmente el nombre es _raspberry.local_ Si no se encuentra, con `arp -n -a` escanearemos las ips conectadas
	(la mac de raspberry es siempre del estilo *b8:28:xx:xx:xx:xx*)
	* `ssh pi@raspberrypi.local` password `raspberry`
	
7. PRIMEROS PASOS:
	* `sudo raspi-config` Para configurar lo que necesitemos
	* `apt-get update upgrade`
	* `sudo rpi-update` -> update pi firmware
	* instalar pip `sudo apt install python3-pip`
	* Desactivar la tarjeta de audio de la raspberry: editar `boot/config.txt`y comentar:
```
# Enable audio (loads snd_bcm2835)
#dtparam=audio=on
```

8. Instalar Mopidy

`apt-get install mopidy`
Seguir estas instrucciones:
https://docs.mopidy.com/en/latest/installation/raspberrypi/

8.1. Instalar Spotify 
```
wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list

sudo apt-get updatesudo apt-get install python3-spotify libspotify12

sudo python3 -m pip install Mopidy-Spotify

```

o mejor seguir esto:
https://github.com/mopidy/mopidy-spotify

8.2 Instalar MPD `sudo python3 -m pip install Mopidy-MPD`

8.3 Instalar Frontend WEB `sudo python3 -m pip install Mopidy-Iris`

9. Instalar dependencias
```
libnfc-bin libnfc5 libnfc-examples
sudo apt install python3-gpiozero
sudo pip3 install pn532pi python-mpd2 
```

Para el lector nfc pn5332: editar /etc/nfc/libnfc.conf
''' 
device.name = "PN532 over I2C"
device.connstring = "pn532_i2c:/dev/i2c-1"

'''


	

