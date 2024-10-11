from streamlit_option_menu import option_menu
import requests
from bs4 import BeautifulSoup
import streamlit as st
from gtts import gTTS
from io import BytesIO
import openai
from youtubesearchpython import *
import io
import requests
import PyPDF2
import langchain
langchain.verbose = False
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
import time
from scripts.news import *
import google.generativeai as genai
from PyPDF2 import PdfReader #library to read pdf files
from langchain.text_splitter import RecursiveCharacterTextSplitter#library to split pdf files
from langchain_google_genai import GoogleGenerativeAIEmbeddings #to embed the text
from langchain_google_genai import ChatGoogleGenerativeAI #
from langchain.prompts import PromptTemplate #to create prompt templates
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
genai.configure(api_key="AIzaSyDLorkWwdH018SkuDl3ROqYENBJT582a00")

def imagedetect(img):
    import google.generativeai as genai
    genai.configure(api_key=st.secrets["gemini_api"])
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(img)
    return response.text
def palm_pdf(txt):

    prompt = f"""
    You are an expert at Reading PDF from Links as summarize it.
    Summarize the PDF and give some Keypoints.
    This is the link :{txt}
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    st.markdown(response.text,unsafe_allow_html=True)
    return(response.text)
def ai_palm(txt):

    prompt = f"""
    You are an expert at Teaching.
    explain me about: {txt}
    Explain with examples, as im a school student.
    Give Points to note down.
    also give some reference
    Think about it step by step, and show your work.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    st.markdown(response.text,unsafe_allow_html=True)
    return(response.text)
def ai_chat(txt, context=""):
    
    prompt = f"""
    **Previous Conversation:**
    {context}
    Act as a Professor 
    **User:** {txt}
    **as Professor Reply to user:**
    (Provide explanation here...)
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    #st.markdown(response.text,unsafe_allow_html=True)
    return(response.text)
def palm_conversation(context=""):
    col1, col2 = st.columns([2, 1])  # Adjust column widths as needed
    with col1:
        st.title("StudentGPT")
        st.markdown("## Your AI Teacher - You can clear your doubts here")
        st.markdown("Ask me anything! I'm here to help you with your studies, from explaining complex concepts to providing personalized examples. Stuck on a problem with diagrams or figures? No worries! Simply upload an image of your question, and I'll analyze it and do my best to provide the answer.")
    
    with col2:
        st.image("images/hero1.png", use_column_width=True)
        
    image = st.file_uploader(label="Upload your image here", type=['png', 'jpg', 'jpeg'])
    submit = st.button("New Chat")
    
    if image is not None:
        # Check file size
        if image.size <= 10 * 1024 * 1024:  # 1MB limit
            # Process the uploaded image
            st.image(image, caption="Uploaded Image", use_column_width=True)
        else:
            st.error("File size should be less than 1MB. Please upload a smaller file.")
    if submit:
        st.session_state["data"] = " "
        st.session_state["pal_context"] = ""
        st.session_state.messages = []
    if image is not None and st.session_state["data"] == " ":
        input_image = Image.open(image)
        # st.image(input_image)
        with st.spinner("🤖 AI is at Work! "):
            st.session_state["data"] = imagedetect(input_image)
            st.markdown(st.session_state["data"])
            audio_bytes = speak(st.session_state["data"])
            st.audio(audio_bytes, format='audio/ogg')
            # st.markdown(imgtxt)
            # result_text = extract_text_from_image(input_image)
            # st.write(result_text)
            # st.balloons()
            # text = (" ".join(result_text))
            # models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
            # model = models[0].name
            # prompt = f"""
            # **Questions:**
            # {text}
            # Act as a Professor 
            # **as Professor Answer to the Questions:**
        
            # (Provide explanation here...)
            # """
        
            # completion = palm.generate_text(
            #     model=model,
            #     prompt=prompt,
            #     temperature=0,
            #     # The maximum length of the response
            #     max_output_tokens=800,
            # )
    else:
        st.write("Upload an Image")
    # Initialize session state if needed
    if "data" not in st.session_state:
        st.session_state["data"] = " "
    if "pal_context" not in st.session_state:
        st.session_state["pal_context"] = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Title and prompt input
    #st.title("StudenBae-AI")
    prompt = st.chat_input("What would you like to learn about?")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])    
    # Update session state and display user message
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner('Processing...'):
            with st.chat_message("user"):
                st.markdown(prompt)
    
        try:
            # Check if context variables are None and set them to an empty string if needed
            data_context = str(st.session_state["data"]) if st.session_state["data"] else ""
            pal_context = str(st.session_state["pal_context"]) if st.session_state["pal_context"] else ""
    
            # Generate response from PaLM using ai_palm function
            full_response = ai_chat(prompt, data_context + " " + pal_context)
    
            if not full_response.strip():  # Check if full_response is empty or contains only whitespace
                raise ValueError("Empty response")
    
            # Update context and show assistant message
            st.session_state["pal_context"] += "\n" + prompt + "\n" + full_response
            with st.chat_message("assistant"):
                st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    
        except Exception as e:
            # Display a studentGpt message if there's an issue or an empty response
            error_message = "I'm a studentGpt and couldn't generate a response. Please ask me anything else."
            with st.chat_message("assistant"):
                st.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
        
# Run the conversation function

def ai_HR1(role):
    
    prompt = f"""
    Develop an HR system for {role} interviews. Create 7 technical questions with short answers, 3 behavioral questions with answers, and 3 coding questions with solutions.
    Also, suggest 5 key resume points for {role} and propose 3 project ideas showcasing a candidate's suitability: 
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    st.markdown(response.text,unsafe_allow_html=True)
    return(response.text)



from deta import Deta
def db(link,vectors):
    try:
      deta = Deta(st.secrets["data_key"])
      db = deta.Base("Vectors")
      db.put({"link": link, "texts": vectors})
    except:
       st.error("Access Denied")
def pdfs(s):
    try:
      links=[]
      try:
          from googlesearch import search
      except ImportError:
          print("No module named 'google' found")
      query = f"{s} filetype:pdf"
      for j in search(query, tld="co.in", num=1, stop=1, pause=2):
          if ".pdf" in j:
              k = j.split("/")
              print(k[-1])
              print(j)
              
              links.append(j)
      st.markdown("SEARCHING FOR THE DOCUMENTS RELATED TO "+s)
      return links
    except:
       st.error("PDF NOT FOUND")
def pdftotxt(urls):
    try:
        
      texts=""
      for url in urls:
          
          
          st.write("PROCESSING: "+url)
          with st.spinner('Wait for it...'):
              time.sleep(5)
          st.success('Done!')
          response = requests.get(url)
          # Create a file-like object from the response content
          pdf_file = io.BytesIO(response.content)
          # Use PyPDF2 to load and work with the PDF document
          pdf_reader = PyPDF2.PdfReader(pdf_file)
          # Access the document information
          num_pages = len(pdf_reader.pages)
    
          # Perform further operations with the PDF document as needed
          # For example, extract text from each page
          for page in pdf_reader.pages:
              txt=page.extract_text()
              texts += txt
              #db(url,txt)
      time.sleep(.5)      
      st.info("DATA EXTRACTION DONE")
      return texts
    except:
       st.error("Converstion Failed")
        # Print the extracted text
    
def chunks(texts,q):
    try:
        
      st.info("DATA TRANFORMATION STARTED")
      st.info("TRANFORMING DATA INTO CHUNKS")
      text_splitter = CharacterTextSplitter(separator = "\n",chunk_size = 1000,chunk_overlap  = 200,
      length_function = len,)
      texts = text_splitter.split_text(texts)
      embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["api"])
      docsearchs = FAISS.from_texts(texts, embeddings)
      chain = load_qa_chain(OpenAI(openai_api_key=st.secrets["api"]), chain_type="stuff")
      with st.spinner('Wait for it...'):
          time.sleep(5)
      st.success('Done!')
      time.sleep(.5)
      st.info("DATA IS LOADED AS CHUNKS AND READY FOR ANALYTICS PURPOSE")
      query=q
      docs = docsearchs.similarity_search(query)
      title=chain.run(input_documents=docs, question="TITLE of the paper")
      query=chain.run(input_documents=docs, question=query)
      st.write(title)
      st.write(query)
      data=f"{title},{query}"
      audio_bytes=speak(data)
      st.audio(audio_bytes, format='audio/ogg')
    except:
       st.error("Error processing Text") 
  
def ai(prompt,n):
  try:
    updated_prompt = f"act as a well experienced professor and explain {prompt} as explainig to your student think step by step and give real time examples and key points but it should be below 150 words",
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=updated_prompt,
      temperature=n,
      max_tokens=150,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.6,
      stop=[" Human:", " AI:"]
    )
    data = response.choices[0].text
    st.markdown(response.choices[0].text,unsafe_allow_html=True)
    return data
  except:
     st.error("Unable Connect To The Server")  
openai.api_key = st.secrets["api"]
start_sequence = "\nAI:"
restart_sequence = "\nHuman: "
def sql(t,q):
  try:
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=f"###{t}\n#\n### {q}\n",
      temperature=1,
      max_tokens=2000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.6,
      stop=[" Human:", " AI:"]
    )
    data = response.choices[0].text
    st.markdown(response.choices[0].text,unsafe_allow_html=True)
    return data
  except:
     st.error("Error connecting the server")
def pearson(my_string):
  try:  
    try:
      from googlesearch import search
      import re
    except ImportError:
      print("No module named 'google' found")
    query = my_string
    pattern = "(instagram|facebook|youtube|twitter|github|linkedin|scholar|hackerrank|tiktok|maps)+\.(com|edu|net|fandom)"
    for i in search(query, tld="co.in", num=20, stop=15, pause=2):
      if (re.search(pattern, i)):
          social_media_name = re.search(pattern, i).group(1)
          title = f"<b>{social_media_name}</b>"
          st.markdown(f'<p style="font-size: larger;">{title}</p>', unsafe_allow_html=True)
          st.markdown(f'<a href="{i}">View more</a>', unsafe_allow_html=True)
      else:
        print("match not found")
  except:
     st.error("Service Unavailable")
            
def yt(vd):
    try:
       
      customSearch = VideosSearch(vd,limit = 20)
      for i in range(20):
          st.video(customSearch.result()['result'][i]['link'])
    except:
       st.error("Video Not Found")
def speak(text):
    mp3_fp = BytesIO()
    tts = gTTS(text, lang='en')
    tts.write_to_fp(mp3_fp)
    return mp3_fp
def pdf(s):
    try:
        try:
            from googlesearch import search
        except ImportError:
            print("No module named 'google' found")
        query = f"filetype:pdf {s}"
        for j in search(query, tld="co.in", num=10, stop=5, pause=2):
            if ".pdf" in j:
                k = j.split("/")
                for i in k:
                    if ".pdf" in i:
                        st.write(i)
                        # Assuming palm_pdf is a function you have defined elsewhere
                        #palm_pdf(j)
                # Assuming you want to display a download link using Streamlit
                palm_pdf(j)
                st.markdown(f'<a href="{j}" download>DOWNLOAD</a>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")
        st.error("PDF NOT Found")
def ppt(s):
    try:
        from googlesearch import search
    except ImportError:
        print("No module named 'google' found")
    query = f"filetype:ppt {s}"
   
    for j in search(query, tld="co.in", num=10, stop=5, pause=2):
        if ".ppt" in j:
            k = j.split("/")
            for i in k:
                if ".ppt" in i:
                    st.write(i)
#             st.components.v1.iframe(j)
            st.markdown(f'<a href="{j}">DOWNLOAD</a>', unsafe_allow_html=True)
def torrent_download(search):
    try:
      url = f"https://1377x.xyz/fullsearch?q={search}"
      r = requests.get(url)
      data = BeautifulSoup(r.text, "html.parser")
      links = data.find_all('a', style="font-family:tahoma;font-weight:bold;")
      torrent = []
      ogtorrent = []
      for link in links:
          st.write(link.text)
          torrent.append(f"https://ww4.1337x.buzz{link.get('href')}")
          url = f"https://ww4.1337x.buzz{link.get('href')}"
          r = requests.get(url)
          data = BeautifulSoup(r.text, "html.parser")
          links = data.find_all('a')
          for link in links:
              link = link.get('href')
              if "magnet" in str(link):
                  st.markdown(f'<a href="{str(link)}">DOWNLOAD</a>', unsafe_allow_html=True)
              if "torrents.org" in str(link):
                  ogtorrent.append(str(link))
    except:
       st.error("Course Not Found")
def display(data):
  try:
  
    st.image("images/search1.png")
    def local_css(file_name):
          with open(file_name) as f:
              st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    def remote_css(url):
          st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)
    def icon(icon_name):
          st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)
        
    local_css("style.css")
    remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
    form = st.form(key='my-form')
    selected = form.text_input("", "")
    submit = form.form_submit_button("SEARCH")
    if submit:
      if "PDF" in data:
        pdf(selected)
      elif "PPT" in data:
        ppt(selected)
      elif "Courses" in data:
        st.write('''Fair Use Act Disclaimer
          This site is for educational purposes only!!
                              **FAIR USE**
        Copyright Disclaimer under section 107 of the Copyright Act 1976, allowance 
        is made for “fair use” for purposes such as criticism, comment, news reporting, teaching, 
        scholarship, education and research.Fair use is a use permitted by copyright statute that might
        otherwise be infringing. Non-profit, educational or personal use 
        tips the balance in favor of fair use. ''')
        torrent_download(selected)
        
                    
      elif "Research papers" in data:
        selected = f"{selected} research papers"
        pdf(selected)
      elif "Question Papers" in data:
        selected = f"{selected} Question Papers"
        pdf(selected)
      elif "E-BOOKS" in data:
        selected = f"{selected} BOOK"
        pdf(selected)
      elif "Hacker Rank" in data:
        st.write(f"[OPEN >](https://www.hackerrank.com/domains/{selected})")
  except:
     st.error("Service Unavailable")
def get_pdf_text(pdf_docs):
    text = ""
    # iterate over all pdf files uploaded
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        # iterate over all pages in a pdf
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    #create an object of RecursiveCharacterTextSplitter with specific chunk size and overlap size
    text_splitter = CharacterTextSplitter(separator = "\n",chunk_size = 1000,chunk_overlap  = 200,
      length_function = len,)
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size = 10000, chunk_overlap = 1000)
    # now split the text we have using object created
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",google_api_key=st.secrets["gemini_api"])  # type: ignore
    vector_stores = FAISS.from_texts(chunks, embedding=embeddings)
    st.write("processing..")
    
    vector_stores.save_local("faiss_index")
    
# def get_vector_store(text_chunks):
#     embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001",google_api_key=st.secrets["gemini_api"] ) # google embeddings
#     vector_store = FAISS.from_texts(text_chunks, embeddings)
    
#     # Incrementally build the index and save periodically
#     for chunk in text_chunks:
#         vector_store.add(embeddings.encode(chunk))
#         vector_store.save_local("faiss_index_partial")
    
#     # Final save
#     vector_store.save_local("faiss_index")
#     st.success('Data loaded')

#     return 1
def get_conversation_chain():
    # define the prompt
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details\n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model = "gemini-pro", temperatue = 0.6,google_api_key=st.secrets["gemini_api"]) # create object of gemini-pro
    prompt = PromptTemplate(template = prompt_template, input_variables= ["context","question"])
    chain = load_qa_chain(model,chain_type="stuff",prompt = prompt)
    return chain
def user_input(user_question):
    # user_question is the input question
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001",google_api_key=st.secrets["gemini_api"])
    # load the local faiss db
    new_db = FAISS.load_local("faiss_index",  embeddings,allow_dangerous_deserialization=True)
    # using similarity search, get the answer based on the input
    docs = new_db.similarity_search(user_question)
    chain = get_conversation_chain()
    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)
    print(response)
    st.write("Reply: ", response["output_text"])
def talkpdf():
    import google.generativeai as genai
    genai.configure(api_key=st.secrets["gemini_api"])
    st.header("Chat with PDF")
    
    user_question = st.text_input("Ask a Question:")
    if user_question:
        with st.spinner("Processing..."):
            user_input(user_question)
    options = st.multiselect(
            'Select Interaction Type:',
            ["Short Q&A - 2 to 4 lines", "Long Q&A - 10 to 20 lines", "Multiple Choice - with answers"])
    n = st.slider('Number of Questions?', 0, 40, 1)
    
    submit = st.button("Submit")
    if submit:
        if options:
            for i in options:
                with st.spinner("Processing..."):
                    user_input(f"Give me the most important, top {n} question and answers, in form of "+i)
  
    pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
    if st.button("Submit & Process"):
        with st.spinner("Processing..."):
            raw_text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(raw_text)
            get_vector_store(text_chunks)
            st.success("Done")
new_db = ''
def advancesearch():
    s = st.text_input("Topic")
    if st.button("Search & Process"):
        urls=pdfs(s)
        raw_text = pdftotxt(urls)
        text_chunks = get_text_chunks(raw_text)
        t = get_vector_store(text_chunks)
        st.success("Done")
    import google.generativeai as genai
    
    genai.configure(api_key=st.secrets["gemini_api"])
    st.header("Advance Search")
    
    user_question = st.text_input("Ask a Question:")
    if user_question:
        with st.spinner("Processing..."):
            user_input(user_question)
    options = st.multiselect(
            'Select Interaction Type:',
            ["Short Q&A - 2 to 4 lines", "Long Q&A - 10 to 20 lines", "Multiple Choice - with answers"])
    n = st.slider('Number of Questions?', 0, 40, 1)
    
    submit = st.button("Submit")
    if submit:
        if options:
            for i in options:
                with st.spinner("Processing..."):
                    user_input(f"Give me the most important, top {n} question and answers, in form of "+i)
