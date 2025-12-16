# Forward API Documentation

A static documentation site for the Checkout.com Forward API, hosted on GitHub Pages.

## 🚀 How to publish to GitHub Pages

1. **Push this repository to GitHub**
   ```bash
   git add .
   git commit -m "Add Forward API documentation"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Navigate to **Settings** → **Pages**
   - Under "Source", select **Deploy from a branch**
   - Select the **main** branch and **/ (root)** folder
   - Click **Save**

3. **Access your site**
   - Your documentation will be available at: `https://<username>.github.io/forward-api-guide/`
   - It may take a few minutes for the initial deployment

## 📝 Editing the documentation

The main documentation is in `index.md`. It's written in standard Markdown, making it easy to edit.

### Key sections:
- **Forward API basics** - How to create forward requests
- **Placeholder values** - Card, billing, and network token placeholders
- **Building requests** - Variables, query parameters, and JWE encryption
- **Secrets management** - Storing and using API keys securely
- **Integration examples** - Stripe, Adyen, and Visa implementations

## 🎨 Customizing the theme

The site uses the [Cayman theme](https://github.com/pages-themes/cayman). You can change this in `_config.yml`:

```yaml
# Available themes:
# - pages-themes/cayman@v0.2.0
# - pages-themes/minimal@v0.2.0
# - pages-themes/slate@v0.2.0
# - pages-themes/hacker@v0.2.0
# - pages-themes/midnight@v0.2.0
remote_theme: pages-themes/cayman@v0.2.0
```

## 📁 Files

| File | Purpose |
|------|---------|
| `index.md` | Main documentation content |
| `_config.yml` | Jekyll configuration and theme settings |
| `forward_api_visa.py` | Python example for Visa integration |
| `README.md` | This file |

## 🔧 Local preview (optional)

To preview locally before publishing:

```bash
# Install Jekyll
gem install bundler jekyll

# Run local server
bundle exec jekyll serve

# Open http://localhost:4000
```

