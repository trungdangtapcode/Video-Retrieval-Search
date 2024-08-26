import faiss
# import clip
import numpy as np
from utils.embeddingserver import text_feature, image_feature_file, image_feature_url

class FaissDB:
    def __init__(self, bin_file_path, clip_backbone="ViT-B/32", device = "cuda"):
        self.index = faiss.read_index(bin_file_path)
        resource = [faiss.StandardGpuResources()]
        self.index = faiss.index_cpu_to_gpu_multiple_py(resource, self.index)
        # self.model, _ = clip.load(clip_backbone, device=device)
        # self.device = device
        self.text_search('Deutsches Rotes Kreuz Kriseninterventionsteam, HTV9, 06:44:01', 5)

    def text_search(self, text: str, k: int):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        text_features = text_feature(text)
        norm = np.linalg.norm(text_features)
        if (norm!=0):
            text_features /= norm
        

        scores, idx_image = self.index.search(text_features, k=k)
        idx_image = idx_image.squeeze()

        return idx_image
    
    def image_search(self, image, k: int):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        image_features = image_feature_file(image)
        norm = np.linalg.norm(image_features)
        if (norm!=0):
            image_features /= norm
        

        scores, idx_image = self.index.search(image_features, k=k)
        idx_image = idx_image.squeeze()

        return idx_image
    
    def url_search(self, image, k: int):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        image_features = image_feature_url(image)
        norm = np.linalg.norm(image_features)
        if (norm!=0):
            image_features /= norm
        

        scores, idx_image = self.index.search(image_features, k=k)
        idx_image = idx_image.squeeze()

        return idx_image

    def vec_search(self, vec, k: int):
        # text_tokens = clip.tokenize([text]).to(self.device)
        # text_features = self.model.encode_text(text_tokens).cpu().detach().numpy().astype(np.float32)
        norm = np.linalg.norm(vec)
        if (norm!=0):
            vec /= norm
        

        scores, idx_image = self.index.search(vec, k=k)
        idx_image = idx_image.squeeze()

        return idx_image
