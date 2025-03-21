Repository for IEEE CBMS 2025 Submission
This repository contains the implementation of our regular paper submitted to the IEEE CBMS 2025 Submission.

MedBlock-Bot: A Blockchain-Enabled RAG System for Providing Feedback to Large Language Models Accessing Pediatric Clinical Guidelines<br/> 
Authors: Mohamed Yaseen Jabarulla, Steffen Oeltze-Jafra, Philipp Beerbaum, Theodor Uden
Affiliation: Peter L. Reichertz Institute for Medical Informatics, TU Braunschweig & Hannover Medical School

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
Download and install Ganache from Truffle Suite.
Start Ganache and create a new workspace.
Copy the RPC URL (e.g., http://127.0.0.1:8545).

#### 2. Configure MetaMask
Install the MetaMask Extension.
Create/import an Ethereum wallet.
Add a Custom RPC Network:
Network Name: Ganache Localhost
New RPC URL: http://127.0.0.1:8545
Chain ID: 1337
Currency Symbol: ETH

------------------------------------------------------------------------------
Deploying Smart Contract<br/>
------------------------------------------------------------------------------

#### 1. Use Remix IDE
Open Remix IDE.
Upload and compile contract.sol.
Deploy the contract using Injected Web3 (connect MetaMask).
Copy the contract address and ABI.

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


#### 2. Run the MedBlock-Bot

```

streamlit run MedBlock-Bot_Script.py
```

Open the provided localhost link in your browser.


