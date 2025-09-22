#!/usr/bin/env python3

import argparse
import subprocess
import sys


def execute_ssh(hostname, *command):
    subprocess.run(["ssh", "-i", "~/.ssh/id_ed25519_rabpm",
                   f"lnls-bpm@{hostname}", *command])


def get_hostname_with_suffix(rack, suffix):
    if rack == 21:
        prefix = "ia-20rabpmtl-co-"
    elif 1 <= rack <= 20:
        prefix = f"ia-{rack:02d}rabpm-co-"
    else:
        raise ValueError("Invalid rack number")

    return prefix + suffix


def get_cpu_hostname(rack):
    return get_hostname_with_suffix(rack, "iocsrv")


def get_mch_hostname(rack):
    return get_hostname_with_suffix(rack, "cratectrl")


def run_pcie_list(rack):
    hostname = get_cpu_hostname(rack)
    execute_ssh(hostname, "pcie-list-slots")


def run_pcie_rescan(rack):
    hostname = get_cpu_hostname(rack)
    execute_ssh(hostname, "pcie-rescan")


def run_pcie_remove(rack, slot):
    hostname = get_cpu_hostname(rack)
    execute_ssh(hostname, "pcie-remove", slot)


def run_ioc_restart(rack, ioc, slot):
    hostname = get_cpu_hostname(rack)
    execute_ssh(hostname, "ioc-restart", ioc, slot)


def run_rffe_reset(rack, virtual_slots):
    hostname = get_cpu_hostname(rack)
    for vslot in virtual_slots:
        execute_ssh(hostname, "rffe-reset", str(vslot))


def run_boot_from_flash(rack, slots):
    try:
        if isinstance(slots, str):
            slots = conv_device_2_slots(slots)
    except ValueError as err:
        print("Unable to perform boot from flash:", err)
        sys.exit(1)

    hostname = get_mch_hostname(rack)
    for slot in slots:
        board = "afcv4-sfp" if slot == 2 else "afcv3"
        subprocess.run(
            ["sirius-script-afc-boot-from-flash.sh", board, hostname, str(slot)])


def conv_device_2_slots(dev):
    if dev == "timing":
        slots = [1]
    elif dev == "fofb":
        slots = [2]
    elif dev == "bpm":
        slots = range(4, 13)
    elif dev == "all":
        slots = range(1, 13)
    else:
        raise ValueError(f'Unsupported device type: {dev}')

    return slots


def add_rack_arg(command):
    command.add_argument("-r", "--racks", required=True,
                         nargs="+", action=ValidateDeviceListAction, all_devices=list(range(1, 22)),
                         help="Rack numbers {01..21} (21 for transport line) or 'all'")


class ValidateDeviceListAction(argparse.Action):
    def __init__(self, all_devices, *args, **kwargs):
        self._all_devices = all_devices
        super(ValidateDeviceListAction, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 1 and values[0] == "all":
            values = self._all_devices

        else:
            try:
                values = list(map(int, values))
            except ValueError as err:
                parser.print_help()
                parser.exit(
                    status=1, message=f"Invalid device argument: {err}\n")
        setattr(namespace, self.dest, values)


def main():
    parser = argparse.ArgumentParser(prog="sirius-script-rabpm-mngr",
                                     description="BPM Rack Management Utility")

    subparsers = parser.add_subparsers(dest="command",
                                       help="Available commands")

    parser_list = subparsers.add_parser("afc-list",
                                        help="List active PCIe physical slots (AMC cards)")
    add_rack_arg(parser_list)

    parser_rescan = subparsers.add_parser("afc-rescan",
                                          help="Rescan PCIe buses")
    add_rack_arg(parser_rescan)

    parser_remove = subparsers.add_parser("afc-remove",
                                          help="Remove PCIe physical slot")
    parser_remove.add_argument("-s", "--slot", required=True,
                               help="Slot number to remove")
    add_rack_arg(parser_remove)

    parser_restart = subparsers.add_parser("ioc-restart",
                                           help="Restart AFC or RFFE IOCs")
    parser_restart.add_argument("ioc", choices=["afc", "rffe"],
                                help="IOC to restart (afc or rffe)")
    parser_restart.add_argument("-s", "--slot", required=True,
                                help="Slot number")
    add_rack_arg(parser_restart)

    parser_reset = subparsers.add_parser("rffe-reset",
                                         help="Reset RFFE")
    parser_reset.add_argument("-v", "--vslots", required=True,
                              nargs="+", action=ValidateDeviceListAction, all_devices=list(range(11, 24)),
                              help="Virtual slot numbers to reset(calculated as "
                              "(2*physical_slot-1) or (2*physical_slot))")
    add_rack_arg(parser_reset)

    parser_boot_from_flash = subparsers.add_parser(
        "afc-reset", help="Boot the AFC from flash memory")
    group = parser_boot_from_flash.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--slots", nargs="+", type=int,
                       help="Slot numbers")
    group.add_argument("--device", choices=['timing', 'fofb', 'bpm', 'all'], dest='slots',
                       help="Reset a batch of specified afc devices (timing, fofb or bpm) or all")
    add_rack_arg(parser_boot_from_flash)

    args = parser.parse_args()

    for rack in args.racks:
        if args.command == "afc-list":
            run_pcie_list(rack)
        elif args.command == "afc-rescan":
            run_pcie_rescan(rack)
        elif args.command == "afc-remove":
            run_pcie_remove(rack, args.slot)
        elif args.command == "ioc-restart":
            run_ioc_restart(rack, args.ioc, args.slot)
        elif args.command == "rffe-reset":
            run_rffe_reset(rack, args.vslots)
        elif args.command == "afc-reset":
            run_boot_from_flash(rack, args.slots)


if __name__ == "__main__":
    main()
