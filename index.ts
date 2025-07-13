import { streamText, type CoreMessage, tool } from 'ai';
import { google } from "@ai-sdk/google"
import { z } from 'zod';

import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { SYSTEM } from "./system"


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
import { exportToMD } from './export';

const model = google("gemini-2.5-pro")

let courseContext = new Map<string, string>(); // Map<courseId, courseName>
let assignmentCache = new Map<string, {courseId: string, name: string}>(); // Map<assignmentId, {courseId, name}>




const getCourseContext = tool({
    description: 'Returns known course IDs/names and recently seen assignment IDs/names. For full assignment details, use getSingleAssignment.',
    parameters: z.object({}),
    execute: async () => {
        return {
            courses: Array.from(courseContext.entries()).map(([id, name]) => ({ id, name })),
            assignments: Array.from(assignmentCache.entries()).map(([assignmentId, data]) => ({
                assignmentId,
                courseId: data.courseId,
                name: data.name
            }))
        };
    }
});




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
    listUsersInCourseUsers: listUsersInCourseUsers,
    getCourseContext: getCourseContext
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

        if (userInput.toLowerCase() === 'context') {
            const contextEntries = Array.from(courseContext.entries()).map(([id, name]) => `${id}:${name}`);
            console.log(`Current course context: ${contextEntries.join(', ')}`);
            continue;
        }

        if (userInput.toLowerCase() === 'clear_context') {
            courseContext.clear();
            assignmentCache.clear();
            console.log('Course context and assignment cache cleared.');
            continue;
        }

        if (userInput.toLowerCase() === 'export_conv') {
            exportToMD(messages);
        }
        // // Add current course context to user message
        // const currentContext = Array.from(courseContext.entries()).map(([id, name]) => `${id}:${name}`).join(', ');
        // const contextMessage = currentContext ? `\n\nCurrent course context: ${currentContext}` : '';

        messages.push({ role: 'user', content: userInput });

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

                toolResults?.forEach(result => {
                    if (result.toolName === 'listFavoriteCourses') {
                        // Since listFavouriteCourses return information about the courses we can use later, it is best to cache it 
                        const courses = Array.isArray(result.result) ? result.result : [result.result];
                        courses.forEach(course => {
                            if (typeof course === 'object' && course !== null && 'id' in course && course.id && course.name) {
                                courseContext.set(course.id.toString(), course.name);
                            }
                        });
                    }
                    if (result.toolName === 'listAssignments') {
                        const courseId = toolCalls.find(tc => tc.toolName === 'listAssignments')?.args?.path?.course_id;
                        if (courseId && !courseContext.has(courseId.toString())) {
                            courseContext.set(courseId.toString(), 'Unknown Course');
                        }
                        // Cache assignment IDs and names
                        const assignments = Array.isArray(result.result) ? result.result : [result.result];
                        assignments.forEach(assignment => {
                            if (typeof assignment === 'object' && assignment !== null && 'id' in assignment && assignment.id && assignment.name) {
                                assignmentCache.set(assignment.id.toString(), {
                                    courseId: courseId.toString(),
                                    name: assignment.name
                                });
                            }
                        });
                    }
                    if (result.toolName === 'getSingleAssignment') {
                        const courseId = toolCalls.find(tc => tc.toolName === 'getSingleAssignment')?.args?.path?.course_id;
                        const assignment = result.result;
                        if (courseId && assignment && typeof assignment === 'object' && 'id' in assignment && assignment.id && assignment.name) {
                            assignmentCache.set(assignment.id.toString(), {
                                courseId: courseId.toString(),
                                name: assignment.name
                            });
                        }
                    }
                });

                // const contextEntries = Array.from(courseContext.entries()).map(([id, name]) => `${id}:${name}`);
            },
        });

        for await (const res of textStream) {
            assistant += res;
            process.stdout.write(res);
        }
        console.log();
        messages.push({ role: 'assistant', content: assistant });

    }
    rl.close();
}


main().catch(console.error); 
