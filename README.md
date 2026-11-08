
# Ross Tutorial
This document will guide user how to link remote server and setup LLM and Vivado AI MCP. And experience AI-driven FPGA development.



## Connect Remote Server through SSH
- connect server with username, password and IP address
  - modify username/password with requirement,
    - username: `ross-user1@220.128.132.194:2622`
    - password: `123456`
    <img width="3200" height="958" alt="image" src="https://github.com/user-attachments/assets/d1cba477-5255-4e77-96e1-5bf7eaffc1bc" />

- Open Folder as wrokspace and input password again
  <img width="2284" height="1088" alt="image" src="https://github.com/user-attachments/assets/7bb68641-c70f-4a12-b606-5925c03487e7" />
  <img width="2316" height="570" alt="image" src="https://github.com/user-attachments/assets/03f6eb23-82ed-42c9-bc96-4ac984582e9d" />


<br>
<br>

## Setup Local LLM
- Open Chat box
  <img width="2562" height="1377" alt="image" src="https://github.com/user-attachments/assets/303c2b72-c481-4817-9961-0e87c87b63bc" />
- Select **Local** in CHAT box
  <img width="2556" height="1390" alt="image" src="https://github.com/user-attachments/assets/705c298d-0c48-4590-8f28-1aeb487e47f8" />



- Select **Manage Models...** or **Add Models...** in CHAT box
  <img width="2560" height="1394" alt="image" src="https://github.com/user-attachments/assets/2dc56c7d-02da-4ba8-ab9b-bb951898afdf" />




- Press **Add Models** and Select **Custom Endpoint** <br>
  <img width="1308" height="340" alt="image" src="https://github.com/user-attachments/assets/7928fc6e-2744-4d30-b19f-45ce1d01ce42" /> <br>



- Keep **Group Namd** or type any you like and input **API Key** <br>
  - API Key: `sk-86789d4017a98f36a51de871ee45b0e7495c193af29620610` <br>
  <img width="404" height="76" alt="image" src="https://github.com/user-attachments/assets/522278a9-131e-44d6-b868-b1b2cd247052" /> <br>
  <img width="404" height="74" alt="image" src="https://github.com/user-attachments/assets/26bfe271-c28b-4044-8a40-1d6e449cf4c3" /> <br>

  - and select **Chat Completions Chat Completions API** <br>
  <img width="404" height="98" alt="image" src="https://github.com/user-attachments/assets/e38b063d-9d98-4f19-95ca-2da5169377d1" /> <br>


- Edit .json file and save
  ```
    [
    	{
    		"name": "Custom Endpoint",
    		"vendor": "customendpoint",
    		"apiKey": "${input:chat.lm.secret.41f2ad22}",
    		"apiType": "chat-completions",
    		"models": [
    			{
    				"id": "claude-haiku",
    				"name": "Claude Haiku 5.5 (LiteLLM)",
    				"url": "http://192.168.1.26:4000/v1/chat/completions",
    				"toolCalling": true,
    				"vision": true,
    				"maxInputTokens": 253952,
    				"maxOutputTokens": 16000
    			}
    		]
    	}
    ]
  ```
  <img width="1287" height="397" alt="image" src="https://github.com/user-attachments/assets/63587d3b-5271-41e5-8de9-52e3da0142d1" /><br>


<br>
<br>

## Select and setup LLM model
<img width="2558" height="1392" alt="image" src="https://github.com/user-attachments/assets/eed62880-5ac1-4522-963d-451b07df0f79" /><br>

<img width="3200" height="1542" alt="image" src="https://github.com/user-attachments/assets/b5a1c7c6-66c2-4ae4-b73d-414eb9e590e4" /><br>


<br>
<br>

## Start Vivado AI MCP tool
- Press ▶️ to start a new section
  <img width="3207" height="956" alt="image" src="https://github.com/user-attachments/assets/e1fd8c51-38a1-4f6d-a758-77e4ada35d5a" /><br>
- Select the Vivado execution file
  - `/opt/tools/amd/2025.2/Vivado/bin/vivado`
    <br><br>
    <img width="2560" height="506" alt="image" src="https://github.com/user-attachments/assets/59eab279-6a63-4f5a-a9d4-ca73e9f0884b" /> <br>
    <img width="2559" height="392" alt="image" src="https://github.com/user-attachments/assets/f8c2bad2-66ad-4892-aad3-81a2b4302596" /> <br>
    <img width="2560" height="290" alt="image" src="https://github.com/user-attachments/assets/9cedbc2a-046b-4a98-a0dd-50d564fdadaf" /> <br>
    <img width="2559" height="298" alt="image" src="https://github.com/user-attachments/assets/d3a3fee4-0732-4fc4-b369-0e44f957e6ae" /> <br>
    <img width="2559" height="321" alt="image" src="https://github.com/user-attachments/assets/33b4de3b-f730-4d4e-a94d-ba9dd1a004e7" /> <br>
    <img width="2559" height="315" alt="image" src="https://github.com/user-attachments/assets/0c94fec4-9a7c-47ff-94fe-fcc7769dab82" /> <br>

    


- Wait for new section start <br>
  <img width="241" height="316" alt="image" src="https://github.com/user-attachments/assets/292f0d32-55e3-4633-8fe7-1d6e741b277e" /><br>









