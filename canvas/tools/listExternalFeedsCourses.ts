
import { tool } from "ai";
import { listExternalFeedsCoursesDataSchema } from "./aitm.schema.ts";
import { listExternalFeedsCourses, ListExternalFeedsCoursesData } from "..";

export default tool({
  description: `
  List external feeds
Returns the paginated list of External Feeds this course or group.
    `,
  parameters: listExternalFeedsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListExternalFeedsCoursesData, "url"> ) => {
    try {
      const { data } = await listExternalFeedsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    