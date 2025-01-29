<h1 align="center" style="font-size: 3em;">PokoScribe</h1>

<p align="center">
  <img src="images/logo.webp" alt="PokoScribe Logo" width="200">
</p>

## Overview

PokoScribe is a Multi-Agent System (MAS) that combines summarization, citation, paper outlining, and chapter creation for automation of academic writing.

The system has agents that work together to speed up academic writing tasks or can be used individually for specific tasks if the data are provided in the correct format.

Prompts and answers of the system are stored using PostgreSQL database.

Disclaimer: PokoScribe is not a replacement for human writers and under no cirumstances should the output of the system be used as the final version of the paper. The system is designed to help writers to write faster and more efficiently automating some of the tasks in the writing process and only if the data are gathered with rationality and have been prepared in the correct format.


## Table of Contents

- [Overview](#overview)
- [Table of Contents](#table-of-contents)
- [Agents](#agents)
  - [AI Agent Summarizer](#ai-agent-summarizer)
  - [AI Agent Outliner](#ai-agent-outliner)
  - [AI Agent Chapter Creator](#ai-agent-chapter-creator)

- [Tools](#tools)
  - [AHSS](#ahss)
  - [Sci-Hub](#sci-hub)
  - [TokenCounter](#tokencounter)
- [Best Practices](#best-practices)


## Agents

PokoScribe has agents that work together to automate the academic writing process.The agents make API calls to various services of popular AI chatbots to process data that have been gathered. The agents are designed to work together and the goal is to automate the process so the output of one agent can be used as the input of another agent. For this the configuration file and the correct prompt engineering are crucial for the system to work more efficiently.

### AI Agent Summarizer

Agent that summarizes academic papers, articles or even books with proper citation according to the user preferances. prompts and answers are stored in db with the citation of the paper, and the project that the paper is related to.

sources: [AI-Agent-Summarizer](docs/AI-Agent-Summarizer.md) documentation.

### AI Agent Outliner

AI agent that creates an outline for the paper, article, or essay based on the total summaries and citations of the specific project. Its purpose is to suggest the structure of the text after it reads the summaries and citations of the papers related to the project.

sources: [AI-Agent-Outliner](docs/AI-Agent-Outliner.md) documentation.


### AI Agent Chapter Creator

AI agent that generates chapters of the paper based on the outline. The chapter that generated are passed to the agent and creates them based on the summaries it reads

sources: [AI-Agent-ChapterMaker](docs/AI-Agent-ChapterMaker.md) documentation.

## Tools

The system has tools that are used to gather data and process them for the agents to work efficiently.

### AHSS
AHSS (Academic Hyper Search System) is a tool that is used to gather academic papers from the web. It uses platforms to gather metadata and store them in the database for later use.

sources: [AHSS](docs/Tools-AHSS.md) documentation.

### SciHub-dler

Sci-Hub-dler is a tool that is used to download academic papers from Sci-Hub. It uses the DOI of the paper to download the paper in pdf format.

sources: [SciHub-dler](docs/Tools-SciHub-dler.md) documentation.

### TokenCounter

TokenCounter is a tool that is used to count the tokens of the text. It is used to count the tokens of the summaries and the citations of the papers that are used in the system. It is called by the agents to count the tokens of the text in order to create batches and handle the text more efficiently.

sources: [TokenCounter](docs/Tools-TokenCounter.md) documentation.

## Best Practices

To ensure the system runs smoothly and efficiently, the following best practices should be followed:

🔑 Keep API keys secure and do not share them <br>
📄 Secure that the folders and databases are properly setup via config and db folder files <br>
🔄 Regular database maintenance <br>
📊 Monitor API usage and token count <br>
📝 Check log files for errors <br>
📋 Maintain prompt templates and modify them accordingly <br>
💾 Regular backups of completed summaries <br>
📁 Organize files in the data folder <br
🔍 Check the database for any inconsistencies <br
📈 Monitor the system performance <br
🔒 Secure the system with proper authentication <br>
📚 Keep the system up-to-date with the latest libraries and dependencies <br>
📧 Regularly check the email for any notifications <br>
📅 Schedule tasks for regular maintenance <br>
📜 Keep the documentation up-to-date <br>
📌 Follow the best practices for coding and documentation <br>
📦 Keep the system modular and scalable <br>
🔧 Regularly check the system for any bugs or issues <br>
📡 Monitor the system for any security vulnerabilities <br>
🔗 Regularly check the links in the system <br> 
📑 Keep the system clean and organized <br>
📤 Regularly check the system for any outdated or unused files <br>



