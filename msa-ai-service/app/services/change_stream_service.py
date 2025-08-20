# polling -> change stream으로 변경 시 사용

# from app.db.mongodb import get_collection

# def watch_queries():
#     col = get_collection("qa_queries")
#     with col.watch() as stream:
#         for change in stream:
#             if change["operationType"] == "insert":
#                 doc = change["fullDocument"]
#                 # 처리 로직
