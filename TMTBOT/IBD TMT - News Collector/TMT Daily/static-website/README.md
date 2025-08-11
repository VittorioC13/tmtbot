# TMT Daily Briefs Website

A modern, responsive website for displaying TMT (Technology, Media, and Telecommunications) daily briefs.

## Running Locally

1. Clone this repository or download the files
2. Copy your PDF briefs to the `assets` folder with the naming format `brief_YYYY-MM-DD.pdf`
3. Open `index.html` in your web browser

Alternatively, you can use a local server:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js
npx serve
```

Then visit `http://localhost:8000` in your browser.

## Deploying to Vercel

1. Install the Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

## Deploying to Netlify

1. Install the Netlify CLI:
```bash
npm install -g netlify-cli
```

2. Login to Netlify:
```bash
netlify login
```

3. Deploy:
```bash
netlify deploy
```

## Manual Deployment

You can also deploy manually to either platform:

1. Push your code to a GitHub repository
2. Connect your repository to Vercel or Netlify
3. Configure the build settings:
   - Build command: (leave empty)
   - Publish directory: ./
4. Deploy!

## File Structure

```
static-website/
├── index.html
├── css/
│   └── styles.css
├── js/
│   └── main.js
└── assets/
    └── brief_*.pdf
```

## Customization

- Edit `js/main.js` to update the list of briefs and their descriptions
- Modify `css/styles.css` to change the website's appearance
- Update `index.html` to modify the structure and content 