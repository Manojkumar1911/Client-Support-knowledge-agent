from Backend.app.core import semantic_kernel_orchestrator as orchestrator
# Monkeypatch retrieve_relevant_docs to mimic test
orchestrator.retrieve_relevant_docs = lambda q, top_k=3: ["Doc one about metrics", "Doc two about metrics"]
res = orchestrator.semantic_kernel_orchestrator("Please summarize the docs", user_id="u1")
print(res)
