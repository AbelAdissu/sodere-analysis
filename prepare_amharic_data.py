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



'''
The function translate_non_code_snippets_and_
stitch_back is designed to handle text that may contain embedded code snippets, 
ensuring that only the non-code portions of the text are translated.

'''

def translate_non_code_snippets_and_stitch_back(text, translate_client):

    '''
    text: The string that potentially contains both code and non-code segments.
    translate_client: An instance of a translation client, which is used to perform translations.
    
    '''

    error_suspicious = False
    if not ('```' in text or '`' in text):
        return do_cloud_translation(translate_client, text), len(text), error_suspicious

    '''
    The first if statement checks if the text contains specific delimiters for code (``` or `).
    If neither of these delimiters is found in the text, this suggests that the entire text is non-code. In this case, the function:
        Translates the entire text using do_cloud_translation.
        Returns the translated text, the length of the original text, and a flag (error_suspicious) set to False indicating no issues with code delimiters in the text.
            
    '''


    '''
    Triple Backticks (```): This delimiter is typically used to create blocks of code in Markdown and other text formats. It's used to start and end a block where the enclosed text is treated distinctly from the rest of the document
    Single Backtick (`): This delimiter is used for inline code in Markdown. It marks a shorter section of text, often just a word or a line
      
    '''


    delimiters = ['```', '`']  # Prefer longer delimiter
    delimiters.sort(key=len, reverse=True)  # Sorting delimiters by length in descending order

    translated_length = 0

    # first, split the text into code snippets and non-code snippets
    non_code_snippets = []
    code_snippets = []
    code_delimiters = []


    '''
    Prepare Delimiters:
        delimiters = ['```', '']`: This creates a list of strings representing code delimiters, which are used to identify blocks of code within the text.
        delimiters.sort(key=len, reverse=True): This sorts the delimiters by length in descending order. Sorting by length ensures that the function checks for longer delimiters first. This is important because if both types of delimiters are present, the longer one (```) typically denotes a multi-line code block which might contain the shorter one ( `) as part of the code.
    
    3. Initialize Variables for Splitting Text:
        translated_length = 0: Initializes a counter to keep track of the length of text that has been translated. This is useful for monitoring how much text has been processed and can be important for applications with limits on the amount of text that can be translated.
        non_code_snippets = []: Initializes a list to store segments of the text that do not contain code and need to be translated.
        code_snippets = []: Initializes a list to store segments of the text that are identified as code. These segments will not be translated to preserve the syntax and functionality of the code.
        code_delimiters = []: Initializes a list to store the delimiters that were used to identify each code snippet. This is necessary for later reconstructing the original text structure accurately after translation of non-code parts.
            
    '''



    while len(text) > 0:

        '''
        
        Initialize Search Variables:

            next_code_snippet_start: Initialized to the length of the remaining text, this variable will store the position where the next code snippet starts.
            next_delimiter: This will hold the delimiter that identifies the start of the next code snippet.
            Find the Next Code Snippet:

        The code searches for the next occurrence of any delimiter (``` or `` ).
        If a delimiter is found and it appears before any previously found snippet start (next_code_snippet_start), update next_code_snippet_start and next_delimiter to the new values.
                
        
        
        '''
        # find the next code snippet
        next_code_snippet_start = len(text)
        next_delimiter = None
        for delimiter in delimiters:
            temp_start = text.find(delimiter)
            if temp_start != -1 and temp_start < next_code_snippet_start:
                next_code_snippet_start = temp_start
                next_delimiter = delimiter

        if next_delimiter is None:
            # no more code snippets
            non_code_snippets.append(text)
            text = ''

        '''
        No Delimiter Found (next_delimiter is None):
            If no further delimiters are found, it means the rest of the text does not contain any code snippets.
            Append the entire remaining text to non_code_snippets and clear text to exit the loop.
                    
        '''
        else:
            # there is a code snippet
            non_code_snippets.append(text[:next_code_snippet_start])
            text = text[next_code_snippet_start + len(next_delimiter):]
            next_code_snippet_end = text.find(next_delimiter)
            if next_code_snippet_end == -1:
                # there is no closing code snippet, treat the rest as code
                code_snippets.append(text)
                code_delimiters.append(next_delimiter)
                text = ''
                error_suspicious = True
            else:
                code_snippets.append(text[:next_code_snippet_end])
                code_delimiters.append(next_delimiter)
                text = text[next_code_snippet_end + len(next_delimiter):]

            
        
            

    # now, translate the non-code snippets
    translated_non_code_snippets = []
    for non_code_snippet in non_code_snippets:
        translated_non_code_snippets.append(do_cloud_translation(translate_client, non_code_snippet))
        translated_length += len(non_code_snippet)

    # now, stitch the non-code snippets and code snippets back together
    translated_text = ''
    for i, non_code_snippet in enumerate(translated_non_code_snippets):
        translated_text += non_code_snippet
        if i < len(code_snippets):
            translated_text += code_delimiters[i] + code_snippets[i] + code_delimiters[i]

    return translated_text, translated_length, error_suspicious

def translate_parquet_file(parquet_file_path, output_destination, checkpoint_format_path, checkpoint_frequency=500):

    '''
    Parameters:
        parquet_file_path: The file path to the input Parquet file containing data to be translated.
        output_destination: The file path where the translated JSON data will be saved.
        checkpoint_format_path: A string pattern to define file paths for saving periodic checkpoints of the translation progress.
        checkpoint_frequency: Frequency of saving checkpoints in terms of number of rows processed.
            
    '''


    outputs = []
    translate_client = translate.Client()

    characters_translated = 0
    i = 0
    data = pd.read_parquet(parquet_file_path, engine='pyarrow')

    '''
    outputs = [] : This list is intended to store the results of the translation process 
    characters_translated : This counter will track the number of characters that have been translated during the operation.
    i = 0 :- This is typically used to keep track of the number of iterations, rows processed
    data = pd.read_parquet(parquet_file_path, engine='pyarrow') : Uses the pandas library’s read_parquet function to load data from a Parquet file specified by parquet_file_path.

    '''
    

    for index, row in data.iterrows():

        # issue happened during translation at 45k, start at 45k
        # if i <= 45000:
        #    i += 1
        #    continue
        #abf = input(row)

        assert characters_translated < 37000000

        prompt = row['prompt']
        chosen = row['chosen']

        # prompt begins with Human: and ends with Assistant: 
        if prompt.startswith('Human: '):
            prompt = prompt[7:]
        if prompt.endswith(' Assistant:'):
            prompt = prompt[:-11]


        '''
        for index, row in data.iterrows(): iterates through each row in the DataFrame data, which contains the content of the Parquet file loaded earlier. 
        index is the row index, and row contains the data in each row.
        assert characters_translated < 37000000: assert characters_translated < 37000000 ensures the total count of translated characters does not exceed 37 million, likely a limitation or quota of the translation API being used.
        prompt = row['prompt']: Retrieves the 'prompt' value from the current row of the DataFrame.
        chosen = row['chosen']: Similarly retrieves the 'chosen' value, which could represent a selected response 
        '''

        '''
        if prompt.startswith('Human: '):: Checks if the prompt string begins with the substring "Human: ". This is often used to indicate that the text following is spoken or written by a human in a conversational dataset.
            prompt = prompt[7:]: If the condition is true, it removes the first seven characters ("Human: ") from the prompt. This is done by slicing the string from the 7th character to the end, effectively removing the "Human: " part. The number 7 corresponds to the length of "Human: ".
        if prompt.endswith(' Assistant:'):: Checks if the prompt string ends with " Assistant:". This might be used to signify that the following text is expected to be a response from an assistant in a dialog dataset.
            prompt = prompt[:-11]: If true, it removes the last eleven characters (" Assistant:") from the prompt. This is achieved by slicing the string up to the 11th character from the end, excluding " Assistant:". The number 11 is derived from the length of " Assistant:".
            
        '''


        translated_json = {}
        translated_json['prompt'], c_t_prompt, err_p = translate_non_code_snippets_and_stitch_back(prompt, translate_client)
        translated_json['chosen'], c_t_chosen, err_c = translate_non_code_snippets_and_stitch_back(chosen, translate_client)
        translated_json['reference_index'] = index
        translated_json['error_suspicion'] = err_p or err_c

        characters_translated += c_t_prompt
        characters_translated += c_t_chosen

        outputs.append(translated_json)

        '''
        translated_json = {}: Creates an empty dictionary to store results related to the current row of data being processed. 
        translated_json['prompt'], c_t_prompt, err_p = translate_non_code_snippets_and_stitch_back(prompt, translate_client): This line calls the translate_non_code_snippets_and_stitch_back function with the prompt text and the translation client. The function is expected to return the translated text, the number of characters translated (c_t_prompt), and a flag indicating if there was any suspicious issue (err_p) during translation.
        translated_json['chosen'], c_t_chosen, err_c = translate_non_code_snippets_and_stitch_back(chosen, translate_client): Similar to the previous call but for the chosen text. It also returns the translated text, count of translated characters, and an error flag.
                
        
        '''

        scratch_file_path = 'scratch.txt'
        with open(scratch_file_path, 'w', encoding='utf-8') as f:
            f.write("Initial {}\n New {}".format({'prompt': row['prompt'], 'chosen': row['chosen']}, translated_json))
        #abf = input('set {}'.format(characters_translated))
        print('Translated {} lines and {} chars so far'.format(i, characters_translated))
        time.sleep(1)

        if i % checkpoint_frequency == 0:
            print("Checkpoint: {}".format(i))
            print('Characters translated: {}'.format(characters_translated))
            checkpoint_path = checkpoint_format_path.format(i)
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(outputs, f, ensure_ascii=False, indent=4)
        
        i += 1

    with open(output_destination, 'w', encoding='utf-8') as f:
        # dump output list into one json 
        json.dump(outputs, f, ensure_ascii=False, indent=4)

alpaca_src = ''
alpaca_dest = ''
alpaca_checkpoint = ''

dolly_src = ''
dolly_dest = ''
dolly_checkpoint = ''

translate_parquet_file(alpaca_src, alpaca_dest, alpaca_checkpoint)
translate_dolly_15k_jsonl(dolly_src, dolly_dest, dolly_checkpoint)


