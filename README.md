# (WIP) Niimbot printer client

A module + cli-tool to interact with Niimbot printers.

To use this module you need to know the MAC address of the target device.
To find the MAC-address, you can use a tool like [BluetoothView from NirSoft](https://www.nirsoft.net/utils/bluetooth_viewer.html) on Windows or `bluetoothctl` on Linux.

## Supported printers

- D11

## Usage CLI-tool

Download this repository and install the requirements:

```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
```

All commands require that you specify the MAC address of the target device with the `-a` or `--address` flag.

To print a label with the text "Hello World from Niimbot!", run:

```bash
python3 cli.py -a <mac-address> print_label "Hello World from Niimbot!"
```

For more information about the CLI-tool, run:

### Help


Full help for the CLI-tool can be found by running `python3 cli.py -h`
```bash
usage: cli.py [-h] -a ADDRESS [-v] {info,rfid,heartbeat,print_label} ...

Niimbot printer client

commands:
  {info,rfid,heartbeat,print_label}
    info                Get printer information
    rfid                Get RFID information
    heartbeat           Send heartbeat
    print_label         Print label

options:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        MAC address of target device
  -v, --verbose         Increase verbosity. Add more v's to increase verbosity level. Max 3

```

To get help for a specific command, run:

```bash
python3 cli.py <command> -h
```
