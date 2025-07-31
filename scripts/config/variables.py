from scripts.utils import analyze_with_gemini, format_json_response, get_prompt
import scripts.sanitize as sanitize
import scripts.database as database
import json

VARIABLES = [
    {    
        "NICHE_DESCRIPTION": "Description of the channels niche (e.g., Personal Development based on Stoic Philosophy, Mindfulness for Busy Moms).",
        "NICHE_CORE_CONCEPTS": "The main theories or ideas of the niche (e.g., quantum manifestation, spiritual neuroscience, Law of Attraction, mental reprogramming).",
        "NICHE_KEY_METRIC": "A key concept or metric in the niche (e.g., vibration, frequency, mindset).",
        "NICHE_PRACTICE_EXAMPLES": "Specific rituals, disciplines, or practices that are common and significant for the target audience (e.g., praying, climbing mountains, fasting; or journaling, meditating daily, scripting affirmations).",
        "NICHE_REVERENCE_WORDS_EXAMPLES": "Examples of specific words or short phrases that the audience uses to express reverence, gratitude, or connection, indicating their cultural or spiritual dialect (e.g., 'gratitude', 'Danke', 'hallelujah'; or 'amor fati', 'memento mori', 'namaste').",
        "NICHE_JARGON_CATEGORY_1": "Category of specialized terms or jargon from the niche that should be explained emotionally rather than used technically (e.g., 'theological terms', 'scientific terms'; or 'metaphysical concepts', 'psychological terms').",
        "NICHE_JARGON_CATEGORY_2": "Other Category of specialized terms or jargon from the niche that should be explained emotionally rather than used technically (e.g., 'theological terms', 'scientific terms'; or 'metaphysical concepts', 'psychological terms').",
        "NICHE_POWER_WORDS_LIST": "A list of keywords and concepts that have a strong emotional and spiritual resonance with the target audience (e.g., Consecration, Calling, Divine Silence, Inner Healing, Sacred Loneliness, Altar, Hidden Testimony).",
        "SUB_THEMES_EXAMPLES": "List of sub-themes relevant to the niche (e.g., fear of failure, procrastination, search for meaning, breathing techniques, guided meditation, daily mindfulness).",
        "COMMUNITY_RELATED_TO_NICHE": "Community or culture related to the niche.",
        "IDEALIZED_FIGURE_IN_NICHE": "Idealized figure in the niche.",
        "DEITY_OR_CONCEPT": "The central higher power, universal principle, or core concept that the audience connects with or seeks guidance from (e.g., God, the Universe, the Logos, Source, Higher Self, the Divine Mind).",
        "GUIDANCE_TYPE": "The type of guidance offered (e.g., mental, emotional, practical, philosophical).",
        "STYLE_BLEND_COMPONENTS": "The core concepts or fields that are blended together to create the channel's unique perspective (e.g., practical spirituality and emotional neuroscience; or Stoic philosophy and modern psychology).",
        "ANALYTICAL_LENSES": "The perspectives used for analysis (e.g., philosophical, neuroscientific, emotional, and symbolic).",
    },
    {   
        "TARGET_AUDIENCE_DEMOGRAPHICS_AND_PSYCHOGRAPHICS": "Detailed description of the target audience.",
        "TARGET_AUDIENCE_DEMOGRAPHICS_AND_PSYCHOGRAPHICS_DETAILED": "A detailed paragraph describing the target audience, including their demographics (age, life situation) and psychographics (inner world, beliefs, feelings, spiritual profile).",
        "AUDIENCE_DESIRES": "The primary things the audience is looking for (e.g., balance, reconnection, purpose).",
        "AUDIENCE_DESIRE_1": "The audiences main desire.",
        "AUDIENCE_DESIRE_2": "Other audiences main desire.",
        "AUDIENCE_DESIRE_3": "Other audiences main desire.",
        "AUDIENCE_DESIRE_4": "Other audiences main desire.",
        "DETAILED_AUDIENCE_DESIRES_LIST": "A comprehensive, bulleted list detailing the implicit, deep desires of the target audience (e.g., - To feel heard by God in a clear and intimate way. - To have their waiting and suffering validated.).",
        "TARGET_AUDIENCE_WANTS": "What the audience values instead of clichés (e.g., deep clarity, applicable guidance, and transformative narratives).",
        "UNANSWERED_QUESTION_OR_DESIRE": "The audiences deep question or desire (e.g., search for acceptance, need for belonging, longing for inner peace).",
        "DESIRED_SKILL_OR_CONNECTION": "Skill or connection the audience desires (e.g., intuition, connection with purpose).",
        "DESIRED_STATE_OR_ACTION": "Desired state or action by the audience.",
        "DESIRED_THING": "Thing desired by the audience.",
        "GOAL_TO_DISCERN": "What is sought to be discerned/understood.",
        "DESIRED_OUTCOME_FOR_AUDIENCE": "Desired outcome for the audience (e.g., healing, growth, clarity).",
        "TARGET_AUDIENCE_SPECIFIC_FOCUS_IF_APPLICABLE": "Specific focus within a scientific field for the audience.",
        "TARGET_AUDIENCE_MEMBERS_REAL_CASES": "Type of audience members whose cases can be used.",
    },
    {
        "CORE_AUDIENCE_PAIN_OR_GOAL": "The primary pain, challenge, or goal of the target audience (e.g., overcoming anxiety, finding professional purpose, coping with grief).",
        "CORE_AUDIENCE_PAIN_EXAMPLES": "Specific, concrete examples of the audience's pain points that the content will directly address (e.g., loneliness, abandonment, unanswered prayers; or professional burnout, fear of the future, lack of purpose).",
        "DETAILED_AUDIENCE_PAINS_LIST": "A comprehensive, bulleted list detailing the specific, nuanced emotional and spiritual pains of the target audience. This is used to give the AI deep context (e.g., - Feeling invisible even while praying intensely. - Carrying the weight of unspoken emotional abandonment.).",
        "PAIN_KEYWORD": "Keyword representing the pain/problem.",
        "IDENTITY_WOUND_EXAMPLE": "IDENTITY WOUND Examples of niche-specific wounds.",
        "FAITH_VOID_EXAMPLE": "FAITH VOID Examples of niche-specific wounds or blocks.",
        "EMOTIONAL_BLOCK_EXAMPLE": "EMOTIONAL BLOCK Examples of niche-specific blocks.",
        "EMOTIONAL_WOUND_TYPE": "Type of emotional wound the theme might address (e.g., rejection wound, fear of abandonment, low self-esteem).",
        "WOUNDED_ASPECT": "Wounded aspect of the person.",
        "KNOWLEDGE_BASE_RELATED_WOUND_TYPE": "Type of wound related to the knowledge base (e.g., philosophical wound, cognitive dissonance).",
        "ENERGY_BLOCK_EXAMPLE_1": "Niche-specific example of blockages (e.g., energetic leak, unconscious block).",
        "ENERGY_BLOCK_EXAMPLE_2": "Other Niche-specific example of blockages (e.g., energetic leak, unconscious block).",
        "HIDDEN_ISSUES_EXAMPLES": "Examples of hidden problems the content seeks to reveal (e.g., unconscious limiting beliefs, self-sabotage patterns, unmet emotional needs).",
        "HIDDEN_ISSUES_EXAMPLES_SINGULAR_FORM": "Singular form of the hidden issue examples.",
        "AUDIENCE_EXPERIENCES_WITH_THE_THEME": "Bad experiences that the audience has had with the theme and for which they are looking for answers.",
        "COMMON_DISTORTION_SUBJECTS": "Subjects about which there are common distortions in the niche (e.g., success, happiness, relationships, productivity, discipline).",
        "COMMON_MISUNDERSTANDING_IN_NICHE": "A common misunderstanding within the niche.",
        "EMOTIONAL_OR_COGNITIVE_ERROR_TYPE": "Type of error (e.g., cognitive bias, emotional trap).",
        "POSITIVE_TRAIT": "Positive trait that the error mimics.",
        "NEGATIVE_BEHAVIOR": "Negative behavior that the error hides.",
        "NEGATIVE_OUTCOME_OR_BLOCK": "Negative outcome or block.",
        "UNADDRESSED_ISSUES": "Unresolved issues.",
    },
    {
        "STYLE_REFERENCE_LIST": "A simple, comma-separated list of key authors, thinkers, or figures who serve as the primary style and content inspiration (e.g., Charles Stanley, David Wilkerson, A. W. Tozer; or Seneca, Epictetus, Marcus Aurelius).",
        "STYLE_REFERENCE_LIST_DETAILED": "A more detailed list of inspirational figures, where each name is followed by a brief parenthetical description of their specific contribution or style (e.g., Charles Stanley (pastoral and welcoming teaching), David Wilkerson (prophetic and broken messages), A. W. Tozer (intimacy with God)).",
        "STYLE_REFERENCE_PERSON_1": "Person who are style references.",
        "STYLE_REFERENCE_PERSON_2": "Other Person who are style references.",
        "STYLE_REFERENCE_PERSON_3": "Other Person who are style references.",
        "STYLE_REFERENCE_PERSON_1_FOCUS": "The focus/specialty of this reference person.",
        "STYLE_REFERENCE_PERSON_2_FOCUS": "Other focus/specialty of this reference person.",
        "STYLE_REFERENCE_PERSON_3_FOCUS": "Other focus/specialty of this reference person.",
        "STYLE_INGREDIENT_1": "Component that form the channels unique style.",
        "STYLE_INGREDIENT_2": "Other Component that form the channels unique style.",
        "STYLE_INGREDIENT_3": "Other Component that form the channels unique style.",
        "STYLE_INGREDIENT_4": "Other Component that form the channels unique style.",
        "STYLE_INGREDIENT_5": "Other Component that form the channels unique style.",
        "LANGUAGE_STYLE_ADJECTIVES": "Adjective describing the language style (e.g., clear, concise, empathetic, formal, academic, provocative).",
        "LANGUAGE_STYLE_ADJECTIVES_2": "Other Adjective describing the language style (e.g., clear, concise, empathetic, formal, academic, provocative).",
        "TONE_VERB_1": "Verb describing the desired tone.",
        "TONE_VERB_2": "Other Verb describing the desired tone.",
        "TONE_VERB_3": "Other Verb describing the desired tone.",
        "TONE_VERB_4": "Other Verb describing the desired tone.",
        "TONE_DESCRIPTION_DETAILED": "A detailed description of the script's tone, outlining its intended effect on the viewer and its underlying philosophy (e.g., Therapeutic and clarifying. It guides the viewer to awareness without guilt.).",
        "APPROVED_PHRASES_EXAMPLES": "A list of specific, niche-aligned key phrases and affirmations that resonate deeply with the audience and can be used in the script (e.g., 'What the world calls loneliness, heaven calls preparation.', 'You were separated, not rejected.').",
        "REVELATION_KEYWORD": "Keyword representing the solution/revelation.",
    },
    {        
        "KNOWLEDGE_BASE_MAIN": "The primary source of knowledge or authority in the niche (e.g., Stoic Philosophy, Principles of Positive Psychology, Buddhist Sacred Texts).",
        "SPECIFIC_FOCUS_WITHIN_KNOWLEDGE_BASE": "A specific focus within the main knowledge base.",
        "CORE_TEXTS_OR_PRINCIPLES_OF_NICHE": "Core texts or principles of the niche.",
        "SECONDARY_REFERENCE_EXAMPLE_1": "Thinker or source from outside the primary niche whose ideas can be subtly incorporated, as long as they are connected back to the core message (e.g., 'Gregg Braden', 'Joe Dispenza'; or 'Carl Jung', 'Jordan Peterson').",
        "SECONDARY_REFERENCE_EXAMPLE_2": "Other Thinker or source from outside the primary niche whose ideas can be subtly incorporated, as long as they are connected back to the core message (e.g., 'Gregg Braden', 'Joe Dispenza'; or 'Carl Jung', 'Jordan Peterson').",
        "SOURCE_TEXT_OR_MODEL_EXAMPLE": "Example of a source text or model.",
        "HISTORICAL_OR_ARCHETYPAL_FIGURE": "Relevant historical or archetypal figure.",
        "RELEVANT_LESSON": "Relevant lesson drawn from the figure.",
        "SCIENTIFIC_FIELD_1": "Scientific field to be referenced.",
        "SCIENTIFIC_FIELD_2": "Other Scientific field to be referenced.",
        "SCIENTIFIC_FIELD_3_NEURO": "Other Scientific field to be referenced.",
    },
    {
        "TOPIC_STRUCTURE_STEP1_DESCRIPTION": "Description for each step of the development topic structure (e.g., Step 1: A magnetizing phrase that blends curiosity, emotion, and impact.).",
        "TOPIC_STRUCTURE_STEP2_DESCRIPTION": "Other Description for each step of the development topic structure (e.g., Step 1: A magnetizing phrase that blends curiosity, emotion, and impact.).",
        "TOPIC_STRUCTURE_STEP3_DESCRIPTION": "Other Description for each step of the development topic structure (e.g., Step 1: A magnetizing phrase that blends curiosity, emotion, and impact.).",
        "TOPIC_STRUCTURE_STEP4_DESCRIPTION": "Other Description for each step of the development topic structure (e.g., Step 1: A magnetizing phrase that blends curiosity, emotion, and impact.).",
        "TOPIC_STRUCTURE_STEP5_DESCRIPTION": "Other Description for each step of the development topic structure (e.g., Step 1: A magnetizing phrase that blends curiosity, emotion, and impact.).",
        "TOPIC_STRUCTURE_STEP6_DESCRIPTION": "Other Description for each step of the development topic structure (e.g., Step 1: A magnetizing phrase that blends curiosity, emotion, and impact.).",
        "SCRIPT_FORMAT_STEP_1_DESCRIPTION": "A short phrase describing a specific step in the narrative structure of the video script (e.g., Step 1: 'Poetic and mysterious opening', Step 5: 'Elevated, gentle, and hopeful conclusion').",
        "SCRIPT_FORMAT_STEP_2_DESCRIPTION": "Other short phrase describing a specific step in the narrative structure of the video script (e.g., Step 1: 'Poetic and mysterious opening', Step 5: 'Elevated, gentle, and hopeful conclusion').",
        "SCRIPT_FORMAT_STEP_3_DESCRIPTION": "Other short phrase describing a specific step in the narrative structure of the video script (e.g., Step 1: 'Poetic and mysterious opening', Step 5: 'Elevated, gentle, and hopeful conclusion').",
        "SCRIPT_FORMAT_STEP_4_DESCRIPTION": "Other short phrase describing a specific step in the narrative structure of the video script (e.g., Step 1: 'Poetic and mysterious opening', Step 5: 'Elevated, gentle, and hopeful conclusion').",
        "SCRIPT_FORMAT_STEP_5_DESCRIPTION": "Other short phrase describing a specific step in the narrative structure of the video script (e.g., Step 1: 'Poetic and mysterious opening', Step 5: 'Elevated, gentle, and hopeful conclusion').",
        "PREFERRED_CONTENT_ELEMENT_1": "Content element to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
        "PREFERRED_CONTENT_ELEMENT_2": "Other Content element to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
        "PREFERRED_CONTENT_ELEMENT_3": "Other Content element to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
        "PREFERRED_CONTENT_ELEMENT_4": "Other Content element to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
        "PREFERRED_CONTENT_ELEMENT_5": "Other Content element to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
        "PREFERRED_CONTENT_ELEMENT_6": "Other Content element to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
        "PREFERRED_CONTENT_ELEMENT_7": "Other Content element to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
        "TITLE_THEME_ADJECTIVES": "Adjectives for the theme title (e.g., profound, revealing, practical).",
        "ACTION_VERB": "Action verb for exercises or practices.",
        "ACTION_OR_PRACTICE": "Audiences action or practice.",
        "NUMBER_OF_THEMES_TO_GENERATE": "Number of main themes to be generated.",
    },
    {            
        "EFFECTIVE_TRIGGERS_LIST": "A list of specific psychological or spiritual triggers that are most effective for engaging this particular audience (e.g., - Emotional validation with a scriptural basis: 'God also saw your tear that morning.' - Connection between pain and purpose: 'The wound no one sees is the altar God uses.').",
        "KNOWLEDGE_BASE_RELATED_TRIGGERS": "Triggers related to the niches knowledge base (e.g., philosophical triggers, behavioral triggers).",
        "TRIGGER_EXAMPLE_1_DESCRIPTION": "Description of specific triggers.",
        "TRIGGER_EXAMPLE_2_DESCRIPTION": "Other Description of specific triggers.",
        "TRIGGER_EXAMPLE_3_DESCRIPTION": "Other Description of specific triggers.",
        "TRIGGER_EXAMPLE_4_DESCRIPTION": "Other Description of specific triggers.",
        "TRIGGER_EXAMPLE_5_NEUROSCIENCE_CONNECTION": "An example of a trigger with a neuroscientific connection, if applicable.",
        "FACTOR_TYPE": "Type of factor (e.g., emotional, mental, external).",
        "NEUROCHEMICAL_OR_STRESS_FACTOR": "Neurochemical or stress factor.",
        "NEUROCHEMICAL_EXAMPLE": "Example of a neurochemical.",
        "SITUATION_EXAMPLE": "Example of a situation where the neurochemical acts.",
        "PERSON_TYPE": "Type of person in the real story.",
    },
    {
        "AVOID_CLICHES_FROM_NICHE": "Common clichés in this specific niche (e.g., cheap self-help clichés, empty corporate jargon).",
        "CLICHE_PHRASE_EXAMPLE_1": "Example of cliché phrases to avoid in the niche.",
        "CLICHE_PHRASE_EXAMPLE_2": "Other Example of cliché phrases to avoid in the niche.",
        "CLICHE_PHRASE_EXAMPLE_3": "Other Example of cliché phrases to avoid in the niche.",
        "EMPTY_PHRASE_EXAMPLE_1": "Example of empty phrases to avoid.",
        "EMPTY_PHRASE_EXAMPLE_2": "Other Example of empty phrases to avoid.",
        "AVOID_TONE_1": "Tone to be completely avoided.",
        "AVOID_TONE_2": "Other Tone to be completely avoided.",
        "AVOID_TONE_3": "Other Tone to be completely avoided.",
        "AVOID_GENRE_1": "Content genre to avoid (e.g., superficial self-help).",
        "GENERIC_LIST_FORMAT_EXAMPLE": "Example of a generic list format to avoid (e.g., X steps to Y).",
        "WRONG_SOURCE_METAPHOR": "Metaphor for a wrong source.",
    }
]

def set_qty_variables(variables):
    variables['NUMBER_OF_DEV_TOPICS'] = 5
    variables['NUMBER_OF_SUBTOPICS_MIN'] = 3
    variables['NUMBER_OF_SUBTOPICS_MAX'] = 5
    
    return variables

def remove_variables_period(variables):
    return {
        key: value[:-1] if isinstance(value, str) and value.endswith('.') else value
        for key, value in variables.items()
    }

def all_variables_generated_properly(variables, variables_generated):
    generated_keys = []
    for key, value in variables_generated.items():
        if isinstance(value, list):
            return False
        generated_keys.append(key)
    for key in variables:
        if not key in variables_generated:
            return False

    return True 

def has_invalid_keys(variables):
    invalid_keys = []

    for key in variables:
        if "," in key:
            invalid_keys.append(key)

    return len(invalid_keys) > 0

def generate_variables(prompt_variables):
    default_prompt_path = 'default_prompts/script/set_variables.json'

    prompt = get_prompt(default_prompt_path, prompt_variables)
    prompt_json = json.loads(prompt)
    response = analyze_with_gemini(prompt_json=prompt_json)
    current_variables = format_json_response(response)
    
    if has_invalid_keys(current_variables) or not all_variables_generated_properly(prompt_variables['variables_dict'], current_variables):
        print(f"\t\t- Invalid. Generating again...")
        return generate_variables(prompt_variables)
    
    return current_variables

def set_variables(phase1_insights, phase2_insights, phase3_insights, channel):
    all_variables = {}

    prompt_variables = {
        "channel": sanitize.text(str(channel)),
        "phase1_insights": sanitize.text(phase1_insights),
        "phase2_insights": sanitize.text(phase2_insights),
        "phase3_insights": sanitize.text(phase3_insights),
    }
    
    for i, current in enumerate(VARIABLES):
        print(f"\t- {i+1}/{len(VARIABLES)}")
        variables_to_generate = sanitize.variables(current)
        prompt_variables['variables_dict'] = variables_to_generate
        prompt_variables['variables'] = sanitize.text(str(variables_to_generate))
        current_variables = generate_variables(prompt_variables)
        all_variables.update(current_variables)

    if all_variables:
        variables_without_period = remove_variables_period(all_variables) 
        return set_qty_variables(variables_without_period)
    
    return {}


def build(insights_p1, insights_p2, insights_p3, channel):    
    print(f"- Variables...")

    language = database.get_input_final_language()
    duration = database.get_input_video_duration()()

    variables = set_variables(insights_p1, insights_p2, insights_p3, channel)
    
    if not variables:
        return run(channel, insights_p1, insights_p2, insights_p3)

    variables['LANGUAGE_AND_REGION'] = language
    variables['VIDEO_DURATION'] = duration
    
    return variables

def run(channel, insights_p1, insights_p2, insights_p3):
    path = f"storage/thought/{channel['id']}/"

    variables = build(insights_p1, insights_p2, insights_p3, channel)
    database.export('variables', variables, format='json', path=path)

    return variables