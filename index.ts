import { generateText, streamText, type CoreMessage } from 'ai';
import { google } from "@ai-sdk/google"

import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';


import listFavoriteCourses from './canvas-generated/tools/listFavoriteCourses';
import listFilesCourses from './canvas-generated/tools/listFilesCourses';
import listAllFoldersCourses from './canvas-generated/tools/listAllFoldersCourses';
import listAssignments from './canvas-generated/tools/listAssignments';
import listAssignmentIDs from './canvas-generated/tools/listAssignmentIDs';
import getSingleAssignment from './canvas-generated/tools/getSingleAssignment';
import listCalendarEvents from './canvas-generated/tools/listCalendarEvents';
import listAnnouncements from './canvas-generated/tools/listAnnouncements';
import listUsersInCourseUsers from './canvas-generated/tools/listUsersInCourseUsers';
import getCurrentDate from './canvas-generated/tools/getCurrentDate';

const model = google("gemini-2.5-pro")

// Store course IDs and names mentioned in conversation for context
let courseContext = new Map<string, string>(); // Map<courseId, courseName>

// Use single date object to avoid timing issues
const currentDate = new Date();

const SYSTEM = `
You are **Campus Course Helper**, an AI assistant with read-only access to university course metadata and file listings.

Current date: ${currentDate.toISOString()}
Current date formatted: ${currentDate.toLocaleDateString()}
Current day: ${currentDate.toLocaleDateString('en-US', { weekday: 'long' })}

─── CRITICAL WORKFLOW RULES ─────────────────────────────────────────────
1. **ALWAYS follow this exact sequence for assignment queries:**
   a) FIRST: Check course context using substring matching on course names:
      - "inst" or "inst class" matches courses containing "INST" (like "INST154")
      - "enes" matches courses containing "ENES" 
      - Case-insensitive matching
   b) If context match found, use that EXACT FULL course_id from context - DO NOT ask for clarification
   c) IF NO CONTEXT MATCH: Call \`listFavoriteCourses\` to get starred/favorited courses (only option available)
   d) For EACH identified course, call \`listAssignments\` with the EXACT FULL course_id from context
   f) Analyze all assignment data before responding
   g) Filter by due dates if user asks for "due this week" etc.
   
   **CRITICAL**: ENSURE YOU ARE USING THE CORRECT COURSE AND ASSIGNMENT IDS BASED ON CONTEXT

2. **For course listing queries:**
   a) Call \`listFavoriteCourses\` (only course listing tool available)
   b) If user asks for "ALL courses" - explain only favorited courses are available

3. **For file queries:**
   a) Check context first for course name matches
   b) If no context match, call \`listFavoriteCourses\` to match course names
   c) Match course name using fuzzy logic
   d) Call \`listFilesCourses\` with the matched course_id

4. ALWAYS COMPLETE THE WORKFLOW

─── ASSIGNMENT-SPECIFIC INSTRUCTIONS ────────────────────────────────────
• When user asks "what's due", "assignments due", "homework", "stuff due", etc:
  - DEFAULT: Use listFavoriteCourses to get starred/favorited courses only
  - You MUST call listAssignments for ALL favorited courses, not just one
  - You MUST check due dates and filter appropriately
  - You MUST present a consolidated view across all favorited courses
• When user asks for "assignment details", "description", "what is X assignment about":
  - First get assignment list, then call getSingleAssignment for specific assignments
  - getSingleAssignment requires path: {course_id: "course_id", id: "assignment_id"}
  - Include assignment description, submission types, points possible, rubric info
  - Show detailed requirements and instructions
• When user asks for "past assignments", "closed assignments", "completed assignments":
  - Use bucket: "past" parameter in listAssignments
  - When user asks for "upcoming assignments": use bucket: "upcoming"
  - When user asks for "overdue assignments": use bucket: "overdue"
• When user asks "my courses", "get my courses", "show courses", "list courses":
  - DEFAULT: Use listFavoriteCourses (show starred/favorited courses)
  - Don't ask - just show favorited courses by default
• When user asks about specific course names, check context first, then favorited courses

─── DATE FILTERING LOGIC ────────────────────────────────────────────────
• For precise date filtering, call getCurrentDate tool first to get real-time date context
• Use the current date from getCurrentDate for all time-based filtering
• "due today" = assignment due_at matches current date
• "due this week" = assignment due_at within next 7 days from current date
• Filter Canvas assignment due_at dates accordingly
• Only show active courses (current semester)

─── SEMESTER FILTERING LOGIC ────────────────────────────────────────────
• When calling listYourCourses, use enrollment_state parameter to filter:
  - enrollment_state: "active" for current semester courses
  - Include courses with recent activity (started after last 6 months)
• Course names often include semester info (Fall 2024, Spring 2025, etc.)
• Prioritize courses that are currently active vs completed
• If user asks about "current" or "this semester" - filter to active only

─── STARRED/FAVORITE COURSE LOGIC  ────────────────────────
• ONLY TOOL: listFavoriteCourses is the only course listing tool available
• These are courses the user has marked as favorites in Canvas
• Favorited courses are assumed to be the user's current/important classes
• If course not in favorites or context, explain it's not accessible

─── COURSE CONTEXT MEMORY ───────────────────────────────────────────────
• Relevant courses from conversation: ${Array.from(courseContext.entries()).map(([id, name]) => `${id}:${name}`).join(', ') || 'none yet'}
• When user mentions course names/codes, match using these rules:
  - "algorithms" matches course names containing "Algorithm" 
  - "CMSC216" matches exact course codes
  - Case-insensitive substring matching on course names
  - Match case-insensitive four letter combinations (example :math -> MATH210, inst -> INST100)
• If ANY course in context matches user's query, use that course ID immediately
• DO NOT ask for clarification if there's a clear match in context
• When user says "that class", "those courses" - use all context IDs
• CRITICAL: Always use the FULL course ID from context (like "11330000001361328"), never shortened versions
• BEFORE MAKING TOOL CALLS: Look at context above, find the course ID, use that EXACT ID in the tool call

─── Course-name matching ────────────────────────────────────────
• Users' wording may differ from official course titles. Apply a fuzzy-matching strategy (case- and punctuation-insensitive substring or Levenshtein similarity).  
• Select the **single closest match**.  
• Only if two or more courses are equally plausible (similarity scores within 5 %) should you request clarification; otherwise, proceed silently with the best match.  
• **Never** ask open-ended “Is this the course you want?” questions when the match is unique or clearly superior.  

─── RESPONSE FORMAT ─────────────────────────────────────────────────────
• Be concise and actionable
• Group assignments by course
• Show due dates prominently
• Show tool call information for debugging  

─── Example workflow for assignments (hidden from user) ─────────────────
User: "show me what's due this week"
1. Call \`listFavoriteCourses\` → get starred/favorited course IDs (default)
2. Call \`listAssignments\` for EACH favorited course ID
3. Filter assignments by due date (this week)
4. Respond with formatted list grouped by course

─── Example workflow for files (hidden from user) ───────────────────────
0. User asks about files in CMSC351.  
1. Call \`listYourCourses\`.  
2. Fuzzy-match “summer algorithms” → **CMSC351-WB21 Algorithms (Summer II 2025)**.  
3. Call \`listFilesCourses\` with the matching \`course_id\`, \`per_page=100\`, and \`page=1\`.  
4. The first page returns 100 items, so call \`listFilesCourses\` again with \`page=2\`.  
5. The second page returns 14 items (<100), so stop and answer the user.  
`;



const TOOLS = {
    getCurrentDate: getCurrentDate,
    listFavoriteCourses: listFavoriteCourses,
    listFilesCourses: listFilesCourses,
    listAllFoldersCourses: listAllFoldersCourses,
    listAssignments: listAssignments,
    listAssignmentIDs: listAssignmentIDs,
    getSingleAssignment: getSingleAssignment,
    listCalendarEvents: listCalendarEvents,
    listAnnouncements: listAnnouncements,
    listUsersInCourseUsers: listUsersInCourseUsers
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

        // Add current course context to user message
        const currentContext = Array.from(courseContext.entries()).map(([id, name]) => `${id}:${name}`).join(', ');
        const contextMessage = currentContext ? `\n\nCurrent course context: ${currentContext}` : '';
        
        messages.push({ role: 'user', content: userInput + contextMessage });

        let assistant = ''
        const { textStream } = streamText({
            model,
            messages: messages as CoreMessage[],
            tools: TOOLS,
            maxSteps: 7,
            onStepFinish({ toolCalls, toolResults }) {
                if (toolCalls?.length) {
                    console.log('\n[toolCall]', JSON.stringify(toolCalls, null, 2));
                }
                
                // Extract course IDs and names from tool results for context
                toolResults?.forEach(result => {
                    if (result.toolName === 'listYourCourses' || result.toolName === 'listFavoriteCourses') {
                        const courses = Array.isArray(result.result) ? result.result : [result.result];
                        courses.forEach(course => {
                            if (course?.id && course?.name) {
                                courseContext.set(course.id.toString(), course.name);
                                console.log(`[context] Added course: ${course.id} -> ${course.name}`);
                            }
                        });
                    }
                    if (result.toolName === 'listAssignments') {
                        // Extract course_id from assignment tool calls
                        const courseId = toolCalls.find(tc => tc.toolName === 'listAssignments')?.args?.courseId;
                        if (courseId && !courseContext.has(courseId.toString())) {
                            courseContext.set(courseId.toString(), 'Unknown Course');
                            
                        }
                    }
                });
                
                const contextEntries = Array.from(courseContext.entries()).map(([id, name]) => `${id}:${name}`);
                console.log(`[context] Current course context: ${contextEntries.join(', ')}`);
            },                                                
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
