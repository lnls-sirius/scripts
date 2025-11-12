#!/usr/bin/env python3

import argparse
import subprocess
import os
import shlex


class SSHAgent():
    def __enter__(self):
        self.agent = subprocess.Popen(
            ['ssh-agent', '-D'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        agent_output = self.agent.stdout.readline().decode('ascii')
        self.ssh_auth_sock = shlex.split(agent_output)[0].strip(';').split('=')
        os.environ.update({self.ssh_auth_sock[0]: self.ssh_auth_sock[1]})

        # Use shell=True, so the tilde (~) is correctly expanded by having the
        # shell interpret the command. The command must be a string instead of a
        # list so it becomes a single argument to `/bin/sh -c`.
        # This is needed for ssh-add but not ssh, since it expands ~.
        # That is why shell=True is not necessary in launch_ssh.
        subprocess.run("ssh-add ~/.ssh/id_ed25519_rabpm", shell=True)

    def __exit__(self, *args, **kwargs):
        self.agent.terminate()


class RABPMMngr():
    def __enter__(self):
        return self

    def __init__(self):
        self.procs = []

    def _launch_ssh(self, hostname, *command):
        self.procs.append(subprocess.Popen(
            ["ssh", "-i", "~/.ssh/id_ed25519_rabpm",
                f"lnls-bpm@{hostname}", *command],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    def _get_hostname_with_suffix(self, rack, suffix):
        if rack == 21:
            prefix = "ia-20rabpmtl-co-"
        elif 1 <= rack <= 20:
            prefix = f"ia-{rack:02d}rabpm-co-"
        else:
            raise ValueError("Invalid rack number")

        return prefix + suffix

    def _get_cpu_hostname(self, rack):
        return self._get_hostname_with_suffix(rack, "iocsrv")

    def _get_mch_hostname(self, rack):
        return self._get_hostname_with_suffix(rack, "cratectrl")

    def run_pcie_list(self, rack):
        hostname = self._get_cpu_hostname(rack)
        self._launch_ssh(hostname, "pcie-list-slots")

    def run_pcie_rescan(self, rack):
        hostname = self._get_cpu_hostname(rack)
        self._launch_ssh(hostname, "pcie-rescan")

    def run_pcie_remove(self, rack, slot):
        hostname = self._get_cpu_hostname(rack)
        self._launch_ssh(hostname, "pcie-remove", slot)

    def run_ioc_restart(self, rack, ioc, slot):
        hostname = self._get_cpu_hostname(rack)
        self._launch_ssh(hostname, "ioc-restart", ioc, slot)

    def run_rffe_reset(self, rack, virtual_slots):
        hostname = self._get_cpu_hostname(rack)
        for vslot in virtual_slots:
            self._launch_ssh(hostname, "rffe-reset", str(vslot))

    def _conv_device_2_slots(dev):
        if dev == "timing":
            slots = [1]
        elif dev == "fofb":
            slots = [2]
        elif dev == "bpm":
            slots = range(4, 13)
        elif dev == "all":
            slots = range(1, 13)
        else:
            raise ValueError(f'Unsuported device type: {dev}')

        return slots

    def run_boot_from_flash(self, rack, slots, batch):
        if isinstance(slots, str):
            self._conv_device_2_slots(slots)

        hostname = self._get_mch_hostname(rack)

        for slot in slots:
            board = "afcv4-sfp" if slot == 2 else "afcv3"
            subprocess.run(
                ["sirius-script-afc-boot-from-flash.sh", board, hostname, str(slot)])

    def __exit__(self, *args, **kwargs):
        for p in self.procs:
            p.wait()


def add_rack_arg(command):
    command.add_argument("-r", "--racks", required=True,
                         nargs="+", action=ValidateDeviceList, all_devices=list(range(1, 22)),
                         help="Rack numbers {01..21} (21 for transport line) or 'all'")


class ValidateDeviceList(argparse.Action):
    def __init__(self, option_strings, all_devices, *args, **kwargs):
        self._all_devices = all_devices
        super(ValidateDeviceList, self).__init__(
            option_strings=option_strings, *args, **kwargs)

    def __call__(self, parser, args, values, option_string=None):
        if (len(values) == 1 and values[0] == "all"):
            values = self._all_devices

        else:
            try:
                values = list(map(int, values))
            except ValueError:
                raise ValueError(
                    "Invalid rack argument. Use --help for valid options.")
        setattr(args, self.dest, values)


def main():
    parser = argparse.ArgumentParser(prog="sirius-script-rabpm-mngr",
                                     description="BPM Rack Management Utility")

    subparsers = parser.add_subparsers(dest="command", required=True,
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
                              nargs="+", action=ValidateDeviceList, all_devices=list(range(11, 24)),
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

    with SSHAgent():
        with RABPMMngr() as mngr:
            for rack in args.racks:
                if args.command == "afc-list":
                    mngr.run_pcie_list(rack)
                elif args.command == "afc-rescan":
                    mngr.run_pcie_rescan(rack)
                elif args.command == "afc-remove":
                    mngr.run_pcie_remove(rack, args.slot)
                elif args.command == "ioc-restart":
                    mngr.run_ioc_restart(rack, args.ioc, args.slot)
                elif args.command == "rffe-reset":
                    mngr.run_rffe_reset(rack, args.vslots)
                elif args.command == "afc-reset":
                    mngr.run_boot_from_flash(rack, args.slots)


if __name__ == "__main__":
    main()
