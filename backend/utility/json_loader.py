import os
import json

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))

def load_json_knowledge():
    knowledge_data = []

    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(KNOWLEDGE_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    knowledge_data.append({
                        "filename": filename,
                        "content": data
                    })
                except Exception as e:
                    print(f"[WARN] Could not load {filename}: {str(e)}")

    return knowledge_data


def format_json_knowledge_as_text(knowledge_data):
    formatted_sections = []

    for item in knowledge_data:
        section = f" {item['filename']}\n"
        content = item['content']

        if isinstance(content, dict):
            for key, value in content.items():
                section += f"- {key}: {json.dumps(value, indent=2)}\n"
        elif isinstance(content, list):
            for entry in content:
                section += f"- {json.dumps(entry, indent=2)}\n"
        else:
            section += json.dumps(content, indent=2)

        formatted_sections.append(section)

    return "\n\n".join(formatted_sections)


if __name__ == "__main__":
    knowledge = load_json_knowledge()
    print(format_json_knowledge_as_text(knowledge))
