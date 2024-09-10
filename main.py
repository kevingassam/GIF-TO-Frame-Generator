from fastapi import FastAPI, File, UploadFile, HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import shutil
import os
import random
import zipfile


app = FastAPI()

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

UrlApi = "http://127.0.0.1:8000"



# Mount the directory to serve static files
app.mount("/output", StaticFiles(directory="output"), name="static")

@app.get("/")
async def read_root():
    return {"success":True, "message": "Welcome to the GIF Generator API!"}





@app.post("/generate")
async def CreateGif(file: UploadFile = File(...)):
    try:
        img = Image.open(file.file)
    except Exception as e:
        return {"success":False, "message": "Erreur lors du chargement du fichier !" , "errors" : {str(e)}}
    
        

    # Vérifier que l'image est bien chargée et que c'est un GIF
    if img is None or img.format.lower() != "gif":
        return {"success":False, "message": "Le fichier envoyé n'est pas un GIF."}

    # Calcul de la durée totale du GIF
    duration = 0
    try:
        while True:
            frame_duration = img.info['duration']  # Durée de la frame actuelle
            duration += frame_duration
            img.seek(img.tell() + 1)  # Aller à la frame suivante
    except EOFError:
        pass
    except KeyError:
        raise HTTPException(status_code=400, detail="Le GIF ne contient pas d'information de durée.")

    # Créer un dossier aléatoire pour sauvegarder les images extraites du GIF
    random_directory = "output/output_" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
    os.makedirs(random_directory, exist_ok=True)

    # Sauvegarder chaque frame du GIF en PNG
    frame_rate = 30
    img.seek(0)  # Revenir à la première frame
    for i in range(frame_rate):
        try:
            img.seek(i)
            img.save(f"{random_directory}/frame_{i}.png")
        except EOFError:
            break  # Sortir de la boucle si on atteint la fin du GIF
        
    
    total_files = len(os.listdir(random_directory))
    first_file = os.listdir(random_directory)[0]
    last_file = os.listdir(random_directory)[-1]
    
        
    # Creer un ficier index.html dans le meme dossier
    with open("models/html.html", 'r') as source_file:
        content = source_file.read()
        # Effectuer plusieurs remplacements
        
    replacements = {
        "total_image": str(total_files),
    }
        
    for old_value, new_value in replacements.items():
        content = content.replace(old_value, new_value)

    # Créer le fichier index.html avec le contenu modifié
    with open(random_directory+"/index.html", 'w') as target_file:
        target_file.write(content)
    
        
       
    # Zipper les images PNG dans un ZIP
    with zipfile.ZipFile(random_directory+".zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(random_directory):
            for file in files:
                file_path = os.path.join(root, file)
                # Ajouter le fichier au ZIP
                zipf.write(file_path, os.path.relpath(file_path, random_directory))
    
        
    
    #return json value
    data = { 
      "Folder": random_directory, 
      "first_file": first_file, 
      "last_file": last_file, 
      "total_files": total_files,
      "download_link_zip": f"{UrlApi}/{random_directory}.zip",
      "api": UrlApi,
      "success" : True, 
    } 
    
    
    
    
    #supprimier le dossier meme si ce nest pas vide
    shutil.rmtree(random_directory)

    return data



@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={"detail": "La ressource demandée n'a pas été trouvée. 404"}
    )


