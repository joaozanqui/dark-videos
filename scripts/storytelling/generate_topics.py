import json
import scripts.utils.gemini as gemini
import scripts.utils.handle_text as handle_text

def generate(variables, template_prompt, agent_prompt):
    prompt_str = template_prompt.safe_substitute(variables)
    prompt = json.loads(prompt_str)
    response = gemini.run(prompt_json=prompt, agent_prompt=agent_prompt)  

    return response

def validate(topics):
    required_topics = ['introduction', 'development', 'conclusion']
    return all(topic in topics for topic in required_topics)

def run(variables, template_prompt, agent_prompt):
    topics_str = generate(variables, template_prompt, agent_prompt)

    try:
        topics = handle_text.format_json_response(topics_str)

        if not validate(topics):
            print(f"\t\t\t- Topics generated with errors!")
            print(f"\t\t\t- trying again...")
            return run(variables, template_prompt, agent_prompt)
        
        return topics
    except Exception as e:
        print(f"\t\t-Error to get topics: {e}")
        return run(variables, template_prompt, agent_prompt)
