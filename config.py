"""
Site configuration.

This is the only file you need to touch to change your name, links, or where
the site is hosted. Everything else is content (in content/) or presentation
(in templates/ and static/).
"""

SITE = {
    # ---- identity -------------------------------------------------------
    "title": "Robbie Karas",
    "tagline": "Project write-ups and dev logs.",
    "author": "Robbie Karas",
    "email": "robbiekaras@gmail.com",
    "description": (
        "Project write-ups and development logs from Robbie Karas, "
        "a computer information systems and cybersecurity student at "
        "James Madison University."
    ),

    # ---- hosting --------------------------------------------------------
    # url:      the origin your site is served from, no trailing slash.
    # base_url: the sub-path your site lives at. It is "" for a user-site repo
    #           named "robbiekaras.github.io" (served at the root). If you ever
    #           move to a normal project repo, set this to "/<repo-name>".
    "url": "https://robbiekaras.github.io",
    "base_url": "",

    # Set this to a domain (e.g. "robbiekaras.blog") only if you buy one and
    # want GitHub Pages to serve it. Leave as None otherwise. If you set it,
    # also set base_url to "" and url to "https://<your-domain>".
    "cname": None,

    # ---- links ----------------------------------------------------------
    "links": [
        {"name": "GitHub", "url": "https://github.com/RobbieKaras"},
        {"name": "LinkedIn", "url": "https://www.linkedin.com/in/robbie-karas/"},
        {"name": "Email", "url": "mailto:robbiekaras@gmail.com"},
    ],

    # ---- navigation -----------------------------------------------------
    # "key" is matched against the page's active section to highlight the tab.
    "nav": [
        {"name": "Projects", "url": "/projects/", "key": "projects"},
        {"name": "Posts", "url": "/posts/", "key": "posts"},
        {"name": "About", "url": "/about/", "key": "about"},
    ],

    # ---- behaviour ------------------------------------------------------
    "feed_limit": 25,          # how many items in feed.xml
    "home_recent_posts": 4,    # how many standalone posts on the homepage
    "home_recent_updates": 5,  # how many recent project updates on the homepage
}
