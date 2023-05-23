# Import necessary libraries
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.chat_models import ChatOpenAI

# Set Streamlit page configuratioin
st.set_page_config(page_title='🧠MemoryBot🤖', layout='wide')

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []   # output
if "past" not in st.session_state:
    st.session_state["past"] = []   # past
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

# Define function to get user input
def get_text():
    """
    Get the user input text.
    Returns:
    (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                            placeholder="Your AI assistant here! Ask me anythin...",
                            label_visibility='hidden')
    return input_text

# Define function to start a new chat
def new_chat():
    """
    Clear session state and starts a new chat.
    """

    save = []
    for i in range(len(st.session_state['generated'])-1,-1,-1):
        save.append("User: " + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.entity_store = {}
    st.session_state.entity_memory.buffer.clear()

# Set up sidebar with various options
with st.sidebar.expander("🛠️ ", expanded=False):
    # Option to preview memory store
    if st.checkbox("Preview memory store"):
        with st.expander("Memory-Store", expanded=False):
            st.session_state.entity_memory.store
    # Option to preview memory buffer
    if st.checkbox("Preview memory buffer"):
        with st.expander("Buffer-store", expanded=False):
            st.session_state.entity_memory.buffer
    MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo', 'text-davinci-003','text-davinci-002','code-davinci-002'])
    K = st.number_input(' (#)Summary of prompts to consider', min_value=3, max_value=1000)

# Set up the Streamlit app layout
st.title("🖥️ Chat Bot with 🧠")
st.subheader(" Powered by LangChain + OpenAI + Streamlit")

# Ask the user to enter their OpenAI API key
API_O = st.sidebar.text_input("API-Key", type="password")

# Session state storage would be ideal
if API_O:
    # Create Open AI instance
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=API_O,
        model_name=MODEL,
        request_timeout=120,
        verbose=False
    )

    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm,k=K)

    # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
        llm = llm,
        prompt = ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory = st.session_state.entity_memory 
    )
else:
    st.sidebar.warning("API key required to try this app. The API key is not stored in any form.")
    # st.stop()

# Add a button to start a new chat
st.sidebar.button("New Chat", on_click = new_chat, type='primary')

# Get the user input
user_input = get_text()

# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input:
    output = Conversation.run(input=user_input)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

# Allow to download as well
download_str = []
# Display the conversion history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.info(st.session_state["past"][i],icon="🍪")
        st.success(st.session_state["generated"][i],icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])

    # Can throw error - requires fix
    download_str = '\n'.join(download_str)
    if download_str:
        st.download_button('Download', download_str)

# Display stored conversion sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session
