import discord
import os
import logging
import threading
import requests
import random
import config
import time
import string
import asyncio

from pystyle import Colorate, Colors
from colorama import Fore

logging.disable(logging.CRITICAL)

os.system("cls")

gore_gifs = ["https://imgur.com/LHhTOlW",
             "https://imgur.com/JqIuvdz",
             "https://imgur.com/RCUGpNF",
             "https://imgur.com/LfHZPzd"]
emojies = ["🔥", "💀", "😭", "🤑", "🖕", "🥶", "🥵", "😍", "👾", "😈", "😤", "😱", "😑", "🙀", "🤕"]

logo = """
╦  ┬┌─┐┬ ┬┌┬┐┌─┐
║  ││ ┬├─┤ │ └─┐
╩═╝┴└─┘┴ ┴ ┴ └─┘
╦═╗┌─┐┬┌┬┐┌─┐┬─┐
╠╦╝├─┤│ ││├┤ ├┬┘
╩╚═┴ ┴┴─┴┘└─┘┴└─
"""

features = """

[1] - Start Raider
[2] - Token Reset (EMAIL:PASS TO TOKEN)
[0] - Exit
"""

def print_srv_raider(text: str, error: bool) -> str:
    print(f'~Server Raider~ {Fore.RED + f"[-] - {text}" if error else Fore.GREEN + f"[+] - {Fore.CYAN + text + Fore.RESET}"}')
def print_email_to_token(text: str, error: bool) -> str:
    print(f'~Email to Token~ {Fore.RED + f"[-] - {text}" if error else Fore.GREEN + f"[+] - {Fore.CYAN + text + Fore.RESET}"}')

async def send_message(client, guild_id, channel_id, message, how_many, random_mention, random_mention_amount, token):
    await client.wait_until_ready()
    try:
        server = client.get_guild(guild_id)
        if server is None:
            print_srv_raider(f"Couldn't find the server for token: {token} | Please verify the GuildID or if the token is in the server.", error=True)
            return

        channels = server.text_channels if config.message_all_channels else [server.get_channel(channel_id)]
        members = server.members

        for _ in range(how_many):
            emoji_str = " ".join(random.choices(emojies, k=random.randint(5, 9)))
            random_str = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 11)))
            msg = message
            users_to_mention = random.sample(members, k=min(random_mention_amount, len(members))) if random_mention else []

            if users_to_mention:
                mentions = " ".join(f"<@{user.id}>" for user in users_to_mention)
                msg += " | " + mentions

            msg = msg.replace("%random_user%", str(random.choice(users_to_mention)) if users_to_mention else "N/A")
            rdm_gif = random.choice(gore_gifs)
            msg = msg.replace("%random_gore%", str(rdm_gif))

            for channel in channels:
                if channel.id not in config.blacklisted_channel_ids:
                    try:
                        await channel.send(f"{msg} | {emoji_str} | {random_str}")
                        splitted_token = token.split('.')
                        print_srv_raider(f"Sent message to {channel.name}: {splitted_token[0][:6]}.******.{splitted_token[2]}", error=False)
                    except discord.Forbidden:
                        pass
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = e.retry_after if e.retry_after else 3
                            print_srv_raider(f"Rate limited. Retrying after {retry_after} seconds.", error=True)
                            await asyncio.sleep(retry_after)
                        else:
                            print_srv_raider(f"HTTP Exception occurred: {e}", error=True)
                    except Exception as e:
                        print_srv_raider(f"Unhandled exception: {e}", error=True)

            if config.delay != 0:
                await asyncio.sleep(config.delay)

    except Exception as e:
        print_srv_raider(f"Error while sending message: {e}", error=True)
    finally:
        await client.close()

def login_and_execute(token, channel_id, message, guild_id, how_many, random_mention, random_mention_amount, friend_id, action):
    client = discord.Client()
    
    @client.event
    async def on_ready():
        splitted_token = token.split('.')
        print(f"{Fore.GREEN}[+] - {Fore.CYAN}Logged in '{client.user.name} ({client.user.id})' on token: {splitted_token[0][:6]}.******.{splitted_token[2]}... {Fore.RESET}")
        await asyncio.sleep(3)
        
        if action == "raid":
            await send_message(client, guild_id, channel_id, message, how_many, random_mention, random_mention_amount, token)
    client.run(token)

def start_raider():
    action = input("Choose action \n[1] Send Messages\n[2] Send User Message Spammer (NOT WORKING): ").strip()

    load_from_config = input("Do you want to load the config (y/n) >> ").lower()
    
    if load_from_config == "y":
        guild_id = config.guild_id if action == "1" else None
        channel_id = config.channel_id if action == "1" else None
        friend_id = config.friend_id
        how_many = config.msg_to_send
        message = config.msg if action == "1" else None
        random_mention = config.ping_rdm_user if action == "1" else False
        random_mention_amount = config.ping_count if random_mention else 0
    else:
        if action == "1":
            guild_id = int(input("Enter the guild ID: "))
            channel_id = int(input("Enter the channel ID: "))
            how_many = int(input("How many messages do you want to send: "))
            message = input("Enter the message to send: ")
            random_mention = input("Do you want to ping a random user (y/n): ").lower() == "y"
            random_mention_amount = int(input("How many mentions: ")) if random_mention else 0

    tokens = []
    try:
        with open("tokens.txt", "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Error: tokens.txt file not found.")
        return

    if not tokens:
        print("No tokens found in tokens.txt.")
        return

    threads = []
    for token in tokens:
        thread = threading.Thread(
            target=login_and_execute,
            args=(token, channel_id, message, guild_id, how_many, random_mention, random_mention_amount, friend_id, "raid" if action == "1" else "friend_requests")
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("All threads have completed. Returning to the main menu...")
    input("Press enter to continue...")

def email_to_token():
    load_file = input("Load from file (./accounts.txt) (y/n) >> ").lower()
    format = input("What format:\n1. EMAIL:PASS:TOKEN\n2. EMAIL:TOKEN:PASS\n3. TOKEN:EMAIL:PASS\nPlease enter your choice >> ")

    if load_file != "y":
        email = input("Please enter the account email address >> ")
        password = input("Please enter the password >> ")

        while True:
            payload = {"login": email, "password": password, "undelete": False}
            resp = requests.post("https://discord.com/api/v9/auth/login", json=payload)

            if resp.status_code == 200:
                print(f"{Fore.GREEN}New Token: {resp.json()['token']}{Fore.RESET}")
                break
            elif resp.status_code == 429:
                print_email_to_token("Rate limit. Sleeping 3 seconds and retrying...", error=True)
                print(resp.text)
                time.sleep(3)
                continue
            else:
                print(f"Error: {resp.text}")
                break

        if resp.status_code == 200:
            if format == "1":
                to_write = f"{email}:{password}:{resp.json()['token']}"
            elif format == "2":
                to_write = f"{email}:{resp.json()['token']}:{password}"
            elif format == "3":
                to_write = f"{resp.json()['token']}:{email}:{password}"
            else:
                to_write = f"{email}:{password}:{resp.json()['token']}"
            with open("./made_tokens.txt", "a") as f:
                f.write(to_write + "\n")
    else:
        with open("./accounts.txt", "r") as f:
            accounts = f.read().splitlines()

        for account in accounts:
            combo = account.split(":")
            email = combo[0]
            password = combo[1]

            while True:
                payload = {"login": email, "password": password, "undelete": False}
                resp = requests.post("https://discord.com/api/v9/auth/login", json=payload)

                if resp.status_code == 200:
                    print(f"{Fore.GREEN}New Token: {resp.json()['token']}{Fore.RESET}")
                    break
                elif resp.status_code == 429:
                    print_email_to_token("Rate limit. Sleeping 3 seconds and retrying...", error=True)
                    time.sleep(3)
                    continue
                else:
                    print(f"Error: {resp.text}")
                    break

            if resp.status_code == 200:
                if format == "1":
                    to_write = f"{email}:{password}:{resp.json()['token']}"
                elif format == "2":
                    to_write = f"{email}:{resp.json()['token']}:{password}"
                elif format == "3":
                    to_write = f"{resp.json()['token']}:{email}:{password}"
                else:
                    to_write = f"{email}:{password}:{resp.json()['token']}"
                with open("./made_tokens.txt", "a") as f:
                    f.write(to_write + "\n")

    input("Press enter to continue...")

def menu():
    while True:
        os.system("cls")
        print(Colorate.Diagonal(Colors.blue_to_green, logo, 1))
        print(Colorate.Diagonal(Colors.blue_to_green, features, 1))
        choice = input("Choose an option >> ")

        if choice == "1":
            start_raider()
        elif choice == "2":
            email_to_token()
        elif choice == "0":
            print("Exiting...")
            exit()
        else:
            print("Invalid option. Please try again.")
            input("Press enter to continue...")

if __name__ == "__main__":
    menu()