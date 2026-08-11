# Syncing Gemini Extensions Across Devices

If you want to sync your installed Gemini/Antigravity extensions (plugins and skills) from one machine to another, use the `sync-gemini-extensions.sh` script located in this folder.

## 1. On the "Source" Device (The machine that has all the extensions)

First, run the export command to copy your installed extensions into this git repository:
```bash
cd docs/migrations
./sync-gemini-extensions.sh export
```

Then, commit and push those files to your Git remote:
```bash
git add gemini_extensions/
git commit -m "Export latest Gemini extensions"
git push
```

## 2. On the "Target" Device (The machine you want to update)

First, pull the latest changes so you have the `gemini_extensions` folder from the source device:
```bash
git pull
```

Next, run the import command to copy those extensions into this machine's local Gemini configuration:
```bash
cd docs/migrations
./sync-gemini-extensions.sh import
```

Finally, **restart your Gemini/Antigravity instance** so that it recognizes and loads the new extensions.
