// 직접 수동 데이터 삽입용
// change stream 쓸 때는 안씀

// const db = db.getSiblingDB("ai_service_db")

// // 기존 콜렉션 드롭
// db.qa_queries.drop()
// db.reviews_denorm.drop()
// db.queries_embedding.drop()
// db.reviews_embedding.drop()
// db.qa_answers.drop()

// // 라벨별 리뷰 문구 샘플
// const reviewSamples = {
//   salty: [
//     "국물이 많이 짜네요.",
//     "간이 세서 밥이랑 먹기 좋아요.",
//     "짜지 않고 딱 좋아요."
//   ],
//   quantity: [
//     "양이 많아요.",
//     "조금 부족했어요."
//   ],
//   deep: [
//     "맛이 깊고 진합니다.",
//     "국물 풍미가 깊어요.",
//     "감칠맛이 뛰어나네요."
//   ],
//   spicy: [
//     "매콤하고 맛있어요.",
//     "엄청 매워요!",
//     "살짝 매콤한 정도예요.",
//     "안매워요"
//   ],
//   sweet: [
//     "달콤하고 부드러워요.",
//     "좀 달아요.",
//     "단맛이 은은합니다.",
//     "완전 달아요."
//   ],
//   size: [
//     "조각이 커서 배부릅니다.",
//     "커요",
//     "사이즈가 작아요.",
//     "적당한 크기였어요."
//   ]
// }

// // 스토어 & 메뉴 정의
// const stores = [
//   {
//     store_name: "한식당",
//     menu_name: "된장찌개",
//     labels: {
//       salty: ["짜지 않나요?", "간이 어떤가요?"],
//       quantity: ["양이 많나요?", "양이 적당한가요?"],
//       deep: ["맛이 깊나요?", "국물 맛이 진한가요?"]
//     }
//   },
//   {
//     store_name: "분식당",
//     menu_name: "떡볶이",
//     labels: {
//       quantity: ["양이 많나요?", "양이 적당한가요?"],
//       spicy: ["맵나요?", "얼얼한 맛이 있나요?"],
//       sweet: ["달콤한가요?", "단맛이 강한가요?"]
//     }
//   },
//   {
//     store_name: "디저트카페",
//     menu_name: "치즈케이크",
//     labels: {
//       size: ["크기가 크나요?", "한 조각이 충분한가요?"],
//       sweet: ["달콤한가요?", "단맛이 강한가요?"],
//       deep: ["맛이 진한가요?", "치즈 풍미가 깊나요?"]
//     }
//   }
// ]

// // 루프 돌면서 삽입
// stores.forEach((store) => {
//   const store_id = UUID().toString()
//   const menu_id = UUID().toString()

//   // 리뷰 20개
//   const reviews = []
//   const labelKeys = Object.keys(store.labels)
//   for (let i = 1; i <= 20; i++) {
//     const label = labelKeys[i % labelKeys.length]
//     const sampleTexts = reviewSamples[label]
//     const text = sampleTexts[Math.floor(Math.random() * sampleTexts.length)]
//     reviews.push({
//       review_id: UUID().toString(),
//       text: text,
//       created_at: new Date()
//     })
//   }

//   db.reviews_denorm.insertOne({
//     _id: store_id,
//     store_name: store.store_name,
//     menus: [
//       {
//         menu_id: menu_id,
//         menu_name: store.menu_name,
//         reviews: reviews
//       }
//     ],
//     updated_at: new Date()
//   })

//   // 질문 (라벨별 2개씩)
//   const questions = []
//   for (const [label, qs] of Object.entries(store.labels)) {
//     qs.forEach(qtext => {
//       questions.push({
//         request_id: UUID().toString(),
//         question: qtext
//       })
//     })
//   }

//   db.qa_queries.insertOne({
//     _id: store_id,
//     store_name: store.store_name,
//     menus: [
//       {
//         menu_id: menu_id,
//         menu_name: store.menu_name,
//         questions: questions
//       }
//     ],
//     updated_at: new Date()
//   })
// })
