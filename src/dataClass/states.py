from dataclasses import dataclass

@dataclass
class States:
    random_connect:str = 'RANDOM_CONNECT'
    main:str = 'MAIN'
    connected:str = 'CONNECTED'
