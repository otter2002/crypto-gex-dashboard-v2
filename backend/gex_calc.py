from collections import defaultdict

def compute_gex(options):
    gex_by_strike = defaultdict(lambda: {"call": 0.0, "put": 0.0})
    for opt in options:
        strike = opt["strike"]
        gamma = opt["gamma"]
        oi = opt["open_interest"]
        gex = gamma * oi * 100
        if opt["option_type"] == "call":
            gex_by_strike[strike]["call"] += gex
        elif opt["option_type"] == "put":
            gex_by_strike[strike]["put"] += gex

    result = []
    zero_gamma_strike = None
    min_diff = float("inf")
    call_wall = (0, 0)
    put_wall = (0, 0)

    for strike, gex_values in sorted(gex_by_strike.items()):
        net_gex = gex_values["call"] + gex_values["put"]
        result.append({
            "strike": strike,
            "call_gex": gex_values["call"],
            "put_gex": gex_values["put"],
            "net_gex": net_gex
        })
        if abs(net_gex) < min_diff:
            zero_gamma_strike = strike
            min_diff = abs(net_gex)
        if gex_values["call"] > call_wall[1]:
            call_wall = (strike, gex_values["call"])
        if gex_values["put"] < put_wall[1]:
            put_wall = (strike, gex_values["put"])

    return {
        "data": result,
        "zero_gamma": zero_gamma_strike,
        "call_wall": call_wall[0],
        "put_wall": put_wall[0]
    }
