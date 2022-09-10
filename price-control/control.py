import asyncio
import datetime as dt
import os
import paho.mqtt.publish as publish
import sys
import tibber
from time import sleep

"""
From: https://developer.tibber.com/docs/reference#pricelevel

PriceLevel
Price level based on trailing price average (3 days for hourly values and 30 days for daily values)

VERY_CHEAP: The price is smaller or equal to 60 % compared to average price.
CHEAP: The price is greater than 60 % and smaller or equal to 90 % compared to average price.
NORMAL: The price is greater than 90 % and smaller than 115 % compared to average price.
EXPENSIVE: The price is greater or equal to 115 % and smaller than 140 % compared to average price.
VERY_EXPENSIVE: The price is greater or equal to 140 % compared to average price.
"""

async def main(dry_run: bool):
    while True:
        tibber_connection = tibber.Tibber(access_token)
        await tibber_connection.update_info()
        print("Tibber user:", tibber_connection.name)
        homes = tibber_connection.get_homes()
        if len(homes) == 0:
            sys.stderr.write("No tibber homes found")
            sys.exit(1)
        home = tibber_connection.get_homes()[0]
        await home.update_info()
        if len(homes) > 1:
            print("Using home address:", home.address1)
        await home.update_price_info()
        await tibber_connection.close_connection()

        old_price_level = ""
        now = dt.datetime.utcnow().astimezone(dt.timezone.utc)
        print("Todays and next 12 hours prices:")
        for key in home.price_level:
            if dt.datetime.fromisoformat(key).astimezone(dt.timezone.utc) <= now + dt.timedelta(hours=12):
                now_price_level = home.price_level[key]
                if now_price_level != old_price_level:
                    print(key, '->', home.price_level[key], home.price_total[key], 'kr')
                    old_price_level = now_price_level

        start_day = dt.datetime.utcnow().day
        old_price_level = ""
        print("Controlling away_mode:")
        while True:
            now = dt.datetime.utcnow()
            now_hour = dt.datetime(now.year, now.month, now.day, now.hour, tzinfo=dt.timezone.utc)
            now_price_level = ""
            for key in home.price_level:
                if dt.datetime.fromisoformat(key).astimezone(dt.timezone.utc) == now_hour:
                    now_price_level = home.price_level[key]
                    if now_price_level != old_price_level:
                        print(key, '->', home.price_level[key])
                        old_price_level = now_price_level
                    break;

            if not dry_run:
                # VK Entré
                if now_price_level == "VERY_CHEAP":
                    payload = '{"away_mode":"OFF"}'
                else:
                    payload = '{"away_mode":"ON"}'
                publish.single("zigbee2mqtt/0x1fff0001000001f2/set", payload, hostname=mqtt_server)

                if now_price_level == "VERY_CHEAP" or now_price_level == "CHEAP":
                    payload = '{"away_mode":"OFF"}'
                else:
                    payload = '{"away_mode":"ON"}'
                # VK Bad (kjeller)
                sleep(3)
                publish.single("zigbee2mqtt/0x1fff000100000220/set", payload, hostname=mqtt_server)

                # VK Bad (2. etg)
                if now_price_level == "VERY_CHEAP" or now_price_level == "CHEAP" or now_price_level == "NORMAL":
                    payload = '{"away_mode":"OFF"}'
                else:
                    payload = '{"away_mode":"ON"}'
                sleep(3)
                publish.single("zigbee2mqtt/0x1fff000100000217/set", payload, hostname=mqtt_server)

                sleep(60)
                if start_day != now.day:
                    break
            else:
                sys.exit(0)

if __name__ ==  '__main__':
    access_token = os.environ.get('TIBBER_TOKEN', tibber.DEMO_TOKEN)
    mqtt_server = os.environ.get('MQTT_SERVER', 'mqtt')
    dry_run = len(sys.argv) > 1 and sys.argv[1] == '--dry'

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(dry_run))
