import os
from pathlib import Path
from subprocess import Popen
import shlex
from parser_data import display_stats

BASE_DIR = Path(__file__).resolve().parent.parent


SERVER = BASE_DIR / "client-server-model" / "server" / "main_server.py"
CLIENT = BASE_DIR / "client-server-model" / "client" / "AR_client.py"
DATA_GENERATOR = BASE_DIR / "client-server-model" / "server" / "gen_test_data.py"
STATS = (
    BASE_DIR
    / "client-server-model"
    / "server"
    / "experimental_data"
    / "access_req_stats.txt"
)
ALL_EXPERIMENTS_HISTORY_DIR = BASE_DIR / "client-server-model" / "experiments"
ALL_EXPERIMENTS_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
EXPERIMENTS_PER_CONFIG = 1

"""Server

    argparser = ArgumentParser()
    argparser.add_argument('-a', '--al_update_rate', type=int, help='Auxiliary list update rate')
    argparser.add_argument('-mal', '--max_aux_list_len', type=int, default=100, help='Maximum length of the auxiliary list per vacation')
    argparser.add_argument('-mar', '--max_access_requests', type=int, default=500, help='Maximum number of access requests per vacation')
    argparser.add_argument('-mv', '--max_no_of_vacations', type=int, default=5, help='Maximum number of vacations')
    argparser.add_argument('-pr', '--policy_resolution', type=int, default=2, help Policy resolution mode:
    1: Linear Search
    2: Policy Tree Based
    )
    argparser.add_argument('-v', '--vacation_model', type=int, default=3, help Vacation model:
    1: Access Queue Empty
    2: Fixed Number of Access Requests Served
    3: Aux List Full
)
"""


"""Client

    arg_parser = ArgumentParser()
    arg_parser.add_argument('-a', '--arrival_rate', type=int, help='Mean arrival rate of access requests')
    
    arg_parser.set_defaults(arrival_rate=10)

"""

"""
SYSTEM_CONFIGS = {
    'c1': {
        'al_update_rate': 20,
        'arrival_rate': 150,
        'attributes': 4,
        'subjects': 35,
        'objects': 35
    },
    'c2': {
        'al_update_rate': 15,
        'arrival_rate': 80,
        'attributes': 6,
        'subjects': 45,
        'objects': 45
    },
    'c3': {
        'al_update_rate': 7,
        'arrival_rate': 20,
        'attributes': 8,
        'subjects': 100,
        'objects': 100
    },
    'c4': {
        'al_update_rate': 2,
        'arrival_rate': 5,
        'attributes': 10,
        'subjects': 125,
        'objects': 125
    }
}
"""

SYSTEM_CONFIGS = {
    "c1": { # Linear Search with Access Queue Empty
        "vacation_model": 1,
        "policy_resolution": 1,
    },
    "c2": { # Policy Tree Based with Access Queue Empty
        "vacation_model": 1,
        "policy_resolution": 2,
    },
    "c3": { # Linear Search with Fixed Number of Access Requests Served
        "vacation_model": 2,
        "policy_resolution": 1,
    },
    "c4": { # Policy Tree Based with Fixed Number of Access Requests Served
        "vacation_model": 2,
        "policy_resolution": 2,
    },
}


REST_CONFIGS = {"al_update_rate": [20, 15, 7, 2], "arrival_rate": [150, 80, 20, 5]}

DATA_CONFIGS = {
    "attributes": [4, 6, 8, 10],
    "subjects": [35, 45, 100, 125],
    "objects": [35, 45, 100, 125],
}

VARIANT_CONFIGS = {
    "al_update_rate": [20, 15, 7, 2],
    "arrival_rate": [150, 80, 20, 5],
    "attributes": [4, 6, 8, 10],
    "policy_size": [15, 25, 35, 45],
}

# run gen_test_data.py -a 6 -s 15 -o 15 -> 100
# run gen_test_data.py -a 6 -s 25 -o 25 -> 300
# run gen_test_data.py -a 6 -s 35 -o 35 -> 600
# run gen_test_data.py -a 6 -s 45 -o 45 -> 1000
# Policy variation: [100, 300, 600, 1000]


MAX_NUMBER_OF_VACATIONS = 1 + 5


def get_new_datagen():
    # for a, s, o in zip(DATA_CONFIGS['attributes'], DATA_CONFIGS['subjects'], DATA_CONFIGS['objects']):
    #     yield {
    #         'attributes': a,
    #         'subjects': s,
    #         'objects': o
    #     }
    yield {"attributes": 6, "subjects": 45, "objects": 45}


def get_new_experiment(variant: str, experiment_no: int = 1):
    for data_config in get_new_datagen():
        for c, config in SYSTEM_CONFIGS.items():
            current_config = data_config.copy()
            for k, v in config.items():
                current_config[k] = v
            vary = VARIANT_CONFIGS[variant]
            if variant == "policy_size":
                for k, v in REST_CONFIGS.items():
                    if k in ["subjects", "objects"]:
                        continue
                    current_config[k] = v[1] # Default value
                    
                for vidx, var in enumerate(vary):
                    current_config["subjects"] = var
                    current_config["objects"] = var
                    yield f"{c}_{variant}_v{vidx+1}_{experiment_no}.txt", current_config
            else:
                for k, v in REST_CONFIGS.items():
                    if k == variant:
                        continue
                    current_config[k] = v[1] # Default value
                    
                for vidx, var in enumerate(vary):
                    current_config[variant] = var
                    yield f"{c}_{variant}_v{vidx+1}_{experiment_no}.txt", current_config
    


def experiment(server_config: dict, client_config: dict):
    server_process = None
    client_process = None
    try:
        server_process = Popen(
            shlex.split(
                f"run {SERVER} "
                + " ".join([f"--{k} {v}" for k, v in server_config.items()])
            )
        )
        client_process = Popen(
            shlex.split(
                f"run {CLIENT} "
                + " ".join([f"--{k} {v}" for k, v in client_config.items()])
            )
        )
        server_process.wait()
        client_process.wait()
    except Exception as e:
        print(f"[Runner] Error: {e}")
        if server_process:
            server_process.kill()
        if client_process:
            client_process.kill()
        raise e
    finally:
        if server_process:
            server_process.kill()
        if client_process:
            client_process.kill()


def datagen(config: dict):
    gen_data_process = None
    try:
        if (
            not config.get("attributes")
            or not config.get("subjects")
            or not config.get("objects")
        ):
            raise Exception("Invalid configuration")
        command = f"run {DATA_GENERATOR} " + " ".join(
            [f"--{k} {v}" for k, v in config.items()]
        )
        gen_data_process = Popen(shlex.split(command))
        gen_data_process.wait()
    except Exception as e:
        print(f"[Runner] Error: {e}")
        if gen_data_process:
            gen_data_process.kill()
        raise e
    finally:
        if gen_data_process:
            gen_data_process.kill()

def hash_config(config: dict):
    return hash(frozenset(config.items()))

def efficient_experiment_gen(experiment_no: int = 1):
    actual_order = []
    for variant in VARIANT_CONFIGS.keys():
        actual_order += [
            {
                'experiment_file': experiment_file,
                'config': config,
                'datagen_config': {
                    'attributes': config.get('attributes'),
                    'subjects': config.get('subjects'),
                    'objects': config.get('objects'),
                }
            } for experiment_file, config in get_new_experiment(variant, experiment_no)
        ]
    
    mapping = {}
    for expcfg in actual_order:
        if hash_config(expcfg['datagen_config']) not in mapping:
            mapping[hash_config(expcfg['datagen_config'])] = []
        mapping[hash_config(expcfg['datagen_config'])].append(expcfg)
    effcient_order = []
    for _, expcfgs in mapping.items():
        effcient_order += expcfgs
    effcient_order = [(expcfg['experiment_file'], expcfg['config']) for expcfg in effcient_order]
    return effcient_order

CACHE = {}

def cache_experiments():
    for file in ALL_EXPERIMENTS_HISTORY_DIR.glob('*.txt'):
        CACHE[file.stem] = True

def main():
    for exp in range(1, EXPERIMENTS_PER_CONFIG + 1):
        prev_datagen_config = {}
        for experiment_file, config in efficient_experiment_gen(exp):
            if CACHE[experiment_file.split('.')[0]]:
                print(f'[Runner] Skipping experiment: {experiment_file.split(".")[0]}')
                continue
            print(f'[Runner] Running experiment: {experiment_file.split(".")[0]}')
            datagen_config = {
                "attributes": config.get("attributes"),
                "subjects": config.get("subjects"),
                "objects": config.get("objects"),
            }
            if prev_datagen_config != datagen_config:
                prev_datagen_config = datagen_config
                print(f'[Runner] Generating data for: {experiment_file.split(".")[0]}')
                datagen(datagen_config)
            experiment(
                server_config={
                    "al_update_rate": config.get("al_update_rate"),
                    "policy_resolution": config.get("policy_resolution"),
                    "vacation_model": config.get("vacation_model"),
                    "max_no_of_vacations": MAX_NUMBER_OF_VACATIONS,
                },
                client_config={
                    "arrival_rate": config.get("arrival_rate"),
                },
            )
            os.rename(STATS, ALL_EXPERIMENTS_HISTORY_DIR / experiment_file)
            display_stats(ALL_EXPERIMENTS_HISTORY_DIR / experiment_file)
            print(f'[Runner] Done running experiment: {experiment_file.split(".")[0]}')
    print("[Runner] Done running all experiments")


if __name__ == "__main__":
    cache_experiments()
    main()
