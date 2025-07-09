import { z } from 'zod';
import { generateText, tool } from 'ai';

import { google } from "@ai-sdk/google"


import listYourCourses from './canvas/tools/listYourCourses';
import listUsersInCourseUsers from "./canvas/tools/listUsersInCourseUsers";
import listFavoriteCourses from './canvas/tools/listFavoriteCourses';
import listFilesCourses from './canvas/tools/listFilesCourses';
import listAllFoldersCourses from './canvas/tools/listAllFoldersCourses';

const model = google("gemini-2.5-pro")

const currentYearTool = tool({
    description: 'Get the current year',
    parameters: z.object({}),
    execute: async () => {
        const date = new Date();
        const year = date.getFullYear();
        return { year };
    },
}); 



const result = async ({ prompt }: { prompt?: string }) => {
    return await generateText({
        model: model,
        tools: {
            listCourseDetails: listYourCourses,
            listFavoriteCourses: listFavoriteCourses,
            listFilesCourses: listFilesCourses,
            listAllFoldersCourses: listAllFoldersCourses,
        },
        prompt: "What folders and files exist in the course CMSC330?",
        // toolChoice: "required",
        system: `You are a helpful assistant that can answer questions about courses and files in a university setting. 
        You can use the tools provided to get information about courses, favorite courses, and files in courses.
        All tools except listCourseDetails require a course ID to be passed in. Therefore, always call the tool listCourseDetails first to gather course IDs.
        Note: Course names provided by the user may not match the course names in the system. Find the closest match to the course name provided by the user, and use that closest match as the source of truth for the course ID.`,
        maxSteps: 7,

    })
};

const { text, toolCalls, toolResults } = await result({ prompt: "What courses am I enrolled in?" })

console.log({ text, toolCalls, toolResults })
// console.log(toolResults[0].result)
