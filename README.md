Repository for IEEE CBMS 2025 Submission
This repository contains the implementation of our regular paper submitted to the IEEE CBMS 2025 Submission.

MedBlock-Bot: A Blockchain-Enabled RAG System for Providing Feedback to Large Language Models Accessing Pediatric Clinical Guidelines<br/> 
Authors: Mohamed Yaseen Jabarulla, Steffen Oeltze-Jafra, Philipp Beerbaum, Theodor Uden
Affiliation: Peter L. Reichertz Institute for Medical Informatics, TU Braunschweig & Hannover Medical School

## **About the Paper**  
**MedBlock-Bot** is a **blockchain-enabled Retrieval-Augmented Generation (RAG) system** designed to assist clinicians by providing **expert-validated AI responses** to medical queries.  
Traditional LLMs often **deviate from expert consensus** or provide **outdated** responses. MedBlock-Bot enhances trust in AI-generated clinical knowledge by **securing expert feedback on a permissioned blockchain**.  

### **Key Contributions:**  
✅ **RAG-Driven Clinical Query Processing**  
   - Enhances **LLM response accuracy** by retrieving clinical guidelines before generating answers.  
✅ **Evaluation of Open-Source Medical LLMs**  
   - Compares **BioMistral, HippoMistral, and LLaMa 3.1** in interpreting **Hypoplastic Left Heart Syndrome (HLHS) guidelines** [DOI](https://academic.oup.com/ejcts/article/58/3/416/5898365) .  
   - Assesses adherence to clinical best practices through **expert validation**.  
✅ **Blockchain-Based Feedback Storage**  
   - Implements a **permissioned blockchain** to store **clinician feedback securely**.  
   - Ensures **auditability and immutability** of expert assessments.  
✅ **Smart Contract Execution & Feedback Simulation**  
   - Simulates **clinician feedback submission** with **corrected responses, ratings, and clinician identifiers**.  
   - Analyzes **gas usage, transaction efficiency**, and **smart contract execution** in a **local Ethereum test environment (Ganache)**.  
✅ **Interactive Dual-Mode Dashboard**  
   - **Clinician Mode:** View and validate AI-generated medical responses.  
   - **Developer Mode:** Access structured feedback for **AI model refinement**.
   - 
This research **paves the way** for **reliable, evolving AI-driven clinical decision support systems** that ensure **trust, accountability, and knowledge retention**.

------------------------------------------------------------------------------
MedBlock-Bot:<br/> Installation Guide Using Anaconda
------------------------------------------------------------------------------
#### 1. Install Conda

https://docs.conda.io/en/latest/miniconda.html

#### 2. Clone the Repository

```
git clone https://github.com/yaseen28/MedBlock-Bot.git
cd MedBlock-Bot
```

#### 3. Create and Activate a Conda Environment

```
conda create -n MedBlock-Bot python=3.9 -y
conda activate MedBlock-Bot
```

#### 4. Install Dependencies

```
pip install -r requirements.txt
```

#### 5. Download the Quantised model to the Project Folder (Hint: You can also quantise full model using llama.cpp)

The model used for our experiment are BioMistral, HippoMistral and Llama 3.1. 

   NOTE!! Please ensure that you rename the model file to match the name listed in the 'Select Model' dropdown in the browser. 

------------------------------------------------------------------------------
Setting Up Blockchain Environment<br/>
------------------------------------------------------------------------------

#### 1. Install Ganache (Local Ethereum Blockchain)
a. Download and install Ganache from Truffle Suite. [Download (Windows)](https://archive.trufflesuite.com/ganache/)
b. Start Ganache and create a new workspace.
c. Copy the RPC URL (e.g., http://127.0.0.1:8545).

#### 2. Configure MetaMask
a. Install the MetaMask Extension depends on your browser [Download Here] (https://metamask.io/).

b. Connect MetaMask to Ganache:

c. Open MetaMask → Click on Networks → Add a Network Manually.

d. Enter the following:
''''
Network Name: Ganache Local
New RPC URL: http://127.0.0.1:8545
Chain ID: 1337
Currency Symbol: ETH
''''
e. Click Save.

### Import Test Accounts from Ganache:

a. In Ganache, go to Accounts → Click on a Private Key → Copy it.
b. bOpen MetaMask → Import Account → Paste the Private Key.
c. Now you have ETH for testing transactions.

------------------------------------------------------------------------------
Deploying Smart Contract<br/>
------------------------------------------------------------------------------

#### 1. Use Remix IDE
a. Open Remix IDE [lINK](https://remix.ethereum.org/).
b. Create a new file → Paste the Solidity smart contract code from MedBlock_SC.sol.
c. Compile the contract (0.8.x Solidity Compiler).

#### 2. Deploy the Contract on Ganache
> Go to the Deploy & Run Transactions tab.
> Environment: Select Injected Web3 → Connect MetaMask.
> Deploy the contract → Copy the Contract Address

#### 2. Update Contract Details in script.py
Replace the placeholders in script.py:

```
contract_address = "YOUR_DEPLOYED_CONTRACT_ADDRESS"
with open("abi.json", "r") as file:
    contract_abi = json.load(file)
```
------------------------------------------------------------------------------
Running the Application<br/>
------------------------------------------------------------------------------ 
#### 1. Start Ganache
Ensure Ganache is running.

##### 2. Configure Environment Variables in the MedBlock-Bot_Script.py

''''
w3 = Web3(Web3.HTTPProvider("HTTP://172.22.96.243:8545")) #replace this also based on local BC Ganache software
contract_address = "0xYourDeployedContractAddress"
sender_address = '0xYourtestETHwalletaddress'
private_key = "0xYourtestETHwalletprivatekey"  # Replace with actual private key from metamask IT SHOULD BE TESTNETWORK!!!!!!!
''''

#### 2. Run the MedBlock-Bot

```
streamlit run MedBlock-Bot_Script.py
```

Open the provided localhost link in your browser.
Switch between Clinician Mode (Validate responses) and Developer Mode (Analyze AI feedback).


