
import { tool } from "ai";
import { createNewDiscussionTopicCoursesDataSchema } from "./aitm.schema.ts";
import { createNewDiscussionTopicCourses, CreateNewDiscussionTopicCoursesData } from "..";

export default tool({
  description: `
  Create a new discussion topic
Create an new discussion topic for the course or group.
    `,
  parameters: createNewDiscussionTopicCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateNewDiscussionTopicCoursesData, "url"> ) => {
    try {
      const { data } = await createNewDiscussionTopicCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    