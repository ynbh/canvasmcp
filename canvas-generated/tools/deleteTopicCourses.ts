
import { tool } from "ai";
import { deleteTopicCoursesDataSchema } from "./aitm.schema.ts";
import { deleteTopicCourses, DeleteTopicCoursesData } from "..";

export default tool({
  description: `
  Delete a topic
Deletes the discussion topic. This will also delete the assignment, if it's
an
assignment discussion.
    `,
  parameters: deleteTopicCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteTopicCoursesData, "url"> ) => {
    try {
      const { data } = await deleteTopicCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    