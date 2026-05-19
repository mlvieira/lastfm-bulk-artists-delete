#!/usr/bin/env python3
import pylast
import time
import urllib.parse
import json
import os
from playwright.sync_api import sync_playwright

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
API_KEY = config["api_key"]
API_SECRET = config["api_secret"]
USERNAME = config["username"]
CACHE_FILE = config["cache_file"]
THRESHOLD = config["threshold"]
LIMIT_FETCH = config["limit_fetch"]

def get_targets():
    if os.path.exists(CACHE_FILE):
        print(f"Loading cached list from {CACHE_FILE}...")
        with open(CACHE_FILE, "r") as f:
            return json.load(f)

    print("Fetching from API (this may take a moment)...")
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
    user = network.get_user(USERNAME)
    library_artists = user.get_library().get_artists(limit=LIMIT_FETCH)
    
    targets = [a.item.name for a in library_artists if int(a.playcount) < THRESHOLD]
    
    with open(CACHE_FILE, "w") as f:
        json.dump(targets, f)
    print(f"Found and saved {len(targets)} artists.")
    return targets

def delete_artist(page, artist):
    encoded_artist = urllib.parse.quote(artist)
    url = f"https://www.last.fm/user/{USERNAME}/library/music/{encoded_artist}"
    page.goto(url)
    
    delete_btn = page.locator(".delete-icon").first
    if not delete_btn.is_visible(): # do we need this? 
        return True

    delete_btn.click()
    
    form = page.locator(".delete-catalogue-item-form")
    success = False
    for attempt in range(3):
        if form.is_visible():
            success = True
            break
        time.sleep(2)

    if not success:
        print(f"Modal failed to load for {artist}, refreshing page...")
        page.reload()
        return False

    form.locator("#id_confirm").check()
    form.locator("button.btn-primary").click()
    print(f"Deletion submitted for {artist}. Waiting for redirect...")
    page.wait_for_url("**/library/artists", timeout=20000)
    time.sleep(2.0)
    return True

def run():
    targets = get_targets()
    if not targets:
        print("No artists meet the threshold criteria.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Please log in to Last.fm in the browser window.")
        page.goto("https://www.last.fm/login")
        input("Press Enter after you are logged in...")

        while len(targets) > 0:
            artist = targets[0]
            try:
                print(f"Deleting: {artist} ({len(targets)-1} remaining)")
                if delete_artist(page, artist):
                    targets.pop(0)
                    with open(CACHE_FILE, "w") as f:
                        json.dump(targets, f)
                else:
                    print(f"Could not find delete button for {artist}. Skipping.")
                    targets.pop(0)
            except Exception as e:
                print(f"Error deleting {artist}: {e}")
                print("Exiting. Restart the script to resume from this artist.")
                break

        browser.close()
        print("Cleanup complete.")

if __name__ == "__main__":
    run()
