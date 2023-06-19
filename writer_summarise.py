from .writer_utils import get_matching_file_path, read_file_to_string
from .webui_llm import WebUILLM
from modules.text_generation import generate_reply_wrapper
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate


def _summarise_content(content, summarisation_template, state):
    summarisation_file = get_matching_file_path(summarisation_template)
    if(summarisation_file == ""):
        print(f"No teplate file found for {summarisation_template}")
        return ""
    instruction = read_file_to_string(summarisation_file)
    instruction = instruction.replace("{content}", content)

    outputcontent = ""

    for result in generate_reply_wrapper(instruction, state):
        outputcontent += result[0]

    outputcontent = outputcontent.replace(instruction, "")

    return outputcontent

def _summarise_content_langhchain(content, current_summary, state):
    webui_llm = WebUILLM()
    webui_llm.set_state(state)
    # num_tokens = webui_llm.get_num_tokens(content)

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=5000, chunk_overlap=350)
    docs = text_splitter.create_documents([content])

    chain = load_summarize_chain(llm=webui_llm, chain_type='map_reduce') # verbose=True optional to see what is getting sent to the LLM
    output = chain.run(docs)
    # Use it. This will run through the 4 documents, summarize the chunks, then get a summary of the summary.
    # print (output)
    return output

def generate_chain_prompt(text):
    prompt_template = """Write a concise summary of the following extracting the key information:


    {text}


    CONCISE SUMMARY:"""
    PROMPT = PromptTemplate(template=prompt_template, 
                            input_variables=["text"])

    refine_template = (
        "Your job is to produce a final summary\n"
        "We have provided an existing summary up to a certain point: {existing_answer}\n"
        "We have the opportunity to refine the existing summary"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "Given the new context, refine the original summary"
        "If the context isn't useful, return the original summary."
        "EXTENDED SUMARY:"
        ""
    )
    refine_prompt = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template,
    )
    return PROMPT, refine_prompt

    # chain = load_summarize_chain(OpenAI(temperature=0), 
    #                             chain_type="refine", 
    #                             return_intermediate_steps=True, 
    #                             question_prompt=PROMPT, 
    #                             refine_prompt=refine_prompt)    

def add_summarised_content(content, text_box, summarisation_template, current_summary, state, use_langchain, summarisation_enabled, replace=False, add_cr=True):
    if(summarisation_enabled == False):
        return ""
    if(use_langchain):
        summarised_content = _summarise_content_langhchain(content, current_summary, state)
    else:
        summarised_content = _summarise_content(content, summarisation_template, state)
    if(replace):
        text_box = summarised_content
    else:
        text_box += summarised_content
    if(add_cr):
        text_box+="\n\n"
    return text_box
