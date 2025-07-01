from string import Template

def build_prompt_template(variables, step, agent=False):
    template_path = f"scripts/storytelling/{'agents' if agent else 'prompts'}/"
    template_file = f"{template_path}{step}.txt"

    with open(template_file, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    template = Template(prompt_template)
    
    prompt = template.safe_substitute(variables)
    return prompt