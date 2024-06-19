import pandas as pd
import json 
import os
import time 

from google.cloud import translate_v2 as translate


def do_cloud_translation(translate_client, text):
    
    if len(text) == 0:
        return text

    result = translate_client.translate(text, target_language="am")
    translated_text = result['translatedText']
    return translated_text

'''

The provided function do_cloud_translation is designed to translate text from English (or any other language, implicitly) to Amharic using Google Cloud's Translation API. Here's how it works:

Input Parameters:

    translate_client: This is an instance of the Google Cloud Translate client, which facilitates communication with Google's translation services.
    text: The string of text that needs to be translated.
    
Process:

    First, the function checks if the input text is empty. If it is, the function returns the empty string immediately, avoiding unnecessary API calls.
    If there is text to translate, the function calls the translate method of the translate_client, specifying "am" as the target_language to indicate that the text should be translated into Amharic.
    The result of the translation is stored in the result variable, which is expected to be a dictionary containing at least the key 'translatedText'.

Output:
    The function retrieves the translated text from the result dictionary using the key 'translatedText' and returns this translated text.


'''




'''
The function 'translate_dolly_15k_jsonl' is designed to translate the contents of a JSON Lines (JSONL) file from
English to Amharic, leveraging Google Cloud's Translation API. 

'''
def translate_dolly_15k_jsonl(input_file, output_destination, checkpoint_format_path, checkpoint_frequency=500):
    
    '''
    Parameters:
        input_file: Path to the JSONL file containing the data to be translated.
        output_destination: Path where the translated JSONL file will be saved.
        checkpoint_format_path: String format to define the paths for saving intermediate results, or checkpoints.
        checkpoint_frequency: Determines how often (in terms of lines processed) to save a checkpoint. Default is every 500 lines.

    '''
    
    translate_client = translate.Client()

    characters_translated = 0

    outputs = []

    '''
    Initialization:

        Initializes a translation client from Google Cloud.
        Sets a counter for characters translated to ensure it stays below a limit of 14 million (likely to comply with API usage constraints).
        Prepares an empty list outputs to collect translated data
             
    '''

    json_keys = ['category', 'instruction', 'response', 'context']
    translate_keys = {'instruction', 'response', 'context'}

    '''
    - It defines which JSON keys (category, instruction, response, context) are subject to translation. Translation is applied to instruction, response, and context.
    - Extracts the text from these keys, translates it, and updates the count of characters translated.
    - Non-translatable keys (category in this case) are copied directly to the output JSON object.
    - Tracks the original 'response' in the translated JSON for reference. 
    '''





    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            assert characters_translated < 14000000
            
            '''
            File Handling: Opens the input_file specified in the function parameters for reading.
            Loop Over Lines: Iterates over each line in the file, treating each line as a separate JSON object.
            Ensures that the total number of characters translated does not exceed 14 million. If this limit is exceeded, an assertion error is triggered.

            '''

            json_line = json.loads(line)
            translated_json = {}
            for key in json_keys:
                if key in translate_keys:
                    text = json_line[key]
                    translated_text = do_cloud_translation(translate_client, text)
                    characters_translated += len(text)
                    translated_json[key] = translated_text
                else:
                    translated_json[key] = json_line[key]

            '''
            JSON Parsing: Converts each line from JSON format to a Python dictionary (json_line).
            Translation: Iterates over the keys in the json_line. If a key is marked for translation (translate_keys includes 'instruction', 'response', 'context'), the corresponding text is translated, and the count of translated characters is updated.
            Output JSON Construction: Builds a new dictionary (translated_json) where translated texts are stored under their respective keys. Non-translatable keys are copied directly.
            Output JSON Construction: Builds a new dictionary (translated_json) where translated texts are stored under their respective keys. Non-translatable keys are copied directly.
            '''

            translated_json['reference_response'] = json_line['response']
            
            scratch_file_path = 'scratch.txt'
            with open(scratch_file_path, 'w', encoding='utf-8') as f:
                f.write("Initial {}\n New {}".format(json_line, translated_json))
            #abf = input('set {}'.format(characters_translated))
            print('Translated {} lines and {} chars so far'.format(i, characters_translated))
            time.sleep(2.5)
            outputs.append(translated_json)

            '''
            Debug File Writing: Writes the original and newly translated JSON objects to a scratch file ('scratch.txt') for debugging or tracking purposes.
            Progress Logging: Outputs the progress to the console, indicating the number of lines processed and the total characters translated so far.
            Sleep: Introduces a pause of 2.5 seconds between processing each line, which could be used to manage the rate of API requests or simply for debugging.
                    
            '''

            if i % checkpoint_frequency == 0:
                print("Checkpoint: {}".format(i))
                print('Characters translated: {}'.format(characters_translated))
                checkpoint_path = checkpoint_format_path.format(i)
                with open(checkpoint_path, 'w', encoding='utf-8') as f:
                    json.dump(outputs, f, ensure_ascii=False, indent=4)


            '''
            if i % checkpoint_frequency == 0: This condition checks if the current line number i is a multiple of the specified checkpoint_frequency. For example, if checkpoint_frequency is set to 500, this block executes every 500 lines.
            print("Checkpoint: {}".format(i)): Logs the current line number to the console, marking it as a checkpoint
            print('Characters translated: {}'.format(characters_translated)): Outputs the total number of characters that have been translated up to this point.
            checkpoint_path = checkpoint_format_path.format(i): Determines the file path for the checkpoint file by formatting a string with the current line number i
            
            '''

    with open(output_destination, 'w', encoding='utf-8') as f:
        # dump output list into one json 
        json.dump(outputs, f, ensure_ascii=False, indent=4)

    '''
    Storing data in the output_destination 
    outputs is expected to be a list of dictionaries, where each dictionary represents a JSON object with the translated text

    '''
