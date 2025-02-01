import os
import uvicorn
from dotenv import load_dotenv
from driver import app  # Use the configured app from driver.py

load_dotenv()

folders = [
    os.path.join(os.path.dirname(__file__), "logs"),
    os.path.join(os.path.dirname(__file__), "uploads"),
]

if __name__ == "__main__":
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            
    uvicorn.run(
        app,  # Use the configured app from driver.py
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT") or 8001),
        reload=False,
        use_colors=True,
        access_log=True,
        log_level="info",
        forwarded_allow_ips="*",
        proxy_headers=True,
        headers=[("server", "Girikon AI")],
    )
