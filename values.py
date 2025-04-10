from datetime import datetime

PUB_VALUES = {
    "fields": {
        "stationid": {
            "type": "integer",
            "values": list(range(1, 101))  # 100 possible stations
        },
        "city": {
            "type": "string",
            "values": ["Bucharest", "Cluj-Napoca", "Timisoara", "Iasi", "Constanta"]
        },
        "temp": {
            "type": "integer",
            "min": -20,
            "max": 40
        },
        "rain": {
            "type": "double",
            "min": 0.0,
            "max": 100.0
        },
        "wind": {
            "type": "integer",
            "min": 0,
            "max": 100
        },
        "direction": {
            "type": "string",
            "values": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        },
        "date": {
            "type": "date",
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 12, 31)
        }
    }
}


SUB_VALUES = {
    "field_weights": {
        "stationid": 0.1,  # 10%
        "city": 0.9,      # 20%
        "temp": 0.2,      # 20%
        "rain": 0.1,      # 10%
        "wind": 0.1,      # 10%
        "direction": 0.1, # 10%
        "date": 0.2       # 20%
    },
    "equality_weights": {
        "temp": 0.9  # 60% of subscriptions with direction use operator =
    },
    "operators": {
        "integer": ["=", "<", "<=", ">", ">="],
        "double": ["=", "<", "<=", ">", ">="],
        "string": ["="],
        "date": ["=", "<", "<=", ">", ">="]
    }
}


GENERAL_CONFIG = {
    "num_publications": 100000,
    "num_subscriptions": 100000,
    "parallelization": {
        "enabled": True, 
        "num_processes": 8
    }
} 