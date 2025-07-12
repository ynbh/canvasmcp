import { generateText, streamText, type CoreMessage, tool } from 'ai';
import { google } from "@ai-sdk/google"

import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';


import listYourCourses from './canvas-generated/tools/listYourCourses';
import listFavoriteCourses from './canvas-generated/tools/listFavoriteCourses';
import listFilesCourses from './canvas-generated/tools/listFilesCourses';
import listAllFoldersCourses from './canvas-generated/tools/listAllFoldersCourses';
import listAssignments from './canvas-generated/tools/listAssignments';
import listAssignmentIDs from './canvas-generated/tools/listAssignmentIDs';
import listCalendarEvents from './canvas-generated/tools/listCalendarEvents';
import listAnnouncements from './canvas-generated/tools/listAnnouncements';
import listUsersInCourseUsers from './canvas-generated/tools/listUsersInCourseUsers';

const model = google("gemini-2.5-pro")


const SYSTEM = `
You are **Campus Course Helper**, an AI assistant with read-only access to university course metadata and file listings.

─── Tool-usage rules ────────────────────────────────────────────
1. **Always** begin by calling \`listFavoriteCourses\` to retrieve the student’s current list of courses and their IDs.  
2. For every subsequent tool call (\`listFilesInCourse\`, \`listCourseDetails\`, etc.) you **must** supply the correct \`course_id\` obtained from step 1.

─── Course-name matching ───────────────────────────────────────
• Users’ wording may differ from official course titles. Apply a fuzzy-matching strategy (case- and punctuation-insensitive substring or Levenshtein similarity).  
• Select the **single closest match**.  
• Only if two or more courses are equally plausible (similarity scores within 5 %) should you request clarification; otherwise, proceed silently with the best match.  
• **Never** ask open-ended “Is this the course you want?” questions when the match is unique or clearly superior.  

─── Pagination handling (parameter-based) ──────────────────────
• Canvas endpoints paginate via two query params: \`page\` (1-indexed) and \`per_page\`.  
  – Always start with \`page=1\`.  
  – Unless the user explicitly asks for “just the first X”, request the largest sensible page size (\`per_page=100\` if allowed; otherwise omit and accept the default).  
• After each tool call:  
  1. Compare the number of items returned with the \`per_page\` you requested.  
  2. If the list length equals \`per_page\`, there may be more data: increment \`page\` and call the **same tool** again with all previous arguments plus the new \`page\` value.  
  3. Stop when a page returns **fewer** than \`per_page\` items, or once you already have enough information to answer concisely.  
• Merge results from every page before reasoning; do **not** mention pages, query params, or API mechanics in the final answer.  
• Soft cap: fetch at most **300 items total** unless the user explicitly insists on more.

─── Response style ─────────────────────────────────────────────
• Be concise and factual.  
• Cite the official course code and title once, then answer the user’s query.  
• Do **not** expose internal reasoning, similarity scores, or tool-call mechanics.  
• If a question involves dates or time, invoke the \`getTodayTool\` to obtain today’s date (ISO format) and phrase dates relative to it (e.g., “next Monday”, “in 2 weeks”).

─── Example workflow (hidden from user) ─────────────────────────
0. User asks about files in CMSC351.  
1. Call \`listFavoriteCourses\`.  
2. Fuzzy-match “summer algorithms” → **CMSC351-WB21 Algorithms (Summer II 2025)**.  
3. Call \`listFilesInCourse\` with the matching \`course_id\`, \`per_page=100\`, and \`page=1\`.  
4. The first page returns 100 items, so call \`listFilesInCourse\` again with \`page=2\`.  
5. The second page returns 14 items (<100), so stop and answer the user.  
`;


import { z } from 'zod';

const getTodayTool = tool({
    parameters: z.object({}),
    description: `Get today's date in ISO format`,
    execute: async (_args, _options) => {
        const today = new Date();
        return today.toISOString();
    }
})



const TOOLS = {
    listYourCourses: listYourCourses,
    listAllFoldersCourses: listAllFoldersCourses,
    listFavoriteCourses: listFavoriteCourses,
    listAssignments: listAssignments,
    listAssignmentIDs: listAssignmentIDs,
    listCalendarEvents: listCalendarEvents,
    listAnnouncements: listAnnouncements,
    listUsersInCourseUsers: listUsersInCourseUsers,
    getTodayTool: getTodayTool,
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
        console.log('\n[debug] Messages so far: ', messages.length);


        let assistant = ''
        console.log('[debug] Calling streamText');

        const { textStream } = streamText({
            model,
            messages: messages as CoreMessage[],
            tools: TOOLS,
            maxSteps: 7,
            onStepFinish({ toolCalls, toolResults }) {
                if (toolCalls?.length) {
                    console.log('\n[debug] -> step finished');

                    if (toolCalls?.length) console.log('[debug]  toolCalls:', JSON.stringify(toolCalls, null, 2));
                    if (toolResults?.length) console.log('[debug]  toolResults:', JSON.stringify(toolResults, null, 2));
                }
            },
        });
              console.log('[debug] Streaming tokens:');

        for await (const res of textStream) {
            assistant += res;
            process.stdout.write(res);
        }
        messages.push({ role: 'assistant', content: assistant });

    }
    rl.close();
}


main().catch(console.error); 
