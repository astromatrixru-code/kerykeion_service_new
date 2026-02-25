import os

class Settings:
    PROJECT_NAME: str = "Natalchartruler Kerykeion API"
    BASE_OUTPUT_DIR: str = "/tmp" if os.path.exists("/tmp") else os.getcwd()
    
    ALLOWED_HOSTS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://natalchartruler.com/",
        "https://www.natalchartruler.com"
        "http://localhost:8000",          
        "http://127.0.0.1:8000"
    ]

settings = Settings()