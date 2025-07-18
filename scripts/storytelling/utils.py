from string import Template

def build_template(variables, step, file_name):
    template_path = f"default_prompts/{step}/{file_name}.txt"

    with open(template_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    template = Template(prompt_template)
    prompt = template.safe_substitute(variables)

    return prompt