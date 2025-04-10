import multiprocessing as mp
from multiprocessing import shared_memory
import numpy as np
import json
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from utils import generate_random_date, generate_random_value, save_to_file, DateTimeEncoder
from values import PUB_VALUES, SUB_VALUES, GENERAL_CONFIG


class DataGenerator:
    def __init__(self):
        self.pub_config = PUB_VALUES
        self.sub_config = SUB_VALUES
        self.general_config = GENERAL_CONFIG
        self.start_date = self.pub_config["fields"]["date"]["start_date"]
        self.end_date = self.pub_config["fields"]["date"]["end_date"]
        
    def generate_publication(self) -> Dict[str, Any]:
        pub = {}
        for field, config in self.pub_config["fields"].items():
            if field == "date":
                pub[field] = generate_random_date(self.start_date, self.end_date)
            else:
                pub[field] = generate_random_value(config)
        return pub

    def select_fields_for_subscription(self) -> List[str]:
        fields = list(self.sub_config["field_weights"].keys())
        weights = list(self.sub_config["field_weights"].values())


        selected_fields = []
        for field, weight in zip(fields, weights):
            if np.random.random() < weight:
                selected_fields.append(field)
        
        if not selected_fields:
            selected_fields.append(np.random.choice(fields))
        
        return selected_fields

    def get_available_operators(self, field_type: str, field: str) -> List[str]:
        operators = self.sub_config["operators"][field_type]
            
               
        return operators

    def generate_subscription(self) -> Dict[str, List[Any]]:
        sub = {}
        fields = self.select_fields_for_subscription()
        
        for field in fields:
            field_type = self.pub_config["fields"][field]["type"]
            operators = self.get_available_operators(field_type, field)
            
                
            if field in self.sub_config["equality_weights"]:
         
                if np.random.random() < self.sub_config["equality_weights"][field]:
                    operator = "="
                else:
                    
                    other_operators = [op for op in operators if op != "="]
                    if not other_operators:  
                        continue
                    operator = np.random.choice(other_operators)
            else:
                operator = np.random.choice(operators)
            
            if field == "date":
                value = generate_random_date(self.start_date, self.end_date)
            else:
                value = generate_random_value(self.pub_config["fields"][field])
            
            sub[field] = [operator, value]
            
        return sub

    def generate_publications_worker(self, start_idx: int, end_idx: int, shm_name: str, shape: tuple, dtype: str) -> None:
      
        shm = shared_memory.SharedMemory(name=shm_name)
        arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
        
       
        for i in range(start_idx, end_idx):
            pub = self.generate_publication()

            arr[i] = json.dumps(pub, cls=DateTimeEncoder)
        
        shm.close()

    def generate_subscriptions_worker(self, start_idx: int, end_idx: int, shm_name: str, shape: tuple, dtype: str) -> None:
     
        shm = shared_memory.SharedMemory(name=shm_name)
        arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
        
        for i in range(start_idx, end_idx):
            sub = self.generate_subscription()
            arr[i] = json.dumps(sub, cls=DateTimeEncoder)
        
        shm.close()

    def generate_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        num_pubs = self.general_config["num_publications"]
        num_subs = self.general_config["num_subscriptions"]
        num_processes = self.general_config["parallelization"]["num_processes"]
        
        pub_chunk_size = num_pubs // num_processes
        sub_chunk_size = num_subs // num_processes
        
        pub_shm = shared_memory.SharedMemory(create=True, size=num_pubs * 1000)   
        pub_arr = np.ndarray((num_pubs,), dtype='S1000', buffer=pub_shm.buf)
        
        sub_shm = shared_memory.SharedMemory(create=True, size=num_subs * 1000)  
        sub_arr = np.ndarray((num_subs,), dtype='S1000', buffer=sub_shm.buf)
        
        processes = []
        
        for i in range(num_processes):
            start_idx = i * pub_chunk_size
            end_idx = start_idx + pub_chunk_size if i < num_processes - 1 else num_pubs
            p = mp.Process(
                target=self.generate_publications_worker,
                args=(start_idx, end_idx, pub_shm.name, pub_arr.shape, pub_arr.dtype)
            )
            processes.append(p)
            p.start()
        
        for p in processes:
            p.join()
        
        processes.clear()
        
        for i in range(num_processes):
            start_idx = i * sub_chunk_size
            end_idx = start_idx + sub_chunk_size if i < num_processes - 1 else num_subs
            p = mp.Process(
                target=self.generate_subscriptions_worker,
                args=(start_idx, end_idx, sub_shm.name, sub_arr.shape, sub_arr.dtype)
            )
            processes.append(p)
            p.start()
        
        for p in processes:
            p.join()
        
        publications = [json.loads(pub.decode('utf-8')) for pub in pub_arr]
        subscriptions = [json.loads(sub.decode('utf-8')) for sub in sub_arr]
        
        pub_shm.close()
        pub_shm.unlink()
        sub_shm.close()
        sub_shm.unlink()
        
        return publications, subscriptions

    def save_data(self, publications: List[Dict[str, Any]], subscriptions: List[Dict[str, Any]]) -> None:
        save_to_file(publications, "publications.json")
        save_to_file(subscriptions, "subscriptions.json") 