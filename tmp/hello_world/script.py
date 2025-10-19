import bookmap as bm
from collections import deque

# ============ PARÁMETROS ============
VOLUME_HISTORY_SIZE = 20  # Número de trades para calcular promedio
# ====================================

# Historial de volúmenes por instrumento
volume_history = {}
# IDs de indicadores
volume_indicators = {}
req_id_to_alias = {}
req_id = 1


def handle_trade(addon, alias, price, size, is_otc, is_bid, is_execution_start, is_execution_end, aggressor_order_id, passive_order_id):
    # Inicializar historial si no existe
    if alias not in volume_history:
        volume_history[alias] = deque(maxlen=VOLUME_HISTORY_SIZE)

    # Agregar volumen actual
    volume_history[alias].append(size)

    # Calcular y dibujar volumen total acumulado cada 10 trades
    if len(volume_history[alias]) == VOLUME_HISTORY_SIZE and alias in volume_indicators:
        total_volume = sum(volume_history[alias])
        bm.add_point(addon, alias, volume_indicators[alias], total_volume)


def handle_indicator_response(addon, request_id, indicator_id):
    global volume_indicators, req_id_to_alias
    alias = req_id_to_alias[request_id]
    volume_indicators[alias] = indicator_id


def handle_subscribe_instrument(addon, alias, full_name, is_crypto, pips, size_multiplier, instrument_multiplier, supported_features):
    global req_id, req_id_to_alias

    # Indicador: Volumen total acumulado (blanco, panel inferior)
    req_id += 1
    req_id_to_alias[req_id] = alias
    bm.register_indicator(addon, alias, req_id, "Total Volume", "BOTTOM", color=(255, 255, 255))

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
