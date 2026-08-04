from app.graph.workflow import create_workflow

workflow = create_workflow()

state = {
    "question": "How is authentication implemented?",
    "repository_uploaded": True,
    "repository_indexed": True,
}

result = workflow.invoke(state)

print(result)