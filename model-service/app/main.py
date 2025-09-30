import grpc
from concurrent import futures
import model_pb2, model_pb2_grpc
from app.ml.embedding_model import embedding_model
from app.db.mongodb import get_collection
from app.services.labeling_service import LabelingService

queries_embedding_col = get_collection("queries_embedding")
reviews_embedding_col = get_collection("reviews_embedding")

labeling_service = LabelingService()

class ModelService(model_pb2_grpc.ModelServiceServicer):
    def GetEmbedding(self, request, context):
        text = request.text
        meta = dict(request.meta)

        # 1. KoSimCSE 임베딩
        embedding = embedding_model.encode([text])[0]

        # 2. OpenAI 라벨링
        mode = "review" if meta.get("type") == "review" else "question"
        label, polarity = labeling_service.embed_and_label(text, mode)

        # 3. MongoDB 저장
        if meta.get("type") == "query":
            queries_embedding_col.insert_one({
                "_id": meta["query_id"],
                "store_id": meta["store_id"],
                "menu_id": meta["menu_id"],
                "query": text,
                "embedding": embedding,
                "label": label,
                "polarity": polarity
            })
        else:
            reviews_embedding_col.insert_one({
                "_id": meta["review_id"],
                "store_id": meta["store_id"],
                "menu_id": meta["menu_id"],
                "review": text,
                "embedding": embedding,
                "label": label,
                "polarity": polarity
            })

        return model_pb2.EmbeddingResponse(status="ok")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_pb2_grpc.add_ModelServiceServicer_to_server(ModelService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("🚀 model-service gRPC server started at 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
