import scripts.utils.gemini as gemini
import scripts.utils.handle_text as handle_text
import scripts.database as db

def generate(variables: dict, template_prompt: dict, agent_prompt: str):
    prompt = handle_text.substitute_variables_in_json(template_prompt, variables)
    response = gemini.run(prompt_json=prompt, agent_prompt=agent_prompt)  

    return response

def validate(topics: dict, variables: dict):
    required_topics = ['introduction', 'development', 'conclusion']
    has_all_topics = all(topic in topics for topic in required_topics)
    if not has_all_topics:
        return False

    right_number_of_dev_topics = len(topics['development']) == variables['NUMBER_OF_DEV_TOPICS']

    if not right_number_of_dev_topics:
        return False
    
    for dev_topic in topics['development']:
        if (len(dev_topic) - 1) < variables['NUMBER_OF_SUBTOPICS_MIN'] or (len(dev_topic) - 1) > variables['NUMBER_OF_SUBTOPICS_MAX']:
            print(dev_topic)
            print(len(dev_topic) - 1)
            return False
        
    return True


def run(variables: dict, template_prompt: dict, agent_prompt: str):
    topics_str = generate(variables, template_prompt, agent_prompt)

    try:
        topics = handle_text.format_json_response(topics_str)

        if not validate(topics, variables):
            print(f"\t\t\t- Topics generated with errors!")
            print(f"\t\t\t- trying again...")
            return run(variables, template_prompt, agent_prompt)
        
        return topics
    except Exception as e:
        print(f"\t\t-Error to get topics: {e}")
        return run(variables, template_prompt, agent_prompt)
