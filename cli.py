import logging
import argparse
import re

from niimprint import Niimprinter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger("niimprint.cli")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Niimbot printer client")
    parser.add_argument(
        "-a", "--address", required=True, help="MAC address of target device"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity. Add more v's to increase verbosity level. Max 3",
    )

    # command parser
    parser._positionals.title = "commands"
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_info = subparsers.add_parser("info", help="Get printer information")

    parser_rfid = subparsers.add_parser("rfid", help="Get RFID information")

    parser_heartbeat = subparsers.add_parser("heartbeat", help="Send heartbeat")

    parser_print_label = subparsers.add_parser("print_label", help="Print label")

    parser_print_label.add_argument(
        "-q", "--quantity", type=int, default=1, help="Number of copies"
    )
    parser_print_label.add_argument(
        "-w", "--width", type=float, help="Label width in mm (Defaut: 12mm))"
    )
    parser_print_label.add_argument(
        "-l", "--length", type=float, help="Label length in mm (Defaut: 40mm)"
    )
    parser_print_label.add_argument("text", help="Text to print on label (max 2 lines)")

    # @TODO: print image from file
    # parser_print_image = subparsers.add_parser('print_image', help="Print image")
    # parser_print_image.add_argument('image', help="PIL supported image file")
    # parser_print_image.add_argument('-d', '--density', type=int, default=2, help="Printer density (1~3)")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("niimprint.module").setLevel(logging.INFO)
        if args.verbose == 1:
            LOG_LEVEL = logging.INFO
        elif args.verbose == 2:
            LOG_LEVEL = logging.DEBUG
        elif args.verbose >= 3:
            LOG_LEVEL = logging.DEBUG
            logging.getLogger("niimprint.module").setLevel(logging.DEBUG)
        logger.setLevel(LOG_LEVEL)

    if re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", args.address) is None:
        raise ValueError(
            "Invalid MAC address for value of --address. Must be in format XX:XX:XX:XX:XX:XX"
        )

    logger.info("Connecting to %s", args.address)

    printer = Niimprinter(args.address)

    if args.command == "info":
        print(printer.get_info())
    elif args.command == "rfid":
        print(printer.get_rfid())
    elif args.command == "heartbeat":
        print(printer.heartbeat())
    elif args.command == "print_label":
        text = args.text
        print(f"Printing label: {text}")
        if args.width and args.length:
            printer.print_label(text, args.quantity, args.width, args.length)
        else:
            printer.print_label(text, args.quantity)
