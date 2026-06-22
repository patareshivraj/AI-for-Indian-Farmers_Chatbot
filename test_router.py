from app.router.router import QueryRouter
from app.evaluation.datasets.queries import get_test_dataset

router = QueryRouter()
dataset = get_test_dataset()

for item in dataset:
    res = router.route(item["query"])
    if res.intent.value != item["expected_intent"]:
        print(f"FAILED INTENT: Query='{item['query']}'")
        print(f"  Expected: {item['expected_intent']} | Got: {res.intent.value}")
    elif str(res.tool_name.value if res.tool_name else "None") != str(item["expected_tool"]):
        if str(item["expected_tool"]) != "None":
            print(f"FAILED TOOL: Query='{item['query']}'")
            print(f"  Expected: {item['expected_tool']} | Got: {res.tool_name.value if res.tool_name else 'None'}")
