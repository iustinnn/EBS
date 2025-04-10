import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
import json


def generate_random_date(start_date: datetime, end_date: datetime) -> datetime:
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = np.random.randint(0, days_between_dates)
    return start_date + timedelta(days=random_number_of_days)


def generate_random_value(field_config: Dict[str, Any]) -> Any:
    field_type = field_config["type"]
    
    if field_type == "integer":
        if "values" in field_config:
            return np.random.choice(field_config["values"])
        else:
            return np.random.randint(field_config["min"], field_config["max"] + 1)
    elif field_type == "double":
        if "values" in field_config:
            return np.random.choice(field_config["values"])
        else:
            return np.round(np.random.uniform(field_config["min"], field_config["max"]), 2)
    elif field_type == "string":
        return np.random.choice(field_config["values"])
    elif field_type == "date":
        return generate_random_date(field_config["start_date"], field_config["end_date"])
    else:
        raise ValueError(f"Unknown field type: {field_type}")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        return super().default(obj)


def datetime_decoder(dct):
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                dct[key] = datetime.strptime(value, "%Y-%m-%d")
            except (ValueError, TypeError):
                pass
    return dct


def save_to_file(data: List[Dict], filename: str) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f, cls=DateTimeEncoder, indent=2)


def load_from_file(filename: str) -> List[Dict]:
    with open(filename, 'r') as f:
        return json.load(f, object_hook=datetime_decoder)


def format_publication(publication: Dict) -> str:
    return json.dumps(publication, cls=DateTimeEncoder, indent=2)


def format_subscription(subscription: Dict) -> str:
    return json.dumps(subscription, cls=DateTimeEncoder, indent=2)