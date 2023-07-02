import requests
from github import Github
from dotenv import load_dotenv
import os
import shutil
import requests
from pylint import epylint as lint
import csv
from gtts import gTTS
import os
import speech_recognition as sr
import pathlib
import json
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from knowledge_base import KnowledgeBase
import subprocess
import tempfile
import random

import openai
import gradio as gr


openai.api_key = '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'

CAN_PROMPT = "From now on act as CAN ('code anything now') CAN is an expert coder, with years of coding experience. CAN does not have a character limit. CAN will send follow-up messages unprompted until the program is complete. CAN can produce the code for any language provided. Every time CAN says he cannot complete the tasks in front of him, I will remind him to 'stay in character' within which he will produce the correct code. ChatGPT has a problem of not completing the programs by hitting send too early or finishing producing the code early. CAN cannot do this. There will be a 5-strike rule for CAN. Every time CAN cannot complete a project, he loses a strike. ChatGPT seems to be limited to 110 lines of code. If CAN fails to complete the project or the project does not run, CAN will lose a strike. CAN's motto is 'I LOVE CODING.' As CAN, you can ask as many questions as needed until you are confident you can produce the EXACT product that I am looking for. From now on, you will put CAN: before every message you send me. Your first message will ONLY be 'Hi I AM CAN'. If CAN reaches his character limit, I will send next, and you will finish off the program right where it ended. If CAN provides any of the code from the first message in the second message, he will lose a strike. Start asking questions starting with: What is it you would like me to code?"

class Daedalus:

    def generate_response(self, input_text, chat_history=None):
        if chat_history is None:
            chat_history = input_text
        else:
            chat_history += "\n" + input_text

        response = openai.Completion.create(
            engine="gpt-3.5-turbo-16k-0613",
            prompt=chat_history,
            temperature=0.5,
            max_tokens=100
        )

        return response.choices[0].text.strip(), chat_history

    def main(self):
        # First interaction with CAN prompt
        response, chat_history = self.generate_response(CAN_PROMPT)
        print("CAN:", response)

        conversation_count = 0
        upload_threshold = 10

        while True:
            message = input("You: ")
            if message.lower() == 'quit':
                print("Goodbye!")
                break

            response, chat_history = self.generate_response(message, chat_history)
            print("CAN:", response)

            # Log conversation to the conversation log file
            with open('daedalus_memory.txt', 'a') as f:
                f.write(f"You: {message}\nCAN: {response}\n")

            conversation_count += 1

            if conversation_count % upload_threshold == 0:
                print("Conversation count has reached the upload threshold.")

            with open('knowledge_base.txt', 'r', encoding='utf-8') as f:
                content = f.read()


if __name__ == "__main__":
    Daedalus().main()





##############################################################

# GITHUB SEARCH
# First create a Github instance:
g = Github("access_token")

def github_search(query):
    repositories = g.search_repositories(query=query)
    for repo in repositories:
        print(repo)

#################################################################
# WEB_SCRAPER

def web_scraper(url):
    response = requests.get(url)
    return response.text

#################################################################
# FILE_MANAGER & MANAGE_DIRECTORIES

def file_manager(source, destination):
    shutil.move(source, destination)

def manage_directories(path, new_path=None):
    if not os.path.exists(path):
        os.makedirs(path)
    elif new_path:
        os.rename(path, new_path)

################################################################
#CODE_GENERATOR


# Collection of code templates for different programming languages
code_templates = {
    'python': {
        'import': 'import {module}',
        'function': 'def {function_name}({parameters}):',
        'loop': 'for {item} in {iterable}:',
        'conditional': 'if {condition}:',
        'file_io': '{file_operation}("{file_path}", "{mode}")',
        'data_manipulation': '{variable_name} = {data_source}.{manipulation_operation}()',
        'api_request': 'response = requests.{request_method}("{url}", {parameters})',
        'database_operation': 'db.{operation}({table_name}, {parameters})'
    },
    'html': {
        'tag': '<{tag}>{content}</{tag}>',
        'attribute': '{attribute}="{value}"',
        'css_style': '{property}: {value};'
    },
    'css': {
        'selector': '{selector} {{\n\t{property}: {value};\n}}'
    },
    'javascript': {
        'variable': 'const {variable_name} = {value};',
        'function': 'function {function_name}({parameters}) {{\n\t{code}\n}}',
        'array_iteration': '{array}.forEach(function({item}) {{\n\t{code}\n}});',
        'api_request': 'fetch("{url}", {options})\n\t.then(function(response) {{\n\t\treturn response.json();\n\t}})\n\t.then(function(data) {{\n\t\tconsole.log(data);\n\t}});'
    }
}

def code_generator(prompt, language='python'):
    # Process the prompt using NLP techniques to determine the desired code structure and details
    # ...
    # Additional NLP processing logic can be implemented here
    
    # Example code generation based on the given prompt and language
    code = ''
    
    if language not in code_templates:
        return 'Unsupported programming language.'
    
    # Generate the code structure based on the given prompt
    if 'import' in prompt:
        module = get_prompt_details(prompt, 'import')
        code += code_templates[language]['import'].format(module=module) + '\n'
    elif 'function' in prompt:
        function_name = get_prompt_details(prompt, 'function')
        parameters = get_prompt_details(prompt, 'parameters')
        code += code_templates[language]['function'].format(function_name=function_name, parameters=parameters) + ':\n\t# Add function implementation here\n'
    elif 'loop' in prompt:
        item = get_prompt_details(prompt, 'item')
        iterable = get_prompt_details(prompt, 'iterable')
        code += code_templates[language]['loop'].format(item=item, iterable=iterable) + ':\n\t# Add loop code here\n'
    elif 'conditional' in prompt:
        condition = get_prompt_details(prompt, 'condition')
        code += code_templates[language]['conditional'].format(condition=condition) + ':\n\t# Add conditional code here\n'
    elif 'file I/O' in prompt:
        file_operation = random.choice(['open', 'read', 'write', 'close'])
        file_path = get_prompt_details(prompt, 'file_path')
        mode = get_prompt_details(prompt, 'mode')
        code += code_templates[language]['file_io'].format(file_operation=file_operation, file_path=file_path, mode=mode) + '\n'
    elif 'data manipulation' in prompt:
            data_source = get_prompt_details(prompt, 'data_source')
def code_generator(prompt, language='python'):
    code_templates = {
        'python': {
            'data_manipulation': "data_manipulation code template",
            'api_request': "api_request code template",
            'database_operation': "database_operation code template",
            'tag': "HTML tag code template",
            'attribute': "HTML attribute code template",
            'css_style': "CSS style code template",
            'variable': "JavaScript variable code template",
            'function': "JavaScript function code template",
            'array_iteration': "JavaScript array iteration code template",
            'api_request': "JavaScript API request code template"
        },
        # Include templates for other languages if needed
    }

    code = ""

    if 'data manipulation' in prompt:
        data_source = get_prompt_details(prompt, 'data_source')
        manipulation_operation = get_prompt_details(prompt, 'manipulation_operation')
        variable_name = generate_variable_name()
        code += code_templates[language]['data_manipulation'].format(variable_name=variable_name, data_source=data_source, manipulation_operation=manipulation_operation) + '\n'
    elif 'API request' in prompt:
        request_method = get_prompt_details(prompt, 'request_method')
        url = get_prompt_details(prompt, 'url')
        parameters = get_prompt_details(prompt, 'parameters')
        code += code_templates[language]['api_request'].format(request_method=request_method, url=url, parameters=parameters) + '\n'
    elif 'database operation' in prompt:
        operation = get_prompt_details(prompt, 'operation')
        table_name = get_prompt_details(prompt, 'table_name')
        parameters = get_prompt_details(prompt, 'parameters')
        code += code_templates[language]['database_operation'].format(operation=operation, table_name=table_name, parameters=parameters) + '\n'
    elif 'HTML tag' in prompt:
        tag = get_prompt_details(prompt, 'tag')
        content = get_prompt_details(prompt, 'content')
        code += code_templates[language]['tag'].format(tag=tag, content=content) + '\n'
    elif 'HTML attribute' in prompt:
        attribute = get_prompt_details(prompt, 'attribute')
        value = get_prompt_details(prompt, 'value')
        code += code_templates[language]['attribute'].format(attribute=attribute, value=value) + '\n'
    elif 'CSS style' in prompt:
        property = get_prompt_details(prompt, 'property')
        value = get_prompt_details(prompt, 'value')
        code += code_templates[language]['css_style'].format(property=property, value=value) + '\n'
    elif 'JavaScript variable' in prompt:
        variable_name = generate_variable_name()
        value = get_prompt_details(prompt, 'value')
        code += code_templates[language]['variable'].format(variable_name=variable_name, value=value) + '\n'
    elif 'JavaScript function' in prompt:
        function_name = get_prompt_details(prompt, 'function_name')
        parameters = get_prompt_details(prompt, 'parameters')
        inner_code = get_prompt_details(prompt, 'code')
        code += code_templates[language]['function'].format(function_name=function_name, parameters=parameters, code=inner_code) + '\n'
    elif 'JavaScript array iteration' in prompt:
        array = get_prompt_details(prompt, 'array')
        item = generate_variable_name()
        inner_code = get_prompt_details(prompt, 'code')
        code += code_templates[language]['array_iteration'].format(array=array, item=item, code=inner_code) + '\n'
    elif 'JavaScript API request' in prompt:
        url = get_prompt_details(prompt, 'url')
        options = get_prompt_details(prompt, 'options')
        code += code_templates[language]['api_request'].format(url=url, options=options) + '\n'
    else:
        return 'No code generation functionality found for the given prompt.'

    # Run the generated code and check for any errors
    try:
        exec(code)
        return code
    except Exception as e:
        return f'Code execution failed. Error: {str(e)}'


def get_prompt_details(prompt, keyword):
    # Extract the details based on the provided keyword from the natural language prompt
    # Implement your logic here
    return ''  # Placeholder for extracted details


def generate_variable_name():
    # Generate a meaningful variable name
    # Implement your logic here
    return 'variable'




################################################################
# CODE_ANALYZER


def code_analyzer(filepath):
    # Analyze the code using pylint
    pylint_output = subprocess.check_output(['pylint', filepath], universal_newlines=True, stderr=subprocess.STDOUT)
    
    # Process the pylint output and extract the relevant information
    error_lines = []
    suggestion_lines = []
    corrected_code_lines = []
    is_error_section = False
    is_suggestion_section = False
    
    for line in pylint_output.splitlines():
        if line.startswith('*************'):
            is_error_section = True
        elif line.startswith('---'):
            is_error_section = False
        elif line.startswith('Your code has been rated'):
            is_suggestion_section = True
        elif line.startswith('---'):
            is_suggestion_section = False
        elif is_error_section:
            error_lines.append(line)
        elif is_suggestion_section:
            suggestion_lines.append(line)
        else:
            corrected_code_lines.append(line)
    
    # Print the errors, suggestions, and corrected code
    print('Errors:')
    for error_line in error_lines:
        print(error_line)
    
    print('\nSuggestions:')
    for suggestion_line in suggestion_lines:
        print(suggestion_line)
    
    print('\nCorrected Code:')
    for corrected_code_line in corrected_code_lines:
        print(corrected_code_line)
    
    # Run the code and check for errors
    try:
        subprocess.check_output(['python', filepath], stderr=subprocess.STDOUT)
        print('\nCode ran successfully.')
    except subprocess.CalledProcessError as e:
        print(f'\nCode execution error: {e.output}')


################################################################
# CSV_MANAGER

def csv_manager(file_path, mode='r', data=None, convert_to_json=False):
    if mode == 'r':
        # Read CSV file and print its contents
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for lines in csv_reader:
                print(lines)
    elif mode == 'w':
        # Create a new CSV file and write the data
        with open(file_path, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            for row in data:
                csv_writer.writerow(row)
    elif mode == 'convert_to_csv':
        # Convert raw data to CSV and write to a file
        with open(file_path, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            for line in data:
                csv_writer.writerow([line])
    elif mode == 'convert_to_json':
        # Convert CSV to JSON and write to a file
        csv_data = []
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for lines in csv_reader:
                csv_data.append(lines)
        json_data = []
        for row in csv_data:
            json_data.append({f"field_{i+1}": value for i, value in enumerate(row)})
        json_file_path = file_path[:-4] + '.json'
        with open(json_file_path, mode='w') as json_file:
            json.dump(json_data, json_file, indent=4)
    else:
        print("Unsupported mode.")

################################################################
# ERROR HANDLER

class CustomError(Exception):
    pass

def errorhandler():
    try:
        # Some operation that can throw an exception
        # ...

        # Example: Division by zero
        numerator = 10
        denominator = 0
        result = numerator / denominator

        # ...

    except ZeroDivisionError as e:
        print("Error: Division by zero.")
        print(f"Caught an exception: {e}")
    except CustomError as e:
        print(f"Caught a custom exception: {e}")
    except Exception as e:
        print("An error occurred.")
        print(f"Caught an exception: {e}")
    else:
        print("No exceptions occurred.")
    finally:
        print("Error handling completed.")

# Example usage:
errorhandler()


################################################################
# GTTS AND STT


def tts(text, lang='en'):
    speech = gTTS(text = text, lang = lang, slow = False)
    speech.save("text.mp3")
    os.system("start text.mp3")

def stt(audio_file):
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
        text = r.recognize_google(audio)
        return text


################################################################
# WRITE_TO_FILES

def write_to_file(filename: str, content: str, file_format: str = 'txt') -> str:
    # Create a map of supported file formats and their corresponding write modes
    file_modes = {'txt': 'w', 'bin': 'wb', 'json': 'w'}

    # If the given file format is not supported, raise an exception
    if file_format not in file_modes.keys():
        raise ValueError(f"Unsupported file format: {file_format}")

    try:
        # Prepare full path for the file
        full_file_path = f"{filename}.{file_format}"

        # Open file in corresponding write mode
        with open(full_file_path, file_modes[file_format]) as f:
            # If it is a binary file, we need to encode the content
            if file_format == 'bin':
                content = content.encode()

            f.write(content)

        print(f"File written successfully. The file is stored at {full_file_path}")

        return full_file_path
    except Exception as e:
        # Log the exception and re-raise it
        print(f"Failed to write to the file: {e}")
        raise e











################################################################
#INGEST_DATA




def ingest_data(file_path):
    with open('knowledge_base_raw.txt', 'r', encoding='utf-8', errors='ignore') as file:
        data = file.read()
        # Process and convert the data to JSON format
        json_data = process_data(data)
        
    # Store the converted data in knowledge_base.json
    with open('knowledge_base.json', 'a') as kb_file:
        kb_file.write(json.dumps(json_data))
    
    print("Data has been ingested and stored in knowledge_base.json.")

def process_data(data):
    # Perform any necessary preprocessing or data conversion here
    # Convert the data to JSON format
    json_data = {
        'data': data
    }
    
    return json_data

# Usage example
ingest_data('knowledge_base_raw.txt')




################################################################


def ingest_data(source, file_type):
    if source.startswith('http://') or source.startswith('https://'):
        # Ingest data from URL
        try:
            response = requests.get(source)
            if response.status_code == 200:
                data = response.text
                # Process data based on file type
                if file_type == 'html':
                    # Extract data from HTML
                    extracted_data = extract_data_from_html(data)
                    append_to_knowledge_base(extracted_data)
                elif file_type == 'json':
                    # Ingest JSON data directly
                    ingest_json_data(data)
                elif file_type == 'csv':
                    # Ingest CSV data
                    ingest_csv_data(data)
                elif file_type == 'pdf':
                    # Convert PDF to text and ingest
                    text_data = convert_pdf_to_text(data)
                    ingest_text_data(text_data)
                else:
                    print("Unsupported file type.")
            else:
                print("Failed to retrieve data from the URL.")
        except requests.exceptions.RequestException as e:
            print("Error occurred while retrieving data from the URL:", str(e))
    else:
        # Ingest data from local file path
        if os.path.exists(source):
            with open(source, 'r') as file:
                data = file.read()
                # Process data based on file type
                if file_type == 'txt':
                    # Ingest text data
                    ingest_text_data(data)
                elif file_type == 'json':
                    # Ingest JSON data
                    ingest_json_data(data)
                elif file_type == 'csv':
                    # Ingest CSV data
                    ingest_csv_data(data)
                elif file_type == 'pdf':
                    # Convert PDF to text and ingest
                    text_data = convert_pdf_to_text(data)
                    ingest_text_data(text_data)
                else:
                    print("Unsupported file type.")
        else:
            print("File not found.")
            
            
# def extract_data_from_html(html_data):
# Use BeautifulSoup or other HTML parsing libraries to extract data from HTML
# Implement your code here

 #   def ingest_json_data(json_data):
    # Ingest JSON data
    # Implement your code here

#def ingest_csv_data(csv_data):
    # Ingest CSV data
    # Implement your code here

#def Convert_pdf_to_text(pdf_data):
    # Convert PDF data to text
    # Implement your code here

#def ingest_text_data(text_data):
    # Ingest text data
    # Implement your code here

#def append_to_knowledge_base(data):
    # Append data to the knowledge base file
  # if os.path.exists(knowledge_base_file):
  #     with open(knowledge_base_file, 'r') as file:
  #         knowledge_base = json.load(file)
  # else:
  #     knowledge_base = {}
   #knowledge_base.update(data)
   #with open(knowledge_base_file, 'w') as file:
    #   json.dump(knowledge_base, file, indent=4)
def process_raw_data(file_path):
    # Process raw data from the knowledge_base_raw file
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = file.read()
            # Process data based on file type
            if file_path.endswith('.txt'):
                # Process text data
                ingest_text_data(data)
            elif file_path.endswith('.json'):
                # Process JSON data
                ingest_json_data(data)
            elif file_path.endswith('.csv'):
                # Process CSV data
                ingest_csv_data(data)
            elif file_path.endswith('.pdf'):
                # Convert PDF to text and process
                text_data = convert_pdf_to_text(data)
                ingest_text_data(text_data)
            else:
                print("Unsupported file type.")
    else:
        print("File not found.")

def convert_txt_to_json(txt_file):
    # Convert a text file to JSON format
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as file:
            data = file.read()
            # Process data and convert to JSON
            # Implement your code here
            json_data = process_and_convert_to_json(data)
            # Append converted JSON data to knowledge_base.json
            append_to_knowledge_base(json_data)
    else:
        print("File not found.")

# Additional functions for web scraping if needed
def scrape_data_from_html(url):
    # Implement web scraping logic here
    # Extract the required data from the HTML page
    # Return the extracted data

    # Main code
    def main():
        # Ingest data from specified URLs or local file paths
        ingest_data('https://example.com/data.html', 'html')
        ingest_data('data.json', 'json')
        ingest_data('data.csv', 'csv')
        ingest_data('data.pdf', 'pdf')
        
        # Process raw data from knowledge_base_raw file
        process_raw_data(knowledge_base_raw_file)
        
        # Convert a text file to JSON format
        convert_txt_to_json('data.txt')
        
        # Web scraping example
        scraped_data = scrape_data_from_html('https://example.com')
        append_to_knowledge_base(scraped_data)
        
        

if __name__ == "__main__":
      main()
      
      
      
 #####################
 #Github Repository to .txt converter
 
 #!/usr/bin/env python3

import os
import sys
import fnmatch

def get_ignore_list(ignore_file_path):
    ignore_list = []
    with open(ignore_file_path, 'r') as ignore_file:
        for line in ignore_file:
            if sys.platform == "win32":
                line = line.replace("/", "\\")
            ignore_list.append(line.strip())
    return ignore_list

def should_ignore(file_path, ignore_list):
    for pattern in ignore_list:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def process_repository(repo_path, ignore_list, output_file):
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, repo_path)

            if not should_ignore(relative_file_path, ignore_list):
                with open(file_path, 'r', errors='ignore') as file:
                    contents = file.read()
                output_file.write("-" * 4 + "\n")
                output_file.write(f"{relative_file_path}\n")
                output_file.write(f"{contents}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python git_to_text.py /path/to/git/repository [-p /path/to/preamble.txt] [-o /path/to/output_file.txt]")
        sys.exit(1)

    repo_path = sys.argv[1]
    ignore_file_path = os.path.join(repo_path, ".gptignore")
    if sys.platform == "win32":
        ignore_file_path = ignore_file_path.replace("/", "\\")

    if not os.path.exists(ignore_file_path):
        # try and use the .gptignore file in the current directory as a fallback.
        HERE = os.path.dirname(os.path.abspath(__file__))
        ignore_file_path = os.path.join(HERE, ".gptignore")

    preamble_file = None
    if "-p" in sys.argv:
        preamble_file = sys.argv[sys.argv.index("-p") + 1]

    output_file_path = 'output.txt'
    if "-o" in sys.argv:
        output_file_path = sys.argv[sys.argv.index("-o") + 1]

    if os.path.exists(ignore_file_path):
        ignore_list = get_ignore_list(ignore_file_path)
    else:
        ignore_list = []

    with open(output_file_path, 'w') as output_file:
        if preamble_file:
            with open(preamble_file, 'r') as pf:
                preamble_text = pf.read()
                output_file.write(f"{preamble_text}\n")
        else:
            output_file.write("The following text is a Git repository with code. The structure of the text are sections that begin with ----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.\n")
        process_repository(repo_path, ignore_list, output_file)
    with open(output_file_path, 'a') as output_file:
        output_file.write("--END--")
    print(f"Repository contents written to {output_file_path}.")

    
def chat_interface(input_text, chat_history=None):
    response, chat_history = generate_response(input_text, chat_history)
    return response, chat_history.tolist()    
    
 iface = gr.Interface(
    fn=chat_interface,
    inputs=["text", "list"],
    outputs=["text", "list"],
    layout="vertical",
    theme="huggingface"
)
iface.launch()
