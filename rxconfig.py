import reflex as rx

config = rx.Config(
    app_name="mmuhg",
    api_url="http://localhost:8000",
    show_reflex_badge=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)