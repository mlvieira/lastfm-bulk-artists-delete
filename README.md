## Last.fm bulk artists delete

Since last.fm doesn't offer a solution to bulk delete artists, this is it.

### Warning
You **MAY** be banned for using this. So don't go too fast.

## Instructions

1. Clone the repo
2. Create a virtual env
3. Activate virtual env
4. Install requirements
5. Install browser binary
```
playwright install chromium
```
6. Create an API key in [Last.fm](https://www.last.fm/api/account/create)
7. Edit config
```
cp config.example.json config.json
```
8. Run the script
9. A chromium instance will spawn after the artists had been fetched in the last.fm login page, you will need to login and **press** enter in the terminal to continue

## Known Problems
- Sometimes it dies randomly. Just restart the script.
