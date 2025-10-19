import bookmap as bm
import csv
import os
from datetime import datetime


# Ruta del CSV en el escritorio
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
csv_path = os.path.join(desktop, "bookmap_data.csv")


def handle_trade(addon, alias, price, size, is_otc, is_bid, is_execution_start, is_execution_end, aggressor_order_id, passive_order_id):
    # Cada trade genera una nueva fila en el CSV
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # Timestamp con milisegundos
            alias,
            price,
            size,
            'BID' if is_bid else 'ASK'
        ])


def handle_subscribe_instrument(addon, alias, full_name, is_crypto, pips, size_multiplier, instrument_multiplier, supported_features):
    print("Hello world from Ferran Font " + alias, flush=True)
    print("Features: " + str(supported_features), flush=True)

    # Crear archivo CSV con encabezados si no existe
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Alias', 'Price', 'Size', 'Side'])

    print(f"Registrando handler de trades. CSV: {csv_path}", flush=True)

    # Suscribirse a trades
    bm.subscribe_to_trades(addon, alias, 1)


def handle_unsubscribe_instrument(addon, alias):
    print("Adios world from " + alias, flush=True)


if __name__ == "__main__":
    addon = bm.create_addon()
    # Registrar handler para trades
    bm.add_trades_handler(addon, handle_trade)
    # start addon, requires 3 arguments - addon itself, handler for subscribe event
    # and handler for unsubscribe event
    bm.start_addon(addon, handle_subscribe_instrument,
                   handle_unsubscribe_instrument)
    # block python execution giving control over the script to Bookmap only, so you
    # do not risk, that your script will be turned off earlier that you decide
    bm.wait_until_addon_is_turned_off(addon)
