
import { tool } from "ai";
import { listDiscussionTopicsCoursesDataSchema } from "./aitm.schema.ts";
import { listDiscussionTopicsCourses, ListDiscussionTopicsCoursesData } from "..";

export default tool({
  description: `
  List discussion topics
Returns the paginated list of discussion topics for this course or group.
    `,
  parameters: listDiscussionTopicsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListDiscussionTopicsCoursesData, "url"> ) => {
    try {
      const { data } = await listDiscussionTopicsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    