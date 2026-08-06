# RFP Assistant User Note

## What This Software Does

RFP Assistant helps users draft RFP responses from company knowledge documents and previously approved answers. Users can upload RFP questions, generate draft answers, review source references, edit responses, and export the final response as a Word document.

The assistant uses:

- Local knowledge files from `data/documents`
- A searchable document index built during ingestion
- Saved approved answers from memory
- A local Ollama model for answer generation

## How To Open The Software

1. Start the app by running:

   ```bat
   run_app.bat
   ```

2. Open the local app:

   ```text
   http://localhost:8001
   ```

3. If remote access is enabled, open the ngrok tunnel URL:

   ```text
   https://gamma-landmass-quadrant.ngrok-free.dev
   ```

4. Log in with the configured username and password.

## How To Start The Front-End Tutorial

1. Open the RFP Assistant in the browser.
2. Look at the top-right header area.
3. Click the **Tutorial** button.
4. A guided walkthrough will open on top of the app.
5. Use **Next** to move through the tutorial.
6. Use **Back** to return to the previous step.
7. Use **Close** or press `Esc` to exit the tutorial.

The tutorial highlights the main controls one by one and explains what each part of the front end does.

## What The Tutorial Teaches

The built-in tutorial explains these steps:

1. **Knowledge Sources**
   The left panel is where users manage source files, question templates, and detection settings.

2. **Upload Source Documents**
   Users can upload supported files such as `.docx`, `.pdf`, `.pptx`, `.xlsx`, `.txt`, or `.md`.

3. **Re-Ingest Knowledge Docs**
   After adding new documents, users click **Re-ingest Knowledge Docs** so the assistant can search the latest content.

4. **Load A Question Template**
   Users can upload a Word or Excel RFP template. The app detects questions and adds them to the review area.

5. **Apply Detection Settings**
   Users can choose how the app should detect questions and where answers should be placed.

6. **Add One Question**
   Users can manually enter a single RFP question.

7. **Add A Question List**
   Users can paste multiple questions, one per line.

8. **Generate Answers**
   The assistant searches documents and saved memory, then generates draft answers.

9. **Review And Edit**
   Users review generated answers, check references, and make edits before export.

10. **Export DOCX**
    Users generate a Word response document from the reviewed answers.

## Recommended User Workflow

1. Add or upload the latest source documents.
2. Click **Re-ingest Knowledge Docs**.
3. Load an RFP question template or manually add questions.
4. Review the detected questions.
5. Click **Generate Answers**.
6. Review references and edit the answers.
7. Export the completed response as a DOCX file.

## Important Notes

- Re-ingest documents every time new files are added.
- Keep Ollama running while generating answers.
- Review every generated answer before sending it to a client.
- Use saved memory only for approved, reusable answers.
- Do not share the remote tunnel publicly unless login protection is enabled.
