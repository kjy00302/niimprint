# (WIP) Niimbot printer client

    usage: niimprint [-h] -a ADDRESS [--no-check] [-d DENSITY] [-t TYPE] [-n QUANTITY] image

    Niimbot printer client

    positional arguments:
    image                 PIL supported image file

    options:
    -h, --help            show this help message and exit
    -a ADDRESS, --address ADDRESS
                            MAC address of target device
    --no-check            Skips image check
    -d DENSITY, --density DENSITY
                            Printer density (1~3)
    -t TYPE, --type TYPE  Label type (1~3)
    -n QUANTITY, --quantity QUANTITY
                            Number of copies
