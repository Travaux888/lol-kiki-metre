import json
import time
import os
import requests
from datetime import datetime

# --- CONFIGURATION (Variables d'environnement) --- #
# Ces valeurs pourront être changées dans Docker sans toucher au code
API_KEY = os.environ.get("RIOT_API_KEY", "YOUR_API_KEY_HERE")
PLAYERS_FILE = os.environ.get("PLAYERS_FILE", "config/players.json")
HISTORY_FILE = os.environ.get("HISTORY_FILE", "data/history.json")
SLEEP_BETWEEN_PLAYERS = int(os.environ.get("SLEEP_BETWEEN_PLAYERS", 2))

# --- FONCTIONS --- #

def check_riot_api(player_name, tag):
    """
    Appel API Riot pour récupérer le rang d'un joueur.
    Note : Samedi nous intégrerons la vraie URL et le traitement du JSON Riot.
    """
    # Simulation de l'URL Riot (EUW)
    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{player_name}-{tag}"
    headers = {"X-Riot-Token": API_KEY}
    
    try:
        # Bloc commenté pour la simulation actuelle
        # response = requests.get(url, headers=headers, timeout=5)
        # response.raise_for_status() 
        # return response.json()
        
        return "Gold IV"  # Simulation pour tester la logique de comparaison
    except Exception as e:
        print(f"❌ Erreur API pour {player_name}#{tag} : {e}")
        return None

def load_json_file(path, default=None):
    """Charge un fichier JSON ou retourne une valeur par défaut s'il n'existe pas."""
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json_file(path, data):
    """Sauvegarde les données dans un fichier JSON (crée le dossier si besoin)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- PROGRAMME PRINCIPAL --- #

def main():
    print(f"--- 🛡️ LoL Rank Guardian : Scan du {datetime.now().strftime('%d/%m/%Y %H:%M')} ---")

    # 1. Charger la liste des joueurs à surveiller
    players_data = load_json_file(PLAYERS_FILE, default={"players":[]})
    players = players_data.get("players", [])
    
    if not players:
        print("❌ Aucun joueur trouvé dans le fichier config/players.json.")
        return
    
    print(f"✅ {len(players)} joueurs chargés.\n")

    # 2. Charger l'historique des rangs (pour comparer)
    history = load_json_file(HISTORY_FILE, default={})

    # 3. Boucle de vérification
    for p in players:
        name = p["name"]
        tag = p["tag"]

        # Récupération du rang actuel
        current_rank = check_riot_api(name, tag)
        if current_rank is None:
            continue

        # Comparaison avec l'ancien rang stocké
        old_rank = history.get(name, {}).get("rank", "Inconnu")

        if old_rank != current_rank:
            print(f"🔔 ALERT : {name}#{tag} a bougé ! [{old_rank}] ➔ [{current_rank}]")
        else:
            print(f"📊 {name}#{tag} : Stable à {current_rank}")

        # Mise à jour de l'historique en mémoire
        history[name] = {
            "rank": current_rank,
            "last_checked": datetime.now().isoformat()
        }

        # --- PROTECTION RATE LIMIT ---
        # On attend pour ne pas se faire bannir l'IP par Riot
        time.sleep(SLEEP_BETWEEN_PLAYERS)

    # 4. Sauvegarde finale de l'historique sur le disque
    save_json_file(HISTORY_FILE, history)
    print(f"\n--- ✅ Scan terminé avec succès ---")

if __name__ == "__main__":
    main()
