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
- [Best Practices](#best-practices)


## Agents

PokoScribe has the following agents that work together to automate the academic writing process.

### AI Agent Summarizer

Agent that summarizes academic papers, articles or even books with proper citation according to the user preferances. prompts and answers are stored in db with the citation of the paper, and the project that the paper is related to.

sources: [AI-Agent-Summarizer](docs/AI-Agent-Summarizer.md) documentation.

### AI Agent Outliner

AI agent that creates an outline for the paper, article, or essay based on the total summaries and citations of the specific project. Its purpose is to suggest the structure of the text after it reads the summaries and citations of the papers related to the project.

sources: [AI-Agent-Outliner](docs/AI-Agent-Outliner.md) documentation.

### AI Agent Chapter Creator

AI agent that generates chapters of the paper based on the outline. It reads the outline and generates chapters for the paper, article, or essay.

For more information please refer to the

## Best Practices

To ensure the system runs smoothly and efficiently, the following best practices should be followed:

📄 Secure that the folders and databases are properly setup via config and db folder files <br>
🔄 Regular database maintenance <br>
📊 Monitor API usage and token count <br>
📝 Check log files for errors <br>
📋 Maintain prompt templates and modify them accordingly <br>
💾 Regular backups of completed summaries <br>


