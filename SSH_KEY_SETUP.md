# SSH Key Setup

## Your SSH Public Key

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPuwkRTBsFglR8HVuTlvc5R6U6n/VZcRvCkcjx9AJj/Q autodl
```

## Setup Steps

1. Go to GitHub Settings → SSH and GPG keys → New SSH key
2. Add the key above
3. Configure git to use SSH:
   ```bash
   git remote set-url origin git@github.com:disdorqin/power-papers-daily.git
   ```

## GitHub Pages Configuration

After setting up SSH, configure GitHub Pages:
1. Go to https://github.com/disdorqin/power-papers-daily/settings/pages
2. Select "Deploy from a branch"
3. Select "gh-pages" branch
4. Click Save

Your site will be available at: https://disdorqin.github.io/power-papers-daily/sota.html