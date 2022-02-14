# Using the MH-Z19 on a Raspberry Pi Pico

This code should work on both the MH-Z19B and MH-Z19C CO2 sensors, although
it was only tested with the MH-Z19C. There are no dependencies.
I've never written similar code, hence PRs are particularly welcome.
The implementation is based on
[UedaTakeyuki/mh-z20](https://github.com/UedaTakeyuki/mh-z19)
which didn't work for the Pico out of the box.

## Usage
Copy this module on your Pico, import it to your program, instantiate the
sensor class and read the CO2 value. For example:

```python
from mh_z19 import MH_Z19
sensor = MH_Z19(Pin(UART_TX_PIN), Pin(UART_RX_PIN))
print(sensor.read_co2())
```

## License
MIT, see the [LICENSE](LICENSE) file.
