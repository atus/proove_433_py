import argparse
import logging
from proovepi import Proove

parser = argparse.ArgumentParser(description='Proove switch remote controll.')
parser.add_argument("-p", "--gpio-pin", default=4, type=int, help="GPIO pin")
parser.add_argument("-o", "--off", action="store_true", help="Turn device off, otherwise turn device on")

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-id", "--id", type=int, help="Device id")
group.add_argument("-g", "--group", action="store_true", help="Trigger group, otherwise trigger single device")

args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG)

print args.off
print args.group

pr = Proove(args.gpio_pin)
if not args.off:
    if not args.group:
        pr.channel_on(args.id)
    else:
        pr.group_on()
else:
    if not args.group:
        pr.channel_off(args.id)
    else:
        pr.group_off()

pr.cleanup()
