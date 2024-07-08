import json 
import csv
import random 
import pandas as pd
import prompts 


def load_parquet_to_json_list(parquet_file_path):
    data = pd.read_parquet(parquet_file_path, engine='pyarrow')

    json_list = []

    for index, row in data.iterrows():
        jso = json.loads(row.to_json())
        jso['index'] = index
        json_list.append(jso)
    
    return json_list

'''
The function load_parquet_to_json_list is designed to load data from a Parquet file and 
convert it into a list of JSON objects. 

'''

def load_jsonl_to_json_list(jsonl_file_path):
    json_list = []

    with open(jsonl_file_path) as f:
        for line in f:
            json_list.append(json.loads(line))
    
    return json_list

'''
The function load_jsonl_to_json_list is designed to read data from a JSON Lines (JSONL) file and 
convert each line into a JSON object, which it collects into a list. 

'''

def get_prompt_no_context(language='Amharic'):
    return random.choice(prompts.PREFIX_LIST_NO_CONTEXT).format(language)

def get_prompt_with_context(language='Amharic'):
    return random.choice(prompts.PREFIX_LIST_CONTEXT).format(language)

def get_prompt_translation(src_lang, targ_lang):
    return random.choice(prompts.PREFIX_LIST_TRANSLATION).format(src_lang, targ_lang)

def get_prompt_headline_from_article():
    return random.choice(prompts.PREFIX_LIST_HEADLINE)

def get_prompt_article_from_headline():
    return random.choice(prompts.PREFIX_LIST_STORY_FROM_HEADLINE)

def get_prompt_summary_from_article():
    return random.choice(prompts.PREFIX_LIST_SUMMARY)

def get_prompt_article_from_summary():
    return random.choice(prompts.PREFIX_LIST_STORY_FROM_SUMMARY)

def join_alpaca_english_amharic(english_list, amharic_list, with_translation=True, allow_english=True, with_amharic=False):

    new_list = []
    for idx, item in enumerate(english_list):

        prompt_format = get_prompt_no_context() + "\nHuman: {}\nAssistant{}: "

        prompt_format_translation_eng_am = get_prompt_translation('English', 'Amharic') + "\nEnglish: {}\nAmharic: "
        prompt_format_translation_am_eng = get_prompt_translation('Amharic', 'English') + "\nAmharic: {}\nEnglish: "

        english_prompt = item['prompt']
        if english_prompt.startswith('Human: '):
            english_prompt = english_prompt[7:]
        if english_prompt.endswith(' Assistant:'):
            english_prompt = english_prompt[:-11]

        amharic_prompt = amharic_list[idx]['prompt']

        english_response = item['chosen']
        amharic_response = amharic_list[idx]['chosen']

        if allow_english:

            # append the english to amharic
            new_list.append({'input': prompt_format.format(english_prompt, ' [Amharic] '), 'output': amharic_response})

            # append the amharic to english
            new_list.append({'input': prompt_format.format(amharic_prompt, ' [English] '), 'output': english_response})

        if with_amharic:

            # append the amharic to amharic
            new_list.append({'input': prompt_format.format(amharic_prompt, ' [Amharic] '), 'output': amharic_response})

        if with_translation:

            # append translation variant for prompt, english to amharic
            new_list.append({'input': prompt_format_translation_eng_am.format(english_prompt), 'output': amharic_prompt})

            # append translation variant for prompt, amharic to english
            new_list.append({'input': prompt_format_translation_am_eng.format(amharic_prompt), 'output': english_prompt})

            # append translation variant for response, english to amharic
            new_list.append({'input': prompt_format_translation_eng_am.format(english_response), 'output': amharic_response})

            # append translation variant for response, amharic to english
            new_list.append({'input': prompt_format_translation_am_eng.format(amharic_response), 'output': english_response})
        

    return new_list

def join_dolly_english_amharic(english_list, amharic_list, with_translation=True, allow_english=True, with_amharic=False):


    new_list = []
    for idx, item in enumerate(english_list):
        
        prompt_format_no_context = get_prompt_no_context() + "\nHuman: {}\nAssistant{}: "

        prompt_format_context = get_prompt_with_context() + "\nContext: {}\nHuman: {}\nAssistant{}: "


        prompt_format_translation_eng_am = get_prompt_translation('English', 'Amharic') + "\nEnglish: {}\nAmharic: "
        prompt_format_translation_am_eng = get_prompt_translation('Amharic', 'English') + "\nAmharic: {}\nEnglish: "


        enlglish_prompt = item['instruction']
        amharic_prompt = amharic_list[idx]['instruction']

        english_response = item['response']
        amharic_response = amharic_list[idx]['response']

        context = item['context']
        amharic_context = amharic_list[idx]['context']

        if len(context) > 0:
            if allow_english:
                new_list.append({'input': prompt_format_context.format(context, enlglish_prompt, ' [Amharic] '), 'output': amharic_response})
                new_list.append({'input': prompt_format_context.format(context, amharic_prompt, ' [English] '), 'output': english_response})
                new_list.append({'input': prompt_format_context.format(context, amharic_prompt, ' [Amharic] '), 'output': amharic_response})
                new_list.append({'input': prompt_format_context.format(amharic_context, enlglish_prompt, ' [Amharic] '), 'output': amharic_response})
                new_list.append({'input': prompt_format_context.format(amharic_context, amharic_prompt, ' [English] '), 'output': english_response})

            if with_amharic:
                new_list.append({'input': prompt_format_context.format(amharic_context, amharic_prompt, ' [Amharic] '), 'output': amharic_response})

            if with_translation:

                # translation english to amharic context
                new_list.append({'input': prompt_format_translation_eng_am.format(context), 'output': amharic_context})
                # translation amharic to english context
                new_list.append({'input': prompt_format_translation_am_eng.format(amharic_context), 'output': context})
        else:
            if allow_english:
                new_list.append({'input': prompt_format_no_context.format(enlglish_prompt, ' [Amharic] '), 'output': amharic_response})
                new_list.append({'input': prompt_format_no_context.format(amharic_prompt, ' [English] '), 'output': english_response})


            if with_amharic:
                new_list.append({'input': prompt_format_no_context.format(amharic_prompt, ' [Amharic] '), 'output': amharic_response})

        if with_translation:

            # append translation variant for prompt, english to amharic
            new_list.append({'input': prompt_format_translation_eng_am.format(enlglish_prompt), 'output': amharic_prompt})

            # append translation variant for prompt, amharic to english
            new_list.append({'input': prompt_format_translation_am_eng.format(amharic_prompt), 'output': enlglish_prompt})

            # append translation variant for response, english to amharic
            new_list.append({'input': prompt_format_translation_eng_am.format(english_response), 'output': amharic_response})

            # append translation variant for response, amharic to english
            new_list.append({'input': prompt_format_translation_am_eng.format(amharic_response), 'output': english_response})
        #abf = input(new_list)

    return new_list

