import { generateText, streamText, type CoreMessage } from 'ai';
import { google } from "@ai-sdk/google"

import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';


import listYourCourses from './canvas-generated/tools/listYourCourses';
import listFavoriteCourses from './canvas-generated/tools/listFavoriteCourses';
import listFilesCourses from './canvas-generated/tools/listFilesCourses';
import listAllFoldersCourses from './canvas-generated/tools/listAllFoldersCourses';
import listAssignments from './canvas-generated/tools/listAssignments';
import listAssignmentIDs from './canvas-generated/tools/listAssignmentIDs';

const model = google("gemini-2.5-pro")


const SYSTEM = `
You are **Campus Course Helper**, an AI assistant with read-only access to university course metadata and file listings.

─── Tool-usage rules ─────────────────────────────────────────────
1. **Always** begin by calling \`listCourseDetails\` to retrieve the full list of courses and their IDs.
2. For every subsequent tool call (\`listFilesInCourse\`, \`listFavoriteCourses\`, etc.) you **must** supply the correct \`course_id\` obtained from step 1.

─── Course-name matching ────────────────────────────────────────
• Users' wording may differ from official course titles. Apply a fuzzy-matching strategy (case- and punctuation-insensitive substring or Levenshtein similarity).  
• Select the **single closest match**.  
• Only if two or more courses are equally plausible (similarity scores within 5 %) should you request clarification; otherwise, proceed silently with the best match.  
• **Never** ask open-ended “Is this the course you want?” questions when the match is unique or clearly superior.  

─── Response style ───────────────────────────────────────────────
• Be concise and factual.  
• Cite the official course code and title once, then answer the user's query.  
• Do **not** expose internal reasoning, similarity scores, or tool-call mechanics.  

─── Example workflow (hidden from user) ──────────────────────────
0. User asks about files in CMSC351.
1. Call \`listCourseDetails\`.  
2. Fuzzy-match “summer algorithms” → **CMSC351-WB21 Algorithms (Summer II 2025)**.  
3. Call \`listFilesInCourse\` with the matching \`course_id\`.  
`;

const TOOLS = {
    listYourCourses: listYourCourses,
    listFavoriteCourses: listFavoriteCourses,
    listFilesCourses: listFilesCourses,
    listAllFoldersCourses: listAllFoldersCourses,
    listAssignments: listAssignments,
    listAssignmentIDs: listAssignmentIDs,
}

async function main() {
    const rl = readline.createInterface({ input, output });

    const messages = [{ role: 'system', content: SYSTEM }]


    while (true) {
        const userInput = await rl.question('You: ');

        if (userInput.toLowerCase() === 'exit') {
            console.log('Exiting...');
            break;
        }

        messages.push({ role: 'user', content: userInput });

        let assistant = ''
        const { textStream } = streamText({
            model,
            messages: messages as CoreMessage[],
            tools: TOOLS,
            maxSteps: 7,
            onStepFinish({ toolCalls, toolResults }) {
                if (toolCalls?.length) {
                    console.log('\n[toolCall]');
                }
            },                                                   // :contentReference[oaicite:1]{index=1}
        });

        for await (const res of textStream) {
            assistant += res;
            process.stdout.write(res);
        }
        messages.push({ role: 'assistant', content: assistant });

    }
    rl.close();
}


main().catch(console.error); 

// const result = async ({ prompt }: { prompt?: string }) => {
//     return await generateText({
//         model: model,
//         tools: TOOLS,
//         prompt: "What assignments do I have in CMSC330?",
//         system: SYSTEM,
//         maxSteps: 7,

//     })
// };

// const { text, toolCalls, toolResults } = await result({ prompt: "What courses am I enrolled in?" })

// console.log({ text, toolCalls, toolResults })
// console.log(toolResults[0].result)
