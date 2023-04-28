import json

from jsonschema import validate

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "organization": {"type": "string"},
        "critical": {"type": "boolean"},
        "external-contributions": {"type": "boolean"},
    },
    "required": ["name", "email", "critical", "external-contributions"],
}

if __name__ == "__main__":
    with open("public-repositories/published-repositories.json") as f:
        repos_object = json.load(f)
        for repo in repos_object:
            validate(repo, schema=schema)

        sorted_list = sorted(repos_object, key=lambda d: d["name"])
        if repos_object != sorted_list:
            raise Exception("published-repositories.json is not correctly sorted")

        unique_list = list({v["name"]: v for v in repos_object}.values())
        if len(repos_object) != len(unique_list):
            raise Exception("published-repositories.json contains duplicate entries")
