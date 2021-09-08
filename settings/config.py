import yaml
file = open(f"settings/sim.yaml", "r")
full_config = yaml.load(file)
numero_sim = full_config["numero_sim"]
config = full_config["sims"][numero_sim]
file.close()

