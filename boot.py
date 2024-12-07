from machine import Pin, SPI, UART
from mfrc522 import MFRC522
import time

# Pin configuration for RFID
RST_PIN = 27  # Reset pin
CS_PIN = 5    # Chip select pin
SCK_PIN = 18  # SPI Clock pin
MOSI_PIN = 23 # SPI MOSI pin
MISO_PIN = 19 # SPI MISO pin

# UART configuration for GPS
GPS_TX = 17  # GPS TX pin (connected to ESP RX2)
GPS_RX = 16  # GPS RX pin (connected to ESP TX2)
gps_serial = UART(2, baudrate=9600, tx=GPS_TX, rx=GPS_RX)

# LED pin configuration
LED_PIN = 2  # Use GPIO 2 for the LED
led = Pin(LED_PIN, Pin.OUT)

# Initialize SPI for RFID
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
rfid = MFRC522(spi=spi, gpioRst=RST_PIN, gpioCs=CS_PIN)

def read_gps():
    """Read and process data from the GPS module."""
    try:
        if gps_serial.any():
            line = gps_serial.readline()  # Read a complete line from UART
            if line:
                try:
                    line = line.decode('utf-8')  # Decode as UTF-8
                    print(line.strip())  # Print raw NMEA sentence
                    if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                        print("Relevant GPS data:", line.strip())
                except UnicodeDecodeError:
                    print("GPS decoding error")
    except Exception as e:
        print("GPS read error:", e)

def read_rfid():
    """Poll the RFID module for cards."""
    try:
        # Request for a tag (card)
        (status, tag_type) = rfid.request(rfid.REQIDL)
        if status == rfid.OK:
            print("Card detected")
            # Turn on LED for 2 seconds
            led.value(1)
            time.sleep(2)
            led.value(0)
            
            # Perform anticollision to get UID
            (status, uid) = rfid.anticoll()
            if status == rfid.OK:
                print("Card UID:", [hex(x) for x in uid])
                # Select the scanned card
                if rfid.select_tag(uid) == rfid.OK:
                    print("Card selected successfully")
                # Halt communication with the card
                rfid.halt_a()
    except Exception as e:
        print("RFID read error:", e)

def main():
    print("Starting GPS and RFID...")
    while True:
        read_gps()  # Continuously read GPS data
        read_rfid()  # Poll RFID reader
        time.sleep(0.1)  # Short delay to avoid excessive CPU usage

if __name__ == "__main__":
    main()
