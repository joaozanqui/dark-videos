from scripts.utils import analyze_with_gemini, export
from string import Template

def get_prompt(variables):
    template_file = f"scripts/images/prompts/generate.txt"

    with open(template_file, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    template = Template(prompt_template)
    
    prompt = template.safe_substitute(variables)
    return prompt


def run(title, rationale, full_script):
    variables = {
        "VIDEO_TITLE": title,
        "RATIONALE": rationale,
        "FULL_SCRIPT": full_script
    }

    prompt = get_prompt(variables)
    image_prompt = analyze_with_gemini(prompt)

    return image_prompt