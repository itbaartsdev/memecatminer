import requests
import json
import time
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import sys
import os
from colorama import init, Fore, Style
import base64
# Initialize colorama
init()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def key_bot():
    api = base64.b64decode("aHR0cHM6Ly9pdGJhYXJ0cy5jb20vYXBpX3ByZW0uanNvbg==").decode('utf-8')
    try:
        response = requests.get(api)
        response.raise_for_status()
        try:
            data = response.json()
            header = data['header']
            print('\033[96m' + header + '\033[0m')
        except json.JSONDecodeError:
            print('\033[96m' + response.text + '\033[0m')
    except requests.RequestException as e:
        print('\033[96m' + f"Failed to load header: {e}" + '\033[0m')

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def countdown(seconds):
    while seconds > 0:
        sys.stdout.write(f"\r{Fore.YELLOW}[SYSTEM] Next check in: {format_time(seconds)}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    sys.stdout.write('\r' + ' ' * 70 + '\r')  # Clear the line
    sys.stdout.flush()

def restart_program():
    print(f"\n{Fore.YELLOW}[SYSTEM] Restarting program...{Style.RESET_ALL}")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def create_box(text, width=44):
    return (
        f"{Fore.CYAN}╔{'═' * width}╗{Style.RESET_ALL}\n"
        f"{Fore.CYAN}║{text.center(width)}║{Style.RESET_ALL}\n"
        f"{Fore.CYAN}╚{'═' * width}╝{Style.RESET_ALL}"
    )

class RevelationMiner:
    def __init__(self, user_data):
        self.base_url = "https://revelationwithai.com/service1"
        self.token = None
        self.cats = []
        self.current_cats = {}
        self.user_data = user_data
        
    def login(self):
        try:
            login_payload = {
                "user_name": self.user_data['first_name'] + (self.user_data.get('last_name', '') or ''),
                "telegram_id": str(self.user_data['id'])
            }
            
            headers = {
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
            }
            
            response = requests.post(
                f"{self.base_url}/player/login",
                json=login_payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'token' in result['result']:
                    self.token = result['result']['token']
                    return True
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Login error: {str(e)}{Style.RESET_ALL}")
            
        return False

    def get_headers(self):
        return {
            "authorization": self.token,
            "content-type": "application/json"
        }

    def get_remaining_time(self, mining_start_time, mining_duration=10800):
        start_time = datetime.fromisoformat(mining_start_time.replace('Z', ''))
        current_time = datetime.utcnow()
        elapsed = (current_time - start_time).total_seconds()
        return max(0, mining_duration - elapsed)

    def get_current_mining(self):
        """Get current mining information"""
        response = requests.get(
            f"{self.base_url}/mine/current",
            headers=self.get_headers()
        )
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'mining_cats' in result['result']:
                # Create dictionary with cat_id as key for easy lookup
                self.current_cats = {
                    cat['cat_id']: cat for cat in result['result']['mining_cats']
                }
                return True
        return False

    def get_info(self):
        if not self.get_current_mining():
            return False

        response = requests.get(
            f"{self.base_url}/player/info",
            headers=self.get_headers()
        )
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'cats' in result['result']:
                self.cats = result['result']['cats']
                active_cats = [cat for cat in self.cats if cat['in_field']]
                
                if active_cats:
                    print(f"{Fore.CYAN}╔{'═' * 44}╗{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}║{'Active Mining Cats':^44}║{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}╠{'═' * 18}╦{'═' * 12}╦{'═' * 12}╣{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}║{'Name':^18}║{'Breed ID':^12}║{'Rate':^12}║{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}╠{'═' * 18}╬{'═' * 12}╬{'═' * 12}╣{Style.RESET_ALL}")
                    
                    for cat in active_cats:
                        current_info = self.current_cats.get(cat['cat_id'], {})
                        name = current_info.get('name', 'Unknown')[:16]  # Batasi panjang nama
                        breed = str(cat['breed_id']).zfill(5)
                        mine_rate = f"{current_info.get('mine_rate', 0)}/h"
                        print(f"{Fore.CYAN}║{name:^18}║{breed:^12}║{mine_rate:^12}║{Style.RESET_ALL}")
                    
                    total_rate = sum(self.current_cats[cat['cat_id']].get('mine_rate', 0) for cat in active_cats)
                    print(f"{Fore.CYAN}╠{'═' * 18}╩{'═' * 12}╩{'═' * 12}╣{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}║{'Total Mining Rate:':^30} {f'{total_rate}/h':^13}║{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}╚{'═' * 44}╝{Style.RESET_ALL}")
                return True
        return False

    def collect_and_restart_mine(self, cat_id, mining_start_time, mining_duration=10800):
        # Gunakan waktu mining spesifik dari kucing
        cat_info = self.current_cats.get(cat_id, {})
        cat_mining_duration = cat_info.get('time', mining_duration)  # Gunakan time dari data kucing
        
        remaining = self.get_remaining_time(mining_start_time, cat_mining_duration)  # Gunakan durasi spesifik
        cat_name = cat_info.get('name', 'Unknown')
        
        if remaining > 0:
            return remaining
        
        try:
            # Collect mining
            collect_response = requests.post(
                f"{self.base_url}/mine/collect",
                params={"cat_id": cat_id},
                headers=self.get_headers()
            )
            
            if collect_response.status_code == 200:
                result = collect_response.json()
                if 'result' in result and 'earnings' in result['result']:
                    earnings = result['result']['earnings']
                    print(f"{Fore.GREEN}[SUCCESS] {cat_name:^20} │ Collected: {earnings} USDT{Style.RESET_ALL}")
                    
                    time.sleep(2)
                    
                    # Restart mining
                    start_response = requests.post(
                        f"{self.base_url}/mine/start",
                        params={"cat_id": cat_id},
                        headers=self.get_headers()
                    )
                    
                    if start_response.status_code == 200:
                        print(f"{Fore.GREEN}[SUCCESS] {cat_name:^20} │ Mining restarted{Style.RESET_ALL}")
                        
                        time.sleep(2)
                        
                        # Auto click cat
                        click_response = requests.get(
                            f"{self.base_url}/mine/clickCat",
                            params={"cat_id": cat_id, "click_times": 10},
                            headers=self.get_headers()
                        )
                        
                        if click_response.status_code == 200:
                            click_result = click_response.json()
                            if 'result' in click_result and 'coins' in click_result['result']:
                                coins = click_result['result']['coins']
                                print(f"{Fore.GREEN}[SUCCESS] {cat_name:^20} │ Auto-click: +{coins} coins{Style.RESET_ALL}")
                                return self.current_cats[cat_id]['time']  # Use cat's specific mining time
                            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Mining process error: {str(e)}{Style.RESET_ALL}")
            
        return mining_duration

    def check_and_mine(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("\n" + create_box(f"Mining Check: {current_time}"))
        
        # Mendapatkan info player
        response = requests.get(
            f"{self.base_url}/player/info",
            headers=self.get_headers()
        )
        if response.status_code == 200:
            player_info = response.json()['result']
            # Potong nama menjadi maksimal 10 karakter
            shortened_name = player_info['name'][:10]
            print(f"{Fore.CYAN}╔{'═' * 44}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{'Player Information':^44}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠{'═' * 44}╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║ Name    : {shortened_name:<33}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║ Level   : {player_info['level']} ({player_info['level_info']['rank']}){' ' * (33-len(str(player_info['level']))-len(player_info['level_info']['rank'])-3)}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║ Exp     : {player_info['exp']:<33}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║ Coins   : {player_info['coins']}{' ' * (33-len(str(player_info['coins'])))}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═' * 44}╝{Style.RESET_ALL}")
        
        if not self.get_info():
            if not self.login():
                print(f"{Fore.RED}[ERROR] Re-login failed!{Style.RESET_ALL}")
                return None
        
        next_check = float('inf')
        for cat in self.cats:
            if cat['in_field']:
                remaining = self.collect_and_restart_mine(
                    cat['cat_id'], 
                    cat['mining_start_time'], 
                    10800
                )
                if remaining:
                    next_check = min(next_check, remaining)
        
        return next_check if next_check != float('inf') else None

def main():
    clear_screen()
    key_bot()
    
    # Tampilkan MEME CAT MINER ASSISTANT sekali saja di awal
    print(create_box("MEME CAT MINER ASSISTANT"))

    # Baca dan parse semua query dari file
    queries = []
    try:
        with open('query.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parsed = parse_qs(urlparse('?' + line).query)
                    if 'user' in parsed:
                        user_data = json.loads(parsed['user'][0])
                        queries.append(user_data)
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Failed to read queries: {str(e)}{Style.RESET_ALL}")
        return

    if not queries:
        print(f"{Fore.RED}[ERROR] No valid queries found in query.txt{Style.RESET_ALL}")
        return

    miners = []
    # Inisialisasi miner untuk setiap akun
    for user_data in queries:
        miner = RevelationMiner(user_data)
        if miner.login():
            miners.append(miner)
        else:
            print(f"{Fore.RED}[ERROR] Login failed for {user_data['first_name']}{Style.RESET_ALL}")

    if not miners:
        print(f"{Fore.RED}[ERROR] No accounts successfully logged in{Style.RESET_ALL}")
        return

    while True:
        try:
            next_check_global = float('inf')
            
            # Check mining untuk setiap akun
            for miner in miners:
                print(f"\n{Fore.CYAN}{'═' * 17} {miner.user_data['first_name'].center(10)} {'═' * 17}{Style.RESET_ALL}")
                next_check = miner.check_and_mine()
                
                if next_check is not None:
                    next_check_global = min(next_check_global, next_check)
                else:
                    print(f"{Fore.YELLOW}[WARNING] Skipping account {miner.user_data['first_name']}{Style.RESET_ALL}")

            if next_check_global == float('inf'):
                print(f"{Fore.RED}[ERROR] No valid next check time for any account{Style.RESET_ALL}")
                time.sleep(60)  # Wait before retry
                continue

            next_check_secs = max(60, int(next_check_global))
            countdown(next_check_secs)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[SYSTEM] Program stopped by user{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Unexpected error: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[SYSTEM] Restarting in 5 seconds...{Style.RESET_ALL}")
            time.sleep(5)
            restart_program()

if __name__ == "__main__":
    main()
