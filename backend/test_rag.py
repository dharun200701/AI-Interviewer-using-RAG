from rag_pipeline import search_questions

query = "How do you handle conflict in a team?"

results = search_questions(query)

for r in results:
    print("\nQuestion:", r["question"])
    print("Answer:", r["ideal_answer"])