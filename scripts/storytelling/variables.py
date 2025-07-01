from scripts.utils import get_gemini_model, analyze_with_gemini, format_json_response, get_prompt

VARIABLES = f'''
    [{{    
    "NICHE_DESCRIPTION": "Description of the channels niche (e.g., Personal Development based on Stoic Philosophy, Mindfulness for Busy Moms).",
    "NICHE_CORE_CONCEPTS": "The main theories or ideas of the niche (e.g., quantum manifestation, spiritual neuroscience, Law of Attraction, mental reprogramming).",
    "NICHE_KEY_METRIC": "A key concept or metric in the niche (e.g., vibration, frequency, mindset).",
    "NICHE_PRACTICE_EXAMPLES": "Specific rituals, disciplines, or practices that are common and significant for the target audience (e.g., praying, climbing mountains, fasting; or journaling, meditating daily, scripting affirmations).",
    "NICHE_REVERENCE_WORDS_EXAMPLES": "Examples of specific words or short phrases that the audience uses to express reverence, gratitude, or connection, indicating their cultural or spiritual dialect (e.g., 'gratitude', 'Danke', 'hallelujah'; or 'amor fati', 'memento mori', 'namaste').",
    "NICHE_JARGON_CATEGORY_1", "NICHE_JARGON_CATEGORY_2": "Categories of specialized terms or jargon from the niche that should be explained emotionally rather than used technically (e.g., Category 1: 'theological terms', Category 2: 'scientific terms'; or Category 1: 'metaphysical concepts', Category 2: 'psychological terms').",
    "NICHE_POWER_WORDS_LIST": "A list of keywords and concepts that have a strong emotional and spiritual resonance with the target audience (e.g., Consecration, Calling, Divine Silence, Inner Healing, Sacred Loneliness, Altar, Hidden Testimony).",
    "ENERGY_BLOCK_EXAMPLE_1, ENERGY_BLOCK_EXAMPLE_2": Niche-specific examples of blockages (e.g., energetic leak, unconscious block).",
    "ANALYTICAL_LENSES": "The perspectives used for analysis (e.g., philosophical, neuroscientific, emotional, and symbolic).",
    "CORE_AUDIENCE_PAIN_OR_GOAL": "The primary pain, challenge, or goal of the target audience (e.g., overcoming anxiety, finding professional purpose, coping with grief).",
    "SUB_THEMES_EXAMPLES": "List of sub-themes relevant to the niche (e.g., fear of failure, procrastination, search for meaning, breathing techniques, guided meditation, daily mindfulness).",
    "KNOWLEDGE_BASE_MAIN": "The primary source of knowledge or authority in the niche (e.g., Stoic Philosophy, Principles of Positive Psychology, Buddhist Sacred Texts).",
    "GUIDANCE_TYPE": "The type of guidance offered (e.g., mental, emotional, practical, philosophical).",
    "AVOID_CLICHES_FROM_NICHE": "Common clichés in this specific niche (e.g., cheap self-help clichés, empty corporate jargon).",
    "HIDDEN_ISSUES_EXAMPLES": "Examples of hidden problems the content seeks to reveal (e.g., unconscious limiting beliefs, self-sabotage patterns, unmet emotional needs).",
    "EMOTIONAL_WOUND_TYPE": "Type of emotional wound the theme might address (e.g., rejection wound, fear of abandonment, low self-esteem).",
    "DEITY_OR_CONCEPT": "The central higher power, universal principle, or core concept that the audience connects with or seeks guidance from (e.g., God, the Universe, the Logos, Source, Higher Self, the Divine Mind).",
    "TARGET_AUDIENCE_DEMOGRAPHICS_AND_PSYCHOGRAPHICS_DETAILED": "A detailed paragraph describing the target audience, including their demographics (age, life situation) and psychographics (inner world, beliefs, feelings, spiritual profile).",
    "DETAILED_AUDIENCE_PAINS_LIST": "A comprehensive, bulleted list detailing the specific, nuanced emotional and spiritual pains of the target audience. This is used to give the AI deep context (e.g., - Feeling invisible even while praying intensely. - Carrying the weight of unspoken emotional abandonment.).",
    "DETAILED_AUDIENCE_DESIRES_LIST": "A comprehensive, bulleted list detailing the implicit, deep desires of the target audience (e.g., - To feel heard by God in a clear and intimate way. - To have their waiting and suffering validated.).",
    "EFFECTIVE_TRIGGERS_LIST": "A list of specific psychological or spiritual triggers that are most effective for engaging this particular audience (e.g., - Emotional validation with a scriptural basis: 'God also saw your tear that morning.' - Connection between pain and purpose: 'The wound no one sees is the altar God uses.').",
    "AUDIENCE_DESIRES": The primary things the audience is looking for (e.g., balance, reconnection, purpose).",
    "CORE_AUDIENCE_PAIN_EXAMPLES": "Specific, concrete examples of the audience's pain points that the content will directly address (e.g., loneliness, abandonment, unanswered prayers; or professional burnout, fear of the future, lack of purpose).",
    "TARGET_AUDIENCE_WANTS": "What the audience values instead of clichés (e.g., deep clarity, applicable guidance, and transformative narratives).",
    "UNANSWERED_QUESTION_OR_DESIRE": "The audiences deep question or desire (e.g., search for acceptance, need for belonging, longing for inner peace).",
    "IDENTITY_WOUND_EXAMPLE, FAITH_VOID_EXAMPLE, EMOTIONAL_BLOCK_EXAMPLE": "Examples of niche-specific wounds or blocks.",
    "KNOWLEDGE_BASE_RELATED_TRIGGERS": "Triggers related to the niches knowledge base (e.g., philosophical triggers, behavioral triggers).",
    "TRIGGER_EXAMPLE_1_DESCRIPTION, TRIGGER_EXAMPLE_2_DESCRIPTION, TRIGGER_EXAMPLE_3_DESCRIPTION, TRIGGER_EXAMPLE_4_DESCRIPTION": "Descriptions of specific triggers.",
    "TRIGGER_EXAMPLE_5_NEUROSCIENCE_CONNECTION": "An example of a trigger with a neuroscientific connection, if applicable.",
    "CLICHE_PHRASE_EXAMPLE_1, CLICHE_PHRASE_EXAMPLE_2, CLICHE_PHRASE_EXAMPLE_3": "Examples of cliché phrases to avoid in the niche.",
    "APPROVED_PHRASES_EXAMPLES": "A list of specific, niche-aligned key phrases and affirmations that resonate deeply with the audience and can be used in the script (e.g., 'What the world calls loneliness, heaven calls preparation.', 'You were separated, not rejected.').",
    "PREFERRED_CONTENT_ELEMENT_1, PREFERRED_CONTENT_ELEMENT_2, PREFERRED_CONTENT_ELEMENT_3, PREFERRED_CONTENT_ELEMENT_4, PREFERRED_CONTENT_ELEMENT_5, PREFERRED_CONTENT_ELEMENT_6, PREFERRED_CONTENT_ELEMENT_7": "Content elements to prioritize (e.g., inspiring metaphors, case studies, practical exercises).",
    "LANGUAGE_STYLE_ADJECTIVES, LANGUAGE_STYLE_ADJECTIVES_2": "Adjectives describing the language style (e.g., clear, concise, empathetic, formal, academic, provocative).",
    "STYLE_INGREDIENT_1, STYLE_INGREDIENT_2, STYLE_INGREDIENT_3, STYLE_INGREDIENT_4, STYLE_INGREDIENT_5": "Components that form the channels unique style.",
    "STYLE_REFERENCE_LIST": "A simple, comma-separated list of key authors, thinkers, or figures who serve as the primary style and content inspiration (e.g., Charles Stanley, David Wilkerson, A. W. Tozer; or Seneca, Epictetus, Marcus Aurelius).",
    "STYLE_REFERENCE_LIST_DETAILED": "A more detailed list of inspirational figures, where each name is followed by a brief parenthetical description of their specific contribution or style (e.g., Charles Stanley (pastoral and welcoming teaching), David Wilkerson (prophetic and broken messages), A. W. Tozer (intimacy with God)).",
    "TONE_VERB_1, TONE_VERB_2, TONE_VERB_3": "Verbs describing the desired tone.",
    "AVOID_TONE_1, AVOID_TONE_2, AVOID_TONE_3": "Tones to be completely avoided.",
    "TONE_DESCRIPTION_DETAILED": "A detailed description of the script's tone, outlining its intended effect on the viewer and its underlying philosophy (e.g., Therapeutic and clarifying. It guides the viewer to awareness without guilt.).",
    "TITLE_THEME_ADJECTIVES": "Adjectives for the theme title (e.g., profound, revealing, practical).",
    "PAIN_KEYWORD": "Keyword representing the pain/problem.",
    "REVELATION_KEYWORD": "Keyword representing the solution/revelation.",
    "KNOWLEDGE_BASE_RELATED_WOUND_TYPE": "Type of wound related to the knowledge base (e.g., philosophical wound, cognitive dissonance).",
    "COMMON_DISTORTION_SUBJECTS": "Subjects about which there are common distortions in the niche (e.g., success, happiness, relationships, productivity, discipline).",
    "TOPIC_STRUCTURE_STEP1_DESCRIPTION, TOPIC_STRUCTURE_STEP2_DESCRIPTION, TOPIC_STRUCTURE_STEP3_DESCRIPTION, TOPIC_STRUCTURE_STEP4_DESCRIPTION, TOPIC_STRUCTURE_STEP5_DESCRIPTION, TOPIC_STRUCTURE_STEP6_DESCRIPTION": "Descriptions for each step of the development topic structure (e.g., Step 1: A magnetizing phrase that blends curiosity, emotion, and impact.).",
    "EMOTIONAL_OR_COGNITIVE_ERROR_TYPE": "Type of error (e.g., cognitive bias, emotional trap).",
    "POSITIVE_TRAIT": "Positive trait that the error mimics.",
    "NEGATIVE_BEHAVIOR": "Negative behavior that the error hides.",
    "ACTION_VERB": "Action verb for exercises or practices.",
    "COMMON_MISUNDERSTANDING_IN_NICHE": "A common misunderstanding within the niche.",
    "FACTOR_TYPE": "Type of factor (e.g., emotional, mental, external).",
    "DESIRED_SKILL_OR_CONNECTION": "Skill or connection the audience desires (e.g., intuition, connection with purpose).",
    "GOAL_TO_DISCERN": "What is sought to be discerned/understood.",
    "NEUROCHEMICAL_OR_STRESS_FACTOR": "Neurochemical or stress factor.",
    "DESIRED_STATE_OR_ACTION": "Desired state or action by the audience.",
    "HISTORICAL_OR_ARCHETYPAL_FIGURE": "Relevant historical or archetypal figure.",
    "RELEVANT_LESSON": "Relevant lesson drawn from the figure.",
    "SOURCE_TEXT_OR_MODEL_EXAMPLE": "Example of a source text or model.",
    "NEUROCHEMICAL_EXAMPLE": "Example of a neurochemical.",
    "SITUATION_EXAMPLE": "Example of a situation where the neurochemical acts.",
    "PERSON_TYPE": "Type of person in the real story.",
    "NEGATIVE_OUTCOME_OR_BLOCK": "Negative outcome or block.",
    "WOUNDED_ASPECT": "Wounded aspect of the person.",
    "IDEALIZED_FIGURE_IN_NICHE": "Idealized figure in the niche.",
    "DESIRED_THING": "Thing desired by the audience.",
    "WRONG_SOURCE_METAPHOR": "Metaphor for a wrong source.",
    "ACTION_OR_PRACTICE": "Audiences action or practice.",
    "UNADDRESSED_ISSUES": "Unresolved issues.",
    "STYLE_REFERENCE_PERSON_1, STYLE_REFERENCE_PERSON_2, STYLE_REFERENCE_PERSON_3": People who are style references.",
    "STYLE_REFERENCE_PERSON_1_FOCUS, STYLE_REFERENCE_PERSON_2_FOCUS, STYLE_REFERENCE_PERSON_3_FOCUS": The focus/specialty of this reference person.",
    "STYLE_BLEND_COMPONENTS": "The core concepts or fields that are blended together to create the channel's unique perspective (e.g., practical spirituality and emotional neuroscience; or Stoic philosophy and modern psychology).",
    "SECONDARY_REFERENCE_EXAMPLE_1", "SECONDARY_REFERENCE_EXAMPLE_2": "Thinkers or sources from outside the primary niche whose ideas can be subtly incorporated, as long as they are connected back to the core message (e.g., Example 1: 'Gregg Braden', Example 2: 'Joe Dispenza'; or Example 1: 'Carl Jung', Example 2: 'Jordan Peterson').",
    "TARGET_AUDIENCE_MEMBERS_REAL_CASES": "Type of audience members whose cases can be used.",
    "SCIENTIFIC_FIELD_1, SCIENTIFIC_FIELD_2, SCIENTIFIC_FIELD_3_NEURO": "Scientific fields to be referenced.",
    "TARGET_AUDIENCE_SPECIFIC_FOCUS_IF_APPLICABLE": "Specific focus within a scientific field for the audience.",
    "COMMUNITY_RELATED_TO_NICHE": "Community or culture related to the niche.",
    "SPECIFIC_FOCUS_WITHIN_KNOWLEDGE_BASE": "A specific focus within the main knowledge base.",
    "EMPTY_PHRASE_EXAMPLE_1, EMPTY_PHRASE_EXAMPLE_2": "Examples of empty phrases to avoid.",
    "AVOID_GENRE_1": "Content genre to avoid (e.g., superficial self-help).",
    "SCRIPT_FORMAT_STEP_1_DESCRIPTION" ... "SCRIPT_FORMAT_STEP_5_DESCRIPTION": "A short phrase describing a specific step in the narrative structure of the video script (e.g., Step 1: 'Poetic and mysterious opening', Step 5: 'Elevated, gentle, and hopeful conclusion').",
    "GENERIC_LIST_FORMAT_EXAMPLE": "Example of a generic list format to avoid (e.g., X steps to Y).",
    "TARGET_AUDIENCE_DEMOGRAPHICS_AND_PSYCHOGRAPHICS": "Detailed description of the target audience.",
    "AUDIENCE_DESIRE_1, AUDIENCE_DESIRE_2, AUDIENCE_DESIRE_3, AUDIENCE_DESIRE_4": "The audiences main desires.",
    "NUMBER_OF_THEMES_TO_GENERATE": "Number of main themes to be generated.",
    "HIDDEN_ISSUES_EXAMPLES_SINGULAR_FORM": "Singular form of the hidden issue examples.",
    "AUDIENCE_EXPERIENCES_WITH_THE_THEME": "Bad experiences that the audience has had with the theme and for which they are looking for answers.",
    "DESIRED_OUTCOME_FOR_AUDIENCE": "Desired outcome for the audience (e.g., healing, growth, clarity).",
    "CORE_TEXTS_OR_PRINCIPLES_OF_NICHE": "Core texts or principles of the niche.",
    }}]
    '''

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

def get_variables(phase1_insights, phase2_insights, phase3_insights, channel):
    prompt_variables = {
        "channel": channel,
        "phase1_insights": phase1_insights,
        "phase2_insights": phase2_insights,
        "phase3_insights": phase3_insights,
        "variables": VARIABLES
    }

    prompt = get_prompt('scripts/storytelling/prompts/get_variables.txt', prompt_variables)
    
    response = analyze_with_gemini(prompt)

    variables = format_json_response(response) 
    if variables:
        variables_without_period = remove_variables_period(variables) 
        return set_qty_variables(variables_without_period)
    
    return {}
