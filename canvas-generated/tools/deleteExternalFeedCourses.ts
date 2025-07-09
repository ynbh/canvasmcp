
import { tool } from "ai";
import { deleteExternalFeedCoursesDataSchema } from "./aitm.schema.ts";
import { deleteExternalFeedCourses, DeleteExternalFeedCoursesData } from "..";

export default tool({
  description: `
  Delete an external feed
Deletes the external feed.
    `,
  parameters: deleteExternalFeedCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteExternalFeedCoursesData, "url"> ) => {
    try {
      const { data } = await deleteExternalFeedCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    