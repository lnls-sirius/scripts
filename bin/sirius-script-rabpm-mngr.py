#!/usr/bin/env python3

import argparse
import subprocess


def execute_ssh(hostname, *command):
    subprocess.run(["ssh", "-i", "~/.ssh/id_ed25519_rabpm",
                   f"lnls-bpm@{hostname}", *command])


def get_hostname_with_suffix(rack, suffix):
    if rack == "21":
        prefix = "ia-20rabpmtl-co-"
    elif rack.isdigit() and 1 <= int(rack) <= 20:
        prefix = f"ia-{rack.zfill(2)}rabpm-co-"
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


def run_rffe_reset(rack, virtual_slot):
    hostname = get_cpu_hostname(rack)
    execute_ssh(hostname, "rffe-reset", virtual_slot)


def run_boot_from_flash(rack, slot):
    hostname = get_mch_hostname(rack)
    board = "afcv4-sfp" if slot == 2 else "afcv3"
    subprocess.run(
        ["sirius-script-afc-boot-from-flash.sh", board, hostname, str(slot)])


def add_rack_arg(command):
    command.add_argument("-r", "--rack", required=True,
                         help="Rack number {01..20} or 21 for transport line")


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
    parser_reset.add_argument("-v", "--vslot", required=True,
                              help="Virtual slot number to reset(calculated as "
                              "(2*physical_slot-1) or (2*physical_slot))")
    add_rack_arg(parser_reset)

    parser_boot_from_flash = subparsers.add_parser(
        "afc-reset", help="Boot the AFC from flash memory")
    parser_boot_from_flash.add_argument("-s", "--slot", required=True,
                                        help="Slot number")
    add_rack_arg(parser_boot_from_flash)

    args = parser.parse_args()
    if args.command == "afc-list":
        run_pcie_list(args.rack)
    elif args.command == "afc-rescan":
        run_pcie_rescan(args.rack)
    elif args.command == "afc-remove":
        run_pcie_remove(args.rack, args.slot)
    elif args.command == "ioc-restart":
        run_ioc_restart(args.rack, args.ioc, args.slot)
    elif args.command == "rffe-reset":
        run_rffe_reset(args.rack, args.vslot)
    elif args.command == "afc-reset":
        run_boot_from_flash(args.rack, args.slot)


if __name__ == "__main__":
    main()
