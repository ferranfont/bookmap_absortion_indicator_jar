import bookmap as bm
from collections import deque

# ============ PARÁMETROS ============
VOLUME_HISTORY_SIZE = 20  # Número de trades para calcular promedio
ABSORPTION_RATIO = 3.0    # Ratio mínimo para detectar absorción
# ====================================

# Historial de volúmenes por instrumento
volume_history = {}
# Contadores de absorción (últimos N trades)
ask_volume = {}  # Compras agresivas
bid_volume = {}  # Ventas agresivas
# IDs de indicadores
volume_indicators = {}
absorption_indicators = {}
req_id_to_alias = {}
req_id = 1


def handle_trade(addon, alias, price, size, is_otc, is_bid, is_execution_start, is_execution_end, aggressor_order_id, passive_order_id):
    # Inicializar estructuras si no existen
    if alias not in volume_history:
        volume_history[alias] = deque(maxlen=VOLUME_HISTORY_SIZE)
        ask_volume[alias] = 0
        bid_volume[alias] = 0

    # Agregar volumen actual
    volume_history[alias].append(size)

    # Acumular volumen por lado
    if is_bid:
        bid_volume[alias] += size
    else:
        ask_volume[alias] += size

    # Calcular indicadores solo cuando se completa la ventana
    if len(volume_history[alias]) == VOLUME_HISTORY_SIZE:
        # 1. Dibujar volumen total
        if alias in volume_indicators:
            total_volume = sum(volume_history[alias])
            bm.add_point(addon, alias, volume_indicators[alias], total_volume)

        # 2. Detectar absorción
        if alias in absorption_indicators:
            ask_vol = ask_volume[alias]
            bid_vol = bid_volume[alias]

            # Absorción en ASK: muchas compras, pocas ventas
            if bid_vol > 0 and ask_vol / bid_vol >= ABSORPTION_RATIO:
                bm.add_point(addon, alias, absorption_indicators[alias], price)

            # Absorción en BID: muchas ventas, pocas compras
            elif ask_vol > 0 and bid_vol / ask_vol >= ABSORPTION_RATIO:
                bm.add_point(addon, alias, absorption_indicators[alias], price)

        # Resetear contadores
        ask_volume[alias] = 0
        bid_volume[alias] = 0


def handle_indicator_response(addon, request_id, indicator_id):
    global volume_indicators, absorption_indicators, req_id_to_alias
    alias, indicator_type = req_id_to_alias[request_id]

    if indicator_type == "volume":
        volume_indicators[alias] = indicator_id
    elif indicator_type == "absorption":
        absorption_indicators[alias] = indicator_id


def handle_subscribe_instrument(addon, alias, full_name, is_crypto, pips, size_multiplier, instrument_multiplier, supported_features):
    global req_id, req_id_to_alias

    # Indicador 1: Volumen total acumulado (blanco, panel inferior)
    req_id += 1
    req_id_to_alias[req_id] = (alias, "volume")
    bm.register_indicator(addon, alias, req_id, "Total Volume", "BOTTOM", color=(255, 255, 255))

    # Indicador 2: Absorción (amarillo, overlay)
    req_id += 1
    req_id_to_alias[req_id] = (alias, "absorption")
    bm.register_indicator(addon, alias, req_id, "Absorption", "OVERLAY", color=(255, 255, 0))

    # Suscribirse a trades
    bm.subscribe_to_trades(addon, alias, 1)


def handle_unsubscribe_instrument(addon, alias):
    pass


if __name__ == "__main__":
    addon = bm.create_addon()
    bm.add_trades_handler(addon, handle_trade)
    bm.add_indicator_response_handler(addon, handle_indicator_response)
    bm.start_addon(addon, handle_subscribe_instrument, handle_unsubscribe_instrument)
    bm.wait_until_addon_is_turned_off(addon)
