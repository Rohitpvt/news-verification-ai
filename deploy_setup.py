import os
import json

# Create vercel.json
vercel_config = {
    "version": 2,
    "builds": [
        {"src": "app.py", "use": "@vercel/python"}
    ],
    "routes": [
        {"src": "/(.*)", "dest": "app.py"}
    ]
}

with open('vercel.json', 'w') as f:
    json.dump(vercel_config, f, indent=2)

print("✅ Created vercel.json")

# Create Procfile for Heroku/Render
with open('Procfile', 'w') as f:
    f.write('web: gunicorn -w 4 --timeout 120 -b 0.0.0.0:$PORT app:app\n')

print("✅ Procfile ready for Render/Heroku")

# Create .env.example
with open('.env.example', 'w') as f:
    f.write('''# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# Port Configuration
PORT=5000

# API Keys (optional for future enhancements)
# NEWS_API_KEY=your-newsapi-key
''')

print("✅ Created .env.example")

print("\n🚀 Deployment setup complete!")
print("Next steps:")
print("1. Push changes to GitHub")
print("2. Visit https://vercel.com/ and connect your repo")
print("3. Or use Render at https://render.com/")
