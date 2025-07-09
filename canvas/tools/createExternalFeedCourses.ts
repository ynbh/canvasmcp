
import { tool } from "ai";
import { createExternalFeedCoursesDataSchema } from "./aitm.schema.ts";
import { createExternalFeedCourses, CreateExternalFeedCoursesData } from "..";

export default tool({
  description: `
  Create an external feed
Create a new external feed for the course or group.
    `,
  parameters: createExternalFeedCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateExternalFeedCoursesData, "url"> ) => {
    try {
      const { data } = await createExternalFeedCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    