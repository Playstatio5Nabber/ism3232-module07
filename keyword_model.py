# keyword_model.py
# Author: Sami Ali


class KeywordModel:
    """Offline lookup model; changes and calculations require explicit tools."""

    def decide(self, instructions, history, tools):
        last = history[-1]
        if last["role"] == "tool":
            return {"text": last["content"]}
        text = last["content"].lower()
        if "change" in text or "calculate" in text:
            return {
                "text": "Offline mode supports plan and estimate lookups. Ask staff for calculations or changes."
            }
        if (
            "estimate" in text
            or "example e" in text
            or any(word.strip("?.!,").startswith("e1") for word in text.split())
        ):
            return {
                "tool": "look_up_estimate",
                "arguments": {"estimate_id": last["content"]},
            }
        if "plan" in text or any(
            word.strip("?.!,").startswith("p") and word.strip("?.!,")[1:].isdigit()
            for word in text.split()
        ):
            return {"tool": "look_up_plan", "arguments": {"plan_id": last["content"]}}
        if "hello" in text:
            return {"text": "Hello! I can look up a sample plan or saved estimate."}
        return {
            "text": "I can look up a sample plan or saved estimate. Please give its ID."
        }
