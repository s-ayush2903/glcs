import os
import json

jsFile = os.path.join(os.getcwd() + "branches.json")
jsn = json.loads(jsFile)
print(jsn)
