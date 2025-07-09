
import { tool } from "ai";
import { updateTopicCoursesDataSchema } from "./aitm.schema.ts";
import { updateTopicCourses, UpdateTopicCoursesData } from "..";

export default tool({
  description: `
  Update a topic
Update an existing discussion topic for the course or group.
    `,
  parameters: updateTopicCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateTopicCoursesData, "url"> ) => {
    try {
      const { data } = await updateTopicCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    