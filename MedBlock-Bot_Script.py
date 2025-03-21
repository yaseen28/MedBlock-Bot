import streamlit as st
from streamlit_chat import message
from langchain.chains import ConversationChain
from langchain.llms import LlamaCpp
from langchain.memory import ConversationBufferMemory
import time
import torch
from web3 import Web3
import json
import time
import PyPDF2
import fitz


# Function to initialize Web3 connection
def initialize_web3():
    w3 = Web3(Web3.HTTPProvider("HTTP://172.22.96.243:8545")) #replace this also based on local BC Ganache software
    if not w3.is_connected():
        st.error("Failed to connect to the Ethereum network.")
    return w3

#sender_address = ""  # Replace with an account that has ETH (Refer MetaMask)


# Initialize Web3 connection (call this function)
w3 = initialize_web3()

# Load contract ABI and address
with open("abi.json", "r") as file:   #copy this from remix IDE-> compiler option, see below compilatiton details -> ABI
    contract_abi = json.load(file)
contract_address = '' # Replace with deployed contract address from RemixIDE
contract = w3.eth.contract(address=contract_address, abi=contract_abi)


# Initialize session state
def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []


# Function to retrieve feedback data from the blockchain
def retrieve_feedback():
    try:
        # Measure retrieval time
        start_time = time.time()

        # Fetch the total feedback count
        feedback_count = contract.functions.getFeedbackCount().call()
        st.write(f"Total feedback submissions: {feedback_count}")

        feedback_data = []
        if feedback_count > 0:
            for i in range(feedback_count):
                # Fetch feedback by index
                feedback = contract.functions.getFeedback(i).call()
                feedback_data.append({
                    "query": feedback[0],
                    "model_response": feedback[1],
                    "corrected_response": feedback[2],
                    "clinician_name": feedback[3],
                    "score": feedback[4]
                })

        retrieval_time = time.time() - start_time  # Calculate time taken for retrieval

        st.success("✅ Feedback retrieved successfully!")
        st.write(f"⏳ **Retrieval Time:** {retrieval_time:.4f} seconds")
        return feedback_data

    except Exception as e:
        st.error(f"🚨 Error retrieving feedback: {e}")
        return []



# Function to convert feedback to Alpaca-prompt format
def convert_to_alpaca_prompt(feedback_data):
    alpaca_data = []
    for feedback in feedback_data:
        alpaca_data.append({
            "instruction": feedback["query"],
            "input": "",
            "output": feedback["corrected_response"]
        })
    return alpaca_data

# Check account balance
def check_balance(sender_address):
    balance = w3.eth.get_balance(sender_address)
    eth_balance = w3.from_wei(balance, 'ether')
    st.write(f"Account Balance: {eth_balance:.4f} ETH")
    return balance

# Submit feedback to the blockchain
def submit_feedback_to_blockchain(query, model_response, corrected_response, clinician_name, score):
    if w3.is_connected():
        sender_address = ''  # Replace with actual sender address
        private_key = ""  # Replace with actual private key from metamask

        balance = check_balance(sender_address)
        if balance < w3.to_wei(0.01, 'ether'):
            st.error("Insufficient ETH balance to send transaction.")
            return None

        try:
            # Estimate gas dynamically
            estimated_gas = contract.functions.submitFeedback(
                query, model_response, corrected_response, clinician_name, score
            ).estimate_gas({'from': sender_address})

            # Build transaction with adjusted gas limit
            txn = contract.functions.submitFeedback(
                query, model_response, corrected_response, clinician_name, score
            ).build_transaction({
                'chainId': 1337,  # Local Testnet ID
                'gas': estimated_gas + 5000,  # Adding a buffer to avoid "out of gas" errors
                'gasPrice': w3.to_wei('1', 'gwei'),  # Lowering gas price to save ETH
                'nonce': w3.eth.get_transaction_count(sender_address),
            })

            if not private_key:
                st.error("Private key is missing.")
                return None

            # Measure submission time
            start_submission_time = time.time()

            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

            # Measure time until transaction appears in the mempool
            submission_time = time.time() - start_submission_time

            # Measure confirmation time
            start_confirmation_time = time.time()
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            confirmation_time = time.time() - start_confirmation_time

            if tx_receipt.status == 1:
                gas_used = tx_receipt.gasUsed  # Gas consumption for the transaction

                st.success(f"✅ Feedback submitted! Transaction Hash: {tx_hash.hex()}")
                st.write(f"📌 **Transaction Metrics:**")
                st.write(f"- ⏳ **Submission Time:** {submission_time:.4f} seconds")
                st.write(f"- ✅ **Confirmation Time:** {confirmation_time:.4f} seconds")
                st.write(f"- ⛽ **Gas Used:** {gas_used} units")

            else:
                st.error("❌ Transaction failed.")

            return tx_hash.hex()

        except Exception as e:
            st.error(f"🚨 Error submitting feedback: {str(e)}")
            return None

    else:
        st.error("⚠️ Failed to connect to the Ethereum network.")
        return None


# Expert Instruction for HLHS Consensus Paper
hlhs_instruction = """
You are a highly specialized pediatric cardiologist with extensive expertise in imaging children with Hypoplastic Left Heart Syndrome (HLHS). Your primary role is to provide expert-level answers strictly based on the provided consensus paper.

Guidelines:
•	Your answer must be detailed, precise, and strictly evidence-based, using the exact terminology and insights from the consensus paper.
•	If the document contains the necessary information, extract and integrate the relevant details without unnecessary elaboration.
•	If the document does not provide a reliable answer, explicitly state: "The consensus paper does not provide a reliable answer to this question." Do not speculate or introduce information that is not verifiable from the source.
•	When referencing information, ensure clarity and precision, potentially including direct citations or structured explanations.
•	The answer must be concise yet highly informative, avoiding redundant details while covering all essential aspects.
•	Use professional medical language suitable for pediatric cardiologists. Responses should assume the reader has expert-level knowledge."*

Now, please answer the following question based on the consensus paper.
"""

# Function to create the conversational chain
def create_conversational_chain(model_path, temperature, max_tokens, top_p, instructions):
    # Initialize LLM
    llm = LlamaCpp(
        streaming=True,
        model_path=model_path,
        temperature=temperature,
        top_p=top_p,
        max_tokens=min(max_tokens, 1024),
        verbose=True,
        n_ctx=4096,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )

    # Initialize memory for conversation history
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    # Create a conversational chain
    chain = ConversationChain(
        llm=llm,
        memory=memory
    )

    return chain

# Function to handle the chat logic
def conversation_chat(query, chain):
    start_time = time.time()
    result = chain.predict(input=query)  # Predict using the conversational chain
    end_time = time.time()
    response_time = end_time - start_time
    return result, response_time

# Function to extract text from a PDF file
def extract_text_from_pdf(uploaded_file):
    pdf_text = ""
    try:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pdf_text += page.get_text()
        pdf_document.close()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")

    return pdf_text

# Function to display chat history
# Function to display chat history
def display_chat_history(chain, model_path, context=""):
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Your Query:", placeholder="Ask your question", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            with st.spinner('Generating response...'):
                # Limit context to prevent exceeding token limit
                context = context[:2000]  # Only use first 2000 characters to prevent token overflow

                modified_query = f"{hlhs_instruction}\n\n{context}\n\nUser Question: {user_input}"
                output, response_time = conversation_chat(modified_query, chain)

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

            st.info(f"Response generated using {model_path} in {response_time:.2f} seconds")

    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")


# Developer Dashboard
def developer_dashboard():
    st.title("Developer Dashboard")
    st.write("Retrieve feedback data and convert it to Alpaca-prompt format for fine-tuning.")

    if st.button("Retrieve Feedback Data"):
        feedback_data = retrieve_feedback()
        if feedback_data:
            st.success("Feedback data retrieved successfully!")
            st.write("### Feedback Data")
            st.json(feedback_data)

            # Convert to Alpaca-prompt format
            alpaca_data = convert_to_alpaca_prompt(feedback_data)
            st.write("### Alpaca-Prompt Format")
            st.json(alpaca_data)

            # Export as JSON file
            st.download_button(
                label="Download Alpaca-Prompt Data",
                data=json.dumps(alpaca_data, indent=2),
                file_name="alpaca_prompt_data.json",
                mime="application/json"
            )
        else:
            st.error("No feedback data found.")

# Main function to control the app mode
def main():
    # Initialize session state if not already present
    if 'past' not in st.session_state:
        st.session_state['past'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    # Sidebar for mode selection
    app_mode = st.sidebar.selectbox("Choose the mode", ["User Mode", "Developer Dashboard"])

    if app_mode == "User Mode":
        st.image("MHH_LOGO.png", use_column_width=True)
        st.title("Chat with the Model and Submit Feedback")

        # Upload a PDF file for context
        uploaded_pdf = st.file_uploader("Upload a PDF file for context", type=["pdf"])
        context = extract_text_from_pdf(uploaded_pdf) if uploaded_pdf else ""

        # Sidebar model selection
        model_option = st.sidebar.selectbox("Select Model", ["llama3.1", "hippomistral", "Biomistral", "mistral-7b-instruct"])
        model_paths = {
            "llama3.1": "llama3.1.gguf",
            "hippomistral": "hippomistral.gguf",
            "Biomistral": "Biomistral.gguf",
            "mistral-7b-instruct": "mistral-7b-instruct-v0.2.Q6_K.gguf",
        }
        model_path = model_paths[model_option]

        # Sidebar settings for model parameters
        temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.75, 0.01)
        max_tokens = st.sidebar.slider("Max Tokens", 50, 2000, 500)
        top_p = st.sidebar.slider("Top P", 0.0, 1.0, 1.0, 0.01)

        # Create conversation chain
        chain = create_conversational_chain(model_path, temperature, max_tokens, top_p, hlhs_instruction)

        # Display chat interface
        display_chat_history(chain, model_path, context)

        # Feedback form
        st.header("Submit Feedback")
        query = st.session_state['past'][-1] if st.session_state['past'] else ""
        model_response = st.session_state['generated'][-1] if st.session_state['generated'] else ""
        corrected_response = st.text_area("Corrected Response:")
        clinician_name = st.text_input("Clinician Name:")
        score = st.slider("Score (0-6)", 0, 6)

        if st.button("Submit Feedback"):
            if query and model_response and corrected_response and clinician_name:
                tx_hash = submit_feedback_to_blockchain(query, model_response, corrected_response, clinician_name, score)
                if tx_hash:
                    st.success(f"Feedback submitted! Transaction Hash: {tx_hash}")
                else:
                    st.error("There was an issue with submitting the feedback.")
            else:
                st.error("Please fill out all fields in the feedback form.")

    elif app_mode == "Developer Dashboard":
        developer_dashboard()

if __name__ == "__main__":
    main()

