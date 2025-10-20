import bookmap as bm
from collections import deque

# ============ PARÁMETROS ============
WINDOW_SIZE = 20  # Ventana flotante de últimos N trades
SPIKE_MULTIPLIER = 2.0  # Multiplicador para detectar spike
SPIKE_AVG_WINDOW = 14  # Promedio de últimos N trades para spike
# ====================================

# Contadores
ask_volume = {}  # Compras agresivas (acumulado continuo para initiation)
bid_volume = {}  # Ventas agresivas (acumulado continuo para initiation)
bid_volume_window = {}  # Ventas agresivas (ventana flotante de últimos 20)
# Contadores para agresion (se resetean con spike)
ask_volume_agresion = {}
bid_volume_agresion = {}
# IDs de indicadores
volume_indicators = {}
initiation_indicators = {}
agresion_indicators = {}
only_ask_indicators = {}
req_id_to_alias = {}
req_id = 1


def handle_trade(addon, alias, price, size, is_otc, is_bid, is_execution_start, is_execution_end, aggressor_order_id, passive_order_id):
    # Inicializar estructuras
    if alias not in ask_volume:
        ask_volume[alias] = 0
        bid_volume[alias] = 0
        bid_volume_window[alias] = deque(maxlen=WINDOW_SIZE)
        ask_volume_agresion[alias] = 0
        bid_volume_agresion[alias] = 0

    # Detectar spike en cum_bid_vol ANTES de acumular
    spike_detected = False
    spike_marker_value = 0
    if not is_bid and len(bid_volume_window[alias]) >= SPIKE_AVG_WINDOW:
        # Calcular promedio de últimos 14 trades
        recent_volumes = list(bid_volume_window[alias])[-SPIKE_AVG_WINDOW:]
        avg_volume = sum(recent_volumes) / len(recent_volumes)

        # Detectar spike si el trade actual es >= 2x el promedio
        if size >= avg_volume * SPIKE_MULTIPLIER:
            spike_detected = True
            # Guardar valor actual de imbalance antes de resetear (para marcador visual)
            spike_marker_value = ask_volume_agresion[alias] - bid_volume_agresion[alias]
            # Resetear contadores de agresion
            ask_volume_agresion[alias] = 0
            bid_volume_agresion[alias] = 0

    # Acumular volumen por lado
    if is_bid:
        ask_volume[alias] += size  # Bolas VERDES (acumulado continuo)
        ask_volume_agresion[alias] += size
    else:
        bid_volume[alias] += size  # Bolas ROJAS (acumulado continuo)
        bid_volume_window[alias].append(size)  # Bolas ROJAS (ventana flotante)
        bid_volume_agresion[alias] += size

    # Dibujar indicadores en CADA trade
    # 1. cum_bid_vol - Volumen BID de últimos 20 trades (ROJO)
    if alias in volume_indicators:
        cum_bid_vol = sum(bid_volume_window[alias])
        bm.add_point(addon, alias, volume_indicators[alias], cum_bid_vol)

    # 2. Initiation - Diferencia ASK - BID 
    if alias in initiation_indicators:
        initiation = ask_volume[alias] - bid_volume[alias]  # ASK - BID
        bm.add_point(addon, alias, initiation_indicators[alias], initiation)

    # 3. Imbalance - Como real_delta pero se resetea con spike (VERDE)
    if alias in agresion_indicators:
        if spike_detected:
            # Dibujar pico visual en el momento del spike (2x el valor anterior para destacar)
            bm.add_point(addon, alias, agresion_indicators[alias], spike_marker_value * 2)
        else:
            # Valor normal de imbalance
            agresion = ask_volume_agresion[alias] - bid_volume_agresion[alias]
            bm.add_point(addon, alias, agresion_indicators[alias], agresion)

    # 4. only_ask - Solo compras agresivas (ASK), se resetea con spike (AMARILLO)
    if alias in only_ask_indicators:
        only_ask = ask_volume_agresion[alias]
        bm.add_point(addon, alias, only_ask_indicators[alias], only_ask)


def handle_indicator_response(addon, request_id, indicator_id):
    global volume_indicators, initiation_indicators, agresion_indicators, only_ask_indicators, req_id_to_alias
    alias, indicator_type = req_id_to_alias[request_id]

    if indicator_type == "volume":
        volume_indicators[alias] = indicator_id
    elif indicator_type == "initiation":
        initiation_indicators[alias] = indicator_id
    elif indicator_type == "agresion":
        agresion_indicators[alias] = indicator_id
    elif indicator_type == "only_ask":
        only_ask_indicators[alias] = indicator_id


def handle_subscribe_instrument(addon, alias, full_name, is_crypto, pips, size_multiplier, instrument_multiplier, supported_features):
    global req_id, req_id_to_alias

    # Indicador 1: big_bid - Ventana flotante de últimos 20 trades (ROJO)
    req_id += 1
    req_id_to_alias[req_id] = (alias, "volume")
    bm.register_indicator(addon, alias, req_id, "big_bid", "BOTTOM", color=(255, 0, 0))

    # Indicador 2: real_delta - Diferencia ASK - BID (GRIS OSCURO)
    req_id += 1
    req_id_to_alias[req_id] = (alias, "initiation")
    bm.register_indicator(addon, alias, req_id, "real_delta", "BOTTOM", color=(100, 100, 100))

    # Indicador 3: imbalance - Como real_delta pero se resetea con spike (VERDE)
    req_id += 1
    req_id_to_alias[req_id] = (alias, "agresion")
    bm.register_indicator(addon, alias, req_id, "imbalance", "BOTTOM", color=(0, 255, 0))

    # Indicador 4: only_ask - Solo compras agresivas, se resetea con spike (AMARILLO)
    req_id += 1
    req_id_to_alias[req_id] = (alias, "only_ask")
    bm.register_indicator(addon, alias, req_id, "only_ask", "BOTTOM", color=(255, 255, 0))

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
