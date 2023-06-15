# Writer: An Extension for Text Generation Web UI
![Logo](./logo.png)

Writer is an open-source AI writing application specifically designed for novel writing, it aims to explore new options for creative writing with large language model support.

## Key Features :key:

- **Summary Support**: Write or paste a story summary in the summary section. This will provide necessary context to the LLM, assisting in generating content more aligned with the story background.

- **Auto-Summarisation of Chapters**: Instead of writing the story summary you can have the AI doing for you. Writer auto-summarises chapters, adding incremental context to your story. This can then be edited and tweaked.

- **Auto-Collation of Chapters**: Get your chapters organised automatically into a compiled story.

- **Export Options**: Export your finished story to HTML, Markdown, or txt format.

## Installation :cd:

Please follow these steps to install Writer:

1. Open a bash terminal in *text-generation-webui\extensions*
2. Type ``` git clone https://github.com/adunato/writer.git ```
3. Restart Text Generation Web UI

## How To Use :book:

### Writer Pad :memo:

The Writer Pad is the primary workspace. It functions similarly to the Notebook mode in Text Generation Web UI. Use this text box to write, edit, and generate text as per your needs. For best LLM generation, keep each paragraph under the LLM tokens limit (e.g. 2000), then hit "Process Paragraph" and start a new one with the context from the previous ones fed automatically to the LLM.

### Session :floppy_disk:

The Session feature allows you to save and load sessions, including content from the Writer Pad, Summary, and Compiled Story.

### Story Generation :rocket:

Here you can edit the story summary and get a view of the 'Latest Context' sent to the LLM. By viewing the context used by the LLM to generate text.

### Settings :gear:

Configure your text generation and summarisation settings. The summarisation function uses the model currently loaded. However, these settings are isolated from the text generation settings, allowing you to fine-tune them without interference.

## Roadmap :world_map:

I want this app to be a sandbox for AI-assisted writing and I plan to experiment with more ways to use LLM based tools:

- **Additional Context Tools**: Use of textual embeddings, vectors database and other injection techniques to provide additional ways to influence the LLM's context.

- **More Story Compilation Options and Formats**: Additional options for compiling your story, as well as supporting more export formats.

- **Chat with Your Story**: Chat with your story! Ask the LLM for advice on story development.

## Contribution :handshake:

Suggestions and bug reports are welcome! Feel free to create issues and submit pull requests.

## License :page_with_curl:

This project is licensed under the [MIT License](./LICENSE).

---

If any of the above sounds like a corporate sales pitch, blame Chat GPT for getting carried away with its "grammar checks".
