from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import utils.myfaiss
import utils.embeddingserver
import json
import numpy as np
import validators


EMBEDDING_SERVER = "http://192.168.0.106/"
BIN_ALIGN_PATH = "../preprocess/normalizedALIGN.index"
KEYFRAMES_JSON = "keyframes_path.json"
DATA_PATH = "../data"
KEYFRAMES_PATH = DATA_PATH+"/keyframes"
RESIZED_PATH = DATA_PATH+"/keyframes_resized"

utils.embeddingserver.EMBEDDING_SERVER = EMBEDDING_SERVER

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

app = FastAPI()
db = utils.myfaiss.FaissDB(BIN_ALIGN_PATH)

with open('thumbnail_path.json') as json_file: #tam thoi
    json_dict = json.load(json_file)
imgidx2path = {}
imgidx2thumbnailidx = {}
thumbnailidx2imgidx =  {}
thumbnailidx2path = {}
for key, value in json_dict.items():
    imgidx2path[int(key)] = value
    imgidx2thumbnailidx[int(key)] = int(key)
    thumbnailidx2imgidx[int(key)] = [int(key)]
thumbnailidx2path = imgidx2path

keyframes_path = json.load(open(KEYFRAMES_JSON))

app.mount("/palette", StaticFiles(directory="static/palette"), name="home")
app.mount("/concac", StaticFiles(directory="static"), name="static")
app.mount("/img", StaticFiles(directory="static/img"), name="img")
app.mount("/data", StaticFiles(directory=DATA_PATH), name="data")

@app.get("/")
async def root():
    return "hello"

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, scene_description: str|None = None,
            num_clip_query: int = 24, url_query: str|None = None,
            query_type: str|None = None):
    img_idx = None
    global uploaded_img
    if (query_type=='image' and uploaded_img != None):
        img_idx = db.vec_search(uploaded_img_feature, num_clip_query)
    if (query_type=='url' and validators.url(url_query)):
        img_idx = db.url_search(url_query, num_clip_query)
    if (query_type=='text' and scene_description != None):
        img_idx = db.text_search(scene_description,num_clip_query)
    
    data = []
    if (not img_idx is None):
        for idx in img_idx:
            # if (idx not in imgidx2path):
            #     continue
            data.append({'frame_index':idx, 'path': 'data/keyframes/'+keyframes_path[idx]})
        # print(scene_description, data)
        with open('static/reponse/data.json', 'w') as f:
            json.dump(data, f, cls=NpEncoder)
        print(data)

    return templates.TemplateResponse(
        request=request, name="home.html", 
        context={"id": id, "scene_description":scene_description,
                "num_clip_query": num_clip_query, "url_query": url_query,
                "query_type": query_type, 
                "data_response": json.dumps(data, cls=NpEncoder)}
        , data = "con cac"
    )

@app.get("/thumbnail_template/{img_idx}", response_class=HTMLResponse)
async def thumbnail_template(request: Request, img_idx: int):
    path = ""
    # if (img_idx in imgidx2path):
    #     path = imgidx2path[img_idx]
    print('thumbnail queried index: ',img_idx)
    path = 'keyframes_resized/'+keyframes_path[img_idx]
    return templates.TemplateResponse(
        request=request, name="thumbnail_box.html", 
            context={"thumbnail_path": path, 
                    "img_idx":img_idx,  
                    "keyframe_path": 'keyframes/'+keyframes_path[img_idx]}
                    , data = "con cac"
    )

templates = Jinja2Templates(directory="templates")
@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


uploaded_img = None
uploaded_img_feature = None
@app.post("/upload_image")
async def image_query_upload(image: UploadFile = File(...)):
    global uploaded_img, uploaded_img_feature
    uploaded_img = image.file
    uploaded_img_feature = utils.embeddingserver.image_feature_file(uploaded_img)
    print(uploaded_img_feature)
    return {"filename": image.filename}

@app.get("/test", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": id, "scene_description":"nam mo"}, data = "con cac"
    )

@app.get("/test_embedding")
async def test_embedding():
    vec = utils.embeddingserver.text_feature("I love you baby")
    return json.dumps(vec, cls=NpEncoder)