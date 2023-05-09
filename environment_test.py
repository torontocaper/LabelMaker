import os

import dotenv

dotenv.load_dotenv()

app_id = os.environ.get("APP_ID")
print(app_id)